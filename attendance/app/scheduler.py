# app/scheduler.py
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .utils.oss import OSSManager
from .utils.database import db
from sqlalchemy import and_, or_, not_, exists
from sqlalchemy.orm import aliased
from .models import Attendance, Student, Course
import pandas as pd
import logging
from datetime import datetime, timedelta, time
from config import Config  # 确保正确导入配置

logger = logging.getLogger('SCHEDULER')


def init_scheduler(app):
    # 调试模式下仅在主进程初始化
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' and app.debug:
        logger.warning("调试模式下跳过子进程的调度器初始化")
        return
    # 单例检查
    if hasattr(app, 'scheduler'):
        logger.warning("调度器已存在，跳过重复初始化")
        return
    scheduler = BackgroundScheduler(daemon=True)
    # 添加任务前清空旧任务
    scheduler.remove_all_jobs()

    # 添加两个定时任务
    scheduler.add_job(
        id='update_attendance_status',
        func=update_attendance_status,
        trigger=CronTrigger(hour=21, minute=2),  # 21点更新状态
        args=[app]
    )

    scheduler.add_job(
        id='daily_report',
        func=generate_and_upload_report,
        trigger=CronTrigger(hour=22, minute=00),  # 每天22点执行
        args=[app]  # 传递app上下文
    )

    # 启动前检查
    scheduler.start()
    app.scheduler = scheduler  # 将调度器挂载到app对象
    logger.info("定时调度器已启动，任务列表：%s", scheduler.get_jobs())


# 新增任务：更新考勤状态
def update_attendance_status(app):
    with app.app_context():
        try:
            today = datetime.now().date()
            logger.info(f"开始处理【{today}】考勤状态...")
            # （使用更精确的NOT EXISTS）
            absent_students = db.session.query(Student).filter(
                ~exists().where(
                    (Attendance.student_id == Student.student_id) &
                    (Attendance.date == today)
                )
            ).all()

            # 批量生成缺勤记录
            if absent_students:
                absent_records = [{
                    'student_id': s.student_id,
                    'course_id': s.course_id,
                    'date': today,
                    'status': 'Absent'
                } for s in absent_students]

                db.session.bulk_insert_mappings(Attendance, absent_records)
                logger.info(f"新增{len(absent_students)}条缺勤记录")

            # 步骤2：更新现有记录的Anomaly状态
            # 查询需要更新的记录
            # update_query = db.session.query(Attendance).filter(
            #     Attendance.date == today,
            #     or_(
            #         Attendance.status == 'Absent',  # 新插入的记录
            #         and_(
            #             Attendance.check_in.isnot(None),
            #             Attendance.check_out.is_(None)
            #         ),
            #         and_(
            #             Attendance.check_in.is_(None),
            #             Attendance.check_out.isnot(None)
            #         )
            #     )
            # )
            #
            # update_count = 0
            # for record in update_query:
            #     original_status = record.status
            #     # 重新计算状态
            #     new_status = calculate_status(record)
            #
            #     if new_status != original_status:
            #         record.status = new_status
            #         update_count += 1

            # 提交事务
            db.session.commit()
            # logger.info(f"状态处理完成，新增{len(absent_students)}条缺勤，更新{update_count}条记录")

        except Exception as e:
            db.session.rollback()
            logger.error(f"考勤处理失败: {str(e)}", exc_info=True)
            raise
        finally:
            db.session.close()


def calculate_status(record):
    """根据时间计算状态"""
    # 直接从配置读取固定课程时间
    course_start = datetime.combine(record.date, Config.COURSE_START_TIME)  # 合并日期与配置中的时间
    course_end = datetime.combine(record.date, Config.COURSE_END_TIME)

    # 未签到
    if not record.check_in and not record.check_out:
        return 'Absent'

    if not record.check_in and record.check_out:
        return 'Anomaly'

    # 签到了但未签退
    if not record.check_out:
        return 'Anomaly'

    if is_late(record.check_in, course_start) and not is_quit(record.check_out, course_end):
        return 'Late'
    elif is_late(record.check_in, course_start) and is_quit(record.check_out, course_end):
        return 'Late + Early'
    elif not is_late(record.check_in, course_start) and is_quit(record.check_out, course_end):
        return 'Early'
    else:
        return 'Normal'


def is_late(check_in_time, course_start):
    """判断是否Late（超过15分钟）"""
    return (datetime.combine(course_start.date(), check_in_time) - course_start).total_seconds() > 900

def is_quit(check_out_time, course_end):
    """判断是否Early（提前15分钟签退）"""
    return (course_end - datetime.combine(course_end.date(), check_out_time)).total_seconds() > 900

def generate_and_upload_report(app):
    with app.app_context():  # 确保在应用上下文中运行
        try:
            today = datetime.now().date()
            logger.info(f"开始生成【{today}】考勤报告...")

            # 数据库查询
            query = db.session.query(
                Student.student_id,
                Student.name,
                Course.course_name,
                Attendance.check_in,
                Attendance.check_out,
                Attendance.status
            ).join(  # 添加显式JOIN
                Student,
                Student.student_id == Attendance.student_id
            ).join(
                Course,
                Student.course_id == Course.course_id  # 确保学生所属课程一致
            ).filter(
                Attendance.date == today
            )

            df = pd.read_sql(query.statement, db.engine)

            # 生成临时文件
            filename = f"attendance_{today.strftime('%Y%m%d')}.xlsx"
            df.to_excel(filename, index=False)
            logger.info(f"Excel文件已生成：{filename}")

            # 上传OSS
            oss = OSSManager()
            if oss.upload_file(filename):
                logger.info("文件上传OSS成功")
            else:
                logger.error("文件上传失败")

        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}", exc_info=True)
        finally:
            db.session.close()
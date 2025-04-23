# app/utils/oss.py
import oss2
from flask import current_app
from datetime import datetime
import logging

logger = logging.getLogger('OSS')


class OSSManager:
    def __init__(self):
        self._init_oss_client()

    def _init_oss_client(self):
        """初始化OSS客户端"""
        try:
            self.auth = oss2.Auth(
                current_app.config['OSS_ACCESS_KEY_ID'],
                current_app.config['OSS_ACCESS_KEY_SECRET']
            )
            self.bucket = oss2.Bucket(
                self.auth,
                current_app.config['OSS_ENDPOINT'],
                current_app.config['OSS_BUCKET_NAME']
            )
            logger.info("OSS客户端初始化成功")
        except Exception as e:
            logger.error("OSS客户端初始化失败: %s", str(e))
            raise

    def upload_file(self, file_path, object_name=None):
        """上传文件到OSS"""
        try:
            if not object_name:
                object_name = f"attendance_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"

            result = self.bucket.put_object_from_file(object_name, file_path)
            if result.status == 200:
                logger.info(f"文件上传成功: {object_name}")
                return object_name
            return None
        except oss2.exceptions.OssError as e:
            logger.error(f"OSS上传失败: {e}")
            return None

    def generate_presigned_url(self, object_name, expiration=3600):
        """生成预签名下载链接"""
        try:
            return self.bucket.sign_url('GET', object_name, expiration)
        except oss2.exceptions.OssError as e:
            logger.error(f"生成下载链接失败: {e}")
            return None

    def list_files(self, prefix='attendance_'):
        """列出存储桶文件"""
        try:
            return [obj.key for obj in oss2.ObjectIterator(self.bucket, prefix=prefix)]
        except oss2.exceptions.OssError as e:
            logger.error(f"获取文件列表失败: {e}")
            return []
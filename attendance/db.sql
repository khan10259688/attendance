--数据库设计：
 -- 用户表
CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,       -- 用户ID（与学号/工号一致）
    username VARCHAR(50) UNIQUE NOT NULL,  -- 登录用户名（邮箱）
    password CHAR(60) NOT NULL,            -- 密码
    role ENUM('student', 'admin') NOT NULL,-- 用户角色
    last_login DATETIME,                   -- 最后登录时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- 用户创建时间
);

-- 教师表
CREATE TABLE teachers (
    teacher_id VARCHAR(20) PRIMARY KEY,  -- 工号
    name VARCHAR(50) NOT NULL,           -- 姓名
    email VARCHAR(100) NOT NULL,         -- 通知邮箱
	user_id VARCHAR(20) UNIQUE,			 -- 用户id（外键）
	FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 课程表（每天9:00-17:00）
CREATE TABLE courses (
    course_id VARCHAR(10) PRIMARY KEY,   -- 课程编号
    course_name VARCHAR(100) NOT NULL,   -- 课程名称
    teacher_id VARCHAR(20) NOT NULL,     -- 授课教师（外键）
    start_date DATE NOT NULL,            -- 开始日期(2025-04-01)
    end_date DATE NOT NULL,              -- 结束日期(2025-12-31)
	FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);

 -- 学生表（与虚拟数据库集成）
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,  -- 学号
    name VARCHAR(50) NOT NULL,           -- 姓名
    email VARCHAR(100) NOT NULL,         -- 通知邮箱
    course_id VARCHAR(10) NOT NULL,      -- 固定课程ID（外键）
	user_id VARCHAR(20) UNIQUE,          -- 用户id（外键）
	FOREIGN KEY (user_id) REFERENCES users(user_id),
	FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- 考勤记录表
CREATE TABLE attendance (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,      -- 学号
    course_id VARCHAR(10) NOT NULL,       -- 课程ID
    date DATE NOT NULL,                   -- 考勤日期
    check_in TIME,                        -- 签到时间
    check_out TIME,                       -- 签退时间
    status ENUM('Normal', 'Late', 'Early', 'Late + Early', 'Absent', 'Anomaly') DEFAULT 'Absent',
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);


--最终表关系图
--users
--├── teachers (1:1 via user_id)
--├── students (1:1 via user_id)
--│   └── courses (N:1 via course_id)
--└── courses
--    └── teachers (N:1 via teacher_id)
--
--attendance
--├── students (N:1 via student_id)
--└── courses (N:1 via course_id)
--
---- 创建顺序（注意外键依赖）
--1. CREATE TABLE users (...)
--2. CREATE TABLE teachers (...)
--3. CREATE TABLE courses (...)
--4. CREATE TABLE students (...)
--5. CREATE TABLE attendance (...)



-- 插入23个学生用户
INSERT INTO users (user_id, username, password, role) VALUES
('S2024001', '2024001@student.edu', '123456', 'student'),
('S2024002', '2024002@student.edu', '123456', 'student'),
('S2024003', '2024003@student.edu', '123456', 'student'),
('S2024004', '2024004@student.edu', '123456', 'student'),
('S2024005', '2024005@student.edu', '123456', 'student'),
('S2024006', '2024006@student.edu', '123456', 'student'),
('S2024007', '2024007@student.edu', '123456', 'student'),
('S2024008', '2024008@student.edu', '123456', 'student'),
('S2024009', '2024009@student.edu', '123456', 'student'),
('S2024010', '2024010@student.edu', '123456', 'student'),
('S2024011', '2024011@student.edu', '123456', 'student'),
('S2024012', '2024012@student.edu', '123456', 'student'),
('S2024013', '2024013@student.edu', '123456', 'student'),
('S2024014', '2024014@student.edu', '123456', 'student'),
('S2024015', '2024015@student.edu', '123456', 'student'),
('S2024016', '2024016@student.edu', '123456', 'student'),
('S2024017', '2024017@student.edu', '123456', 'student'),
('S2024018', '2024018@student.edu', '123456', 'student'),
('S2024019', '2024019@student.edu', '123456', 'student'),
('S2024020', '2024020@student.edu', '123456', 'student'),
('S2024021', '2024021@student.edu', '123456', 'student'),
('S2024022', '2024022@student.edu', '123456', 'student'),
('S2024023', '2024023@student.edu', '123456', 'student'),

-- 插入2个教师用户
('T2020001', '2020001@protessor.edu', '123456', 'admin'),
('T2020002', '2020002@protessor.edu', '123456', 'admin');


-- 插入教师
INSERT INTO teachers (teacher_id, name, email, user_id) VALUES
('2020001', 'Professor Wang', '2020001@protessor.edu', 'T2020001'),
('2020002', 'Professor Li', '2020002@protessor.edu', 'T2020002');

--插入课程
-- 王老师的课程
INSERT INTO courses (course_id, course_name, teacher_id, start_date, end_date)
VALUES ('CS101', 'Introduction to Computer Science', '2020001', '2025-04-01',  '2025-07-15');  -- 对应王老师的teacher_id

-- 李教授的课程
INSERT INTO courses (course_id, course_name, teacher_id, start_date, end_date)
VALUES ('MA201', 'Advanced Mathematics', '2020002', '2025-04-01', '2025-12-31'); -- 对应李教授的teacher_id


--插入学生
-- 插入学生信息（CS101课程）
INSERT INTO students (student_id, name, email, course_id, user_id) VALUES
('2024001', 'Liang Zhao', '2024001@student.edu', 'CS101', 'S2024001'),
('2024002', 'Wang Fang', '2024002@student.edu', 'CS101', 'S2024002'),
('2024003', 'Li Qiang', '2024003@student.edu', 'CS101', 'S2024003'),
('2024004', 'Liu Yang', '2024004@student.edu', 'CS101', 'S2024004'),
('2024005', 'Li Jing', '2024005@student.edu', 'CS101', 'S2024005'),
('2024006', 'Yang Yong', '2024006@student.edu', 'CS101', 'S2024006'),
('2024007', 'Huang Li', '2024007@student.edu', 'CS101', 'S2024007'),
('2024008', 'Zhou Jie', '2024008@student.edu', 'CS101', 'S2024008'),
('2024009', 'Wu Peng', '2024009@student.edu', 'CS101', 'S2024009'),
('2024010', 'Xu Ming', '2024010@student.edu', 'CS101', 'S2024010'),
('2024011', 'Sun Hao', '2024011@student.edu', 'CS101', 'S2024011'),
('2024012', 'Ma Na', '2024012@student.edu', 'CS101', 'S2024012');

-- 插入学生信息（MA201课程）
INSERT INTO students (student_id, name, email, course_id, user_id) VALUES
('2024013', 'Zhu Tao', '2024013@student.edu', 'MA201', 'S2024013'),
('2024014', 'Hu Xue', '2024014@student.edu', 'MA201', 'S2024014'),
('2024015', 'Lin Feng', '2024015@student.edu', 'MA201', 'S2024015'),
('2024016', 'He Jun', '2024016@student.edu', 'MA201', 'S2024016'),
('2024017', 'Gao Xia', '2024017@student.edu', 'MA201', 'S2024017'),
('2024018', 'Liang Bin', '2024018@student.edu', 'MA201', 'S2024018'),
('2024019', 'Xie Fang', '2024019@student.edu', 'MA201', 'S2024019'),
('2024020', 'Luo Min', '2024020@student.edu', 'MA201', 'S2024020'),
('2024021', 'Song Jie', '2024021@student.edu', 'MA201', 'S2024021'),
('2024022', 'Tang Li', '2024022@student.edu', 'MA201', 'S2024022'),
('2024023', 'Dong Hao', '2024023@student.edu', 'MA201', 'S2024023');
import pymysql
import random
from datetime import datetime, timedelta
import string
from faker import Faker

# 设置中文环境
fake = Faker(['zh_CN'])

def get_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="university",
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def generate_departments(num_departments=10):
    """生成院系数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 预定义的院系名称
    dept_names = [
        "计算机科学与技术学院", "数学学院", "物理学院", "化学学院", 
        "生命科学学院", "经济学院", "管理学院", "法学院", 
        "文学院", "历史学院", "哲学学院", "艺术学院",
        "医学院", "工学院", "农学院", "教育学院"
    ]
    
    try:
        for i in range(min(num_departments, len(dept_names))):
            dept_id = f"D{i+1:03d}"
            dept_name = dept_names[i]
            
            cursor.execute("INSERT IGNORE INTO department (dept_id, dept_name) VALUES (%s, %s)", 
                          (dept_id, dept_name))
        
        conn.commit()
        print(f"已生成 {num_departments} 个院系")
    except Exception as e:
        print(f"生成院系数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_courses(num_courses=50):
    """生成课程数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有院系ID
    cursor.execute("SELECT dept_id FROM department")
    dept_ids = [row[0] for row in cursor.fetchall()]
    
    if not dept_ids:
        print("没有找到院系数据，请先生成院系数据")
        cursor.close()
        conn.close()
        return
    
    # 预定义的课程名称
    course_names = [
        "高等数学", "线性代数", "概率论与数理统计", "离散数学", "数据结构",
        "算法设计", "操作系统", "计算机网络", "数据库原理", "软件工程",
        "计算机组成原理", "编译原理", "人工智能", "机器学习", "深度学习",
        "数字图像处理", "计算机图形学", "软件测试", "项目管理", "信息安全",
        "微积分", "数学分析", "高等代数", "复变函数", "实变函数",
        "泛函分析", "拓扑学", "微分几何", "代数几何", "数论",
        "大学物理", "电磁学", "光学", "热学", "量子力学",
        "理论力学", "电动力学", "统计物理", "固体物理", "原子物理",
        "无机化学", "有机化学", "分析化学", "物理化学", "生物化学",
        "分子生物学", "细胞生物学", "遗传学", "生态学", "微生物学"
    ]
    
    try:
        for i in range(min(num_courses, len(course_names))):
            course_id = f"C{i+1:03d}"
            course_name = course_names[i]
            dept_id = random.choice(dept_ids)
            credit = random.randint(2, 6)  # 2-6学分
            
            cursor.execute("INSERT IGNORE INTO course (course_id, course_name, dept_id, credit) VALUES (%s, %s, %s, %s)", 
                          (course_id, course_name, dept_id, credit))
        
        conn.commit()
        print(f"已生成 {num_courses} 门课程")
    except Exception as e:
        print(f"生成课程数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_devices(num_devices=20):
    """生成设备数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 预定义的设备名称
    device_names = [
        "iPhone 15", "iPhone 14", "iPhone 13", "iPhone 12", "iPhone 11",
        "Samsung Galaxy S24", "Samsung Galaxy S23", "Samsung Galaxy S22", "Samsung Galaxy S21",
        "Huawei Mate 60", "Huawei P60", "Huawei Mate 50", "Huawei P50",
        "Xiaomi 14", "Xiaomi 13", "Xiaomi 12", "Xiaomi 11",
        "MacBook Pro", "MacBook Air", "iMac", "Mac mini",
        "Dell XPS", "Lenovo ThinkPad", "HP Spectre", "ASUS ZenBook",
        "iPad Pro", "iPad Air", "iPad", "iPad mini",
        "Windows Desktop", "Linux Desktop", "ChromeBook"
    ]
    
    try:
        for i in range(min(num_devices, len(device_names))):
            device_id = f"DEV{i+1:03d}"
            device_name = device_names[i]
            
            cursor.execute("INSERT IGNORE INTO device (device_id, device_name) VALUES (%s, %s)", 
                          (device_id, device_name))
        
        conn.commit()
        print(f"已生成 {num_devices} 个设备")
    except Exception as e:
        print(f"生成设备数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_id_card():
    """生成18位身份证号"""
    # 简化的身份证号生成，实际应该更复杂
    area_code = random.choice(['110101', '110102', '110105', '110106', '110107', '110108', '110109'])
    birth_date = fake.date_between(start_date='-25y', end_date='-18y').strftime('%Y%m%d')
    sequence = ''.join(random.choices(string.digits, k=3))
    check_code = random.choice(string.digits + 'X')
    return f"{area_code}{birth_date}{sequence}{check_code}"

def generate_students(num_students=200):
    """生成学生数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有院系ID
    cursor.execute("SELECT dept_id FROM department")
    dept_ids = [row[0] for row in cursor.fetchall()]
    
    if not dept_ids:
        print("没有找到院系数据，请先生成院系数据")
        cursor.close()
        conn.close()
        return
    
    # 预定义的姓氏
    surnames = [
        "王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
        "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
        "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
        "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
        "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎"
    ]
    
    # 预定义的名字
    given_names = [
        "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
        "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞",
        "平", "刚", "桂英", "建华", "建国", "建军", "建平", "建华", "建华", "建华",
        "建华", "建华", "建华", "建华", "建华", "建华", "建华", "建华", "建华", "建华"
    ]
    
    try:
        for i in range(num_students):
            stu_id = f"{random.randint(2020, 2024)}{random.randint(1, 9999):04d}"
            name = random.choice(surnames) + random.choice(given_names)
            birth_date = fake.date_between(start_date='-25y', end_date='-18y')
            id_card = generate_id_card()
            address = fake.address()
            dept_id = random.choice(dept_ids)
            
            cursor.execute("INSERT IGNORE INTO student (stu_id, name, birth_date, id_card, address, dept_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                          (stu_id, name, birth_date, id_card, address, dept_id))
        
        conn.commit()
        print(f"已生成 {num_students} 个学生")
    except Exception as e:
        print(f"生成学生数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_enrollments(num_enrollments=500):
    """生成选课数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID和课程ID
    cursor.execute("SELECT stu_id FROM student")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT course_id FROM course")
    course_ids = [row[0] for row in cursor.fetchall()]
    
    if not student_ids or not course_ids:
        print("没有找到学生或课程数据，请先生成相关数据")
        cursor.close()
        conn.close()
        return
    
    try:
        enrollments = set()
        for _ in range(num_enrollments):
            stu_id = random.choice(student_ids)
            course_id = random.choice(course_ids)
            
            # 避免重复选课
            if (stu_id, course_id) not in enrollments:
                grade = random.randint(60, 100) if random.random() > 0.1 else None  # 10%概率没有成绩
                
                cursor.execute("INSERT IGNORE INTO enrollment (stu_id, course_id, grade) VALUES (%s, %s, %s)", 
                              (stu_id, course_id, grade))
                enrollments.add((stu_id, course_id))
        
        conn.commit()
        print(f"已生成 {len(enrollments)} 条选课记录")
    except Exception as e:
        print(f"生成选课数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_friendships(num_friendships=300):
    """生成好友关系数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID
    cursor.execute("SELECT stu_id FROM student where stu_id !='10000'")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    if len(student_ids) < 2:
        print("学生数量不足，无法生成好友关系")
        cursor.close()
        conn.close()
        return
    
    try:
        friendships = set()
        for _ in range(num_friendships):
            stu_id1, stu_id2 = random.sample(student_ids, 2)
            
            # 避免重复和自环
            if stu_id1 != stu_id2 and (stu_id1, stu_id2) not in friendships and (stu_id2, stu_id1) not in friendships:
                cursor.execute("INSERT IGNORE INTO friendship (stu_id1, stu_id2) VALUES (%s, %s)", 
                              (stu_id1, stu_id2))
                cursor.execute("INSERT IGNORE INTO friendship (stu_id1, stu_id2) VALUES (%s, %s)", 
                              (stu_id2, stu_id1))
                friendships.add((stu_id1, stu_id2))
        
        conn.commit()
        print(f"已生成 {len(friendships)} 对好友关系")
    except Exception as e:
        print(f"生成好友关系数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_login_logs(num_logs=1000):
    """生成登录日志数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID和设备ID
    cursor.execute("SELECT stu_id FROM student")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT device_id FROM device")
    device_ids = [row[0] for row in cursor.fetchall()]
    
    if not student_ids or not device_ids:
        print("没有找到学生或设备数据，请先生成相关数据")
        cursor.close()
        conn.close()
        return
    
    try:
        # 生成过去30天的登录记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for _ in range(num_logs):
            stu_id = random.choice(student_ids)
            device_id = random.choice(device_ids)
            login_time = fake.date_time_between(start_date=start_date, end_date=end_date)
            
            cursor.execute("INSERT INTO login_log (stu_id, login_time, device_id) VALUES (%s, %s, %s)", 
                          (stu_id, login_time, device_id))
        
        conn.commit()
        print(f"已生成 {num_logs} 条登录日志")
    except Exception as e:
        print(f"生成登录日志数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_messages(num_messages=500):
    """生成消息数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID和设备ID
    cursor.execute("SELECT stu_id FROM student")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT device_id FROM device")
    device_ids = [row[0] for row in cursor.fetchall()]
    
    if len(student_ids) < 2 or not device_ids:
        print("学生或设备数量不足，无法生成消息数据")
        cursor.close()
        conn.close()
        return
    
    # 预定义的消息内容
    message_contents = [
        "你好！", "在吗？", "今天天气不错", "一起去吃饭吧", "作业写完了吗？",
        "明天有课吗？", "周末有什么安排？", "最近怎么样？", "考试加油！", "生日快乐！",
        "谢谢！", "不客气", "好的", "没问题", "再见！",
        "明天见", "路上小心", "注意安全", "早点休息", "晚安！",
        "早上好", "下午好", "晚上好", "周末愉快", "节日快乐！",
        "学习加油", "工作顺利", "身体健康", "万事如意", "心想事成"
    ]
    
    try:
        # 生成过去7天的消息记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        for _ in range(num_messages):
            from_stu_id, to_stu_id = random.sample(student_ids, 2)
            content = random.choice(message_contents)
            send_time = fake.date_time_between(start_date=start_date, end_date=end_date)
            device_id = random.choice(device_ids)
            
            cursor.execute("INSERT INTO message (from_stu_id, to_stu_id, content, send_time, device_id) VALUES (%s, %s, %s, %s, %s)", 
                          (from_stu_id, to_stu_id, content, send_time, device_id))
        
        conn.commit()
        print(f"已生成 {num_messages} 条消息")
    except Exception as e:
        print(f"生成消息数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_transfers(num_transfers=200):
    """生成转账记录数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID和设备ID
    cursor.execute("SELECT stu_id FROM student")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT device_id FROM device")
    device_ids = [row[0] for row in cursor.fetchall()]
    
    if len(student_ids) < 2 or not device_ids:
        print("学生或设备数量不足，无法生成转账数据")
        cursor.close()
        conn.close()
        return
    
    try:
        # 生成过去30天的转账记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for _ in range(num_transfers):
            from_stu_id, to_stu_id = random.sample(student_ids, 2)
            amount = round(random.uniform(1.0, 1000.0), 2)  # 1-1000元
            transfer_time = fake.date_time_between(start_date=start_date, end_date=end_date)
            device_id = random.choice(device_ids)
            
            cursor.execute("INSERT INTO transfer (from_stu_id, to_stu_id, amount, transfer_time, device_id) VALUES (%s, %s, %s, %s, %s)", 
                          (from_stu_id, to_stu_id, amount, transfer_time, device_id))
        
        conn.commit()
        print(f"已生成 {num_transfers} 条转账记录")
    except Exception as e:
        print(f"生成转账数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_warnings(num_warnings=50):
    """生成警告记录数据"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 获取所有学生ID
    cursor.execute("SELECT stu_id FROM student")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    if not student_ids:
        print("没有找到学生数据，请先生成学生数据")
        cursor.close()
        conn.close()
        return
    
    # 预定义的警告原因
    warning_reasons = [
        "旷课次数过多", "作业未按时提交", "考试作弊", "违反校规校纪",
        "宿舍卫生不合格", "晚归", "打架斗殴", "考试不及格",
        "使用违规电器", "在宿舍吸烟", "扰乱课堂秩序", "抄袭作业",
        "无故缺勤", "不服从管理", "损坏公物", "携带违禁物品"
    ]
    
    try:
        # 生成过去90天的警告记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        for _ in range(num_warnings):
            stu_id = random.choice(student_ids)
            warn_time = fake.date_time_between(start_date=start_date, end_date=end_date)
            reason = random.choice(warning_reasons)
            
            cursor.execute("INSERT INTO warning (stu_id, warn_time, reason) VALUES (%s, %s, %s)", 
                          (stu_id, warn_time, reason))
        
        conn.commit()
        print(f"已生成 {num_warnings} 条警告记录")
    except Exception as e:
        print(f"生成警告数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_all_data():
    """生成所有表的数据"""
    print("开始生成数据库测试数据...")
    print("=" * 50)
    
    # 按依赖关系顺序生成数据
    generate_friendships(6400)     # 生成500对好友关系
    
    print("=" * 50)
    print("所有数据生成完成！")

if __name__ == "__main__":
    generate_all_data()

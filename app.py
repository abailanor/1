from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from datetime import datetime
import json
from functools import wraps
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os

app = Flask(__name__)
CORS(app)

INDEX_DIR = "whoosh_index"

def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="university",
            charset='utf8mb4'
        )
        return conn
    except Exception as err:
        print(f"数据库连接失败: {err}")
        return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = request.get_json(silent=True) or {}
            stu_id = data.get('stu_id')
        else:
            stu_id = request.args.get('stu_id')
        if not stu_id or stu_id != '10000':
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 学生登录验证
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    stu_id = data.get('stu_id')
    id_card = data.get('id_card')
    
    if not stu_id or not id_card:
        return jsonify({'success': False, 'message': '请输入学号和身份证号'})
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM student WHERE stu_id = %s AND id_card = %s", (stu_id, id_card))
        student = cursor.fetchone()
        
        if student:
            # 记录登录日志
            device_id = data.get('device_id', 'web')
            try:
                cursor.execute(
                    "INSERT INTO login_log (stu_id, login_time, device_id) VALUES (%s, %s, %s)",
                    (stu_id, datetime.now(), device_id)
                )
                conn.commit()
            except:
                cursor.execute(
                    "INSERT INTO device (device_id,device_name) VALUES (%s, %s)",
                    (device_id,device_id+'1')
                )
                conn.commit()
                cursor.execute(
                    "INSERT INTO login_log (stu_id, login_time, device_id) VALUES (%s, %s, %s)",
                    (stu_id, datetime.now(), device_id)
                )
                conn.commit()
            
            return jsonify({
                'success': True,
                'student': {
                    'stu_id': student['stu_id'],
                    'name': student['name'],
                    'dept_id': student['dept_id'],
                    'isAdmin': student['stu_id'] == '10000'
                }
            })
        else:
            return jsonify({'success': False, 'message': '学号或身份证号错误'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取学生信息
@app.route('/api/student/<stu_id>', methods=['GET'])
def get_student(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT s.*, d.dept_name 
            FROM student s 
            JOIN department d ON s.dept_id = d.dept_id 
            WHERE s.stu_id = %s
        """, (stu_id,))
        student = cursor.fetchone()
        
        if student:
            return jsonify({'success': True, 'student': student})
        else:
            return jsonify({'success': False, 'message': '学生不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取课程列表
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT c.*, d.dept_name 
            FROM course c 
            JOIN department d ON c.dept_id = d.dept_id
        """)
        courses = cursor.fetchall()
        return jsonify({'success': True, 'courses': courses})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 学生选课
@app.route('/api/enroll', methods=['POST'])
def enroll_course():
    data = request.get_json()
    stu_id = data.get('stu_id')
    course_id = data.get('course_id')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO enrollment (stu_id, course_id) VALUES (%s, %s)", 
                      (stu_id, course_id))
        conn.commit()
        return jsonify({'success': True, 'message': '选课成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'选课失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取学生已选课程
@app.route('/api/student/<stu_id>/courses', methods=['GET'])
def get_student_courses(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT e.*, c.course_name, c.credit, d.dept_name
            FROM enrollment e
            JOIN course c ON e.course_id = c.course_id
            JOIN department d ON c.dept_id = d.dept_id
            WHERE e.stu_id = %s
        """, (stu_id,))
        courses = cursor.fetchall()
        return jsonify({'success': True, 'courses': courses})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 添加好友
@app.route('/api/friendship', methods=['POST'])
def add_friend():
    data = request.get_json()
    stu_id1 = data.get('stu_id1')
    stu_id2 = data.get('stu_id2')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO friendship (stu_id1, stu_id2) VALUES (%s, %s)", 
                      (stu_id1, stu_id2))
        cursor.execute("INSERT INTO friendship (stu_id1, stu_id2) VALUES (%s, %s)", 
                      (stu_id2, stu_id1))
        conn.commit()
        return jsonify({'success': True, 'message': '添加好友成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加好友失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取好友列表
@app.route('/api/student/<stu_id>/friends', methods=['GET'])
def get_friends(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT s.stu_id, s.name, s.dept_id, d.dept_name
            FROM friendship f
            JOIN student s ON (f.stu_id1 = s.stu_id OR f.stu_id2 = s.stu_id)
            JOIN department d ON s.dept_id = d.dept_id
            WHERE (f.stu_id1 = %s OR f.stu_id2 = %s) AND s.stu_id != %s
        """, (stu_id, stu_id, stu_id))
        friends = cursor.fetchall()
        return jsonify({'success': True, 'friends': friends})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 发送消息
@app.route('/api/message', methods=['POST'])
def send_message():
    data = request.get_json()
    from_stu = data.get('from_stu_id')
    to_stu = data.get('to_stu_id')
    content = data.get('content')
    device_id = data.get('device_id', 'web')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO message (from_stu_id, to_stu_id, content, send_time, device_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (from_stu, to_stu, content, datetime.now(), device_id))
        conn.commit()
        return jsonify({'success': True, 'message': '消息发送成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送消息失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取消息列表
@app.route('/api/student/<stu_id>/messages', methods=['GET'])
def get_messages(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT m.*, 
                   s1.name as from_name, 
                   s2.name as to_name
            FROM message m
            JOIN student s1 ON m.from_stu_id = s1.stu_id
            JOIN student s2 ON m.to_stu_id = s2.stu_id
            WHERE m.from_stu_id = %s OR m.to_stu_id = %s
            ORDER BY m.send_time DESC
        """, (stu_id, stu_id))
        messages = cursor.fetchall()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 转账
@app.route('/api/transfer', methods=['POST'])
def transfer_money():
    data = request.get_json()
    from_stu = data.get('from_stu_id')
    to_stu = data.get('to_stu_id')
    amount = data.get('amount')
    device_id = data.get('device_id', 'web')
    
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transfer (from_stu_id, to_stu_id, amount, transfer_time, device_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (from_stu, to_stu, amount, datetime.now(), device_id))
        
        # 大额转账警告
        if float(amount) > 1000:
            cursor.execute("""
                INSERT INTO warning (stu_id, warn_time, reason) 
                VALUES (%s, %s, %s)
            """, (from_stu, datetime.now(), f'大额转账警告：向{to_stu}转账{amount}元'))
        
        conn.commit()
        return jsonify({'success': True, 'message': '转账成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'转账失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 获取转账记录
@app.route('/api/student/<stu_id>/transfers', methods=['GET'])
def get_transfers(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT t.*, 
                   s1.name as from_name, 
                   s2.name as to_name
            FROM transfer t
            JOIN student s1 ON t.from_stu_id = s1.stu_id
            JOIN student s2 ON t.to_stu_id = s2.stu_id
            WHERE t.from_stu_id = %s OR t.to_stu_id = %s
            ORDER BY t.transfer_time DESC
        """, (stu_id, stu_id))
        transfers = cursor.fetchall()
        return jsonify({'success': True, 'transfers': transfers})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 好友推荐
@app.route('/api/student/<stu_id>/recommendations', methods=['GET'])
def recommend_friends(stu_id):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
        SELECT 
            CASE WHEN f1.stu_id1 < f2.stu_id1 THEN f1.stu_id1 ELSE f2.stu_id1 END AS user1,
            CASE WHEN f1.stu_id1 < f2.stu_id1 THEN f2.stu_id1 ELSE f1.stu_id1 END AS user2,
            COUNT(*) AS common_count
        FROM 
            friendship f1
        JOIN friendship f2 
            ON f1.stu_id2 = f2.stu_id2
            AND f1.stu_id1 != f2.stu_id1
        WHERE 
            (f1.stu_id1 = %s OR f2.stu_id1 = %s)
            AND NOT EXISTS (
                SELECT 1 
                FROM friendship f 
                WHERE (f.stu_id1 = f1.stu_id1 AND f.stu_id2 = f2.stu_id1)
                   OR (f.stu_id1 = f2.stu_id1 AND f.stu_id2 = f1.stu_id1)
            )
        GROUP BY user1, user2
        HAVING common_count >= 2
        ORDER BY common_count DESC
        LIMIT 20
        """
        
        cursor.execute(query, (stu_id, stu_id))
        results = cursor.fetchall()
        
        recommendations = []
        for row in results:
            other_user = row['user1'] if row['user1'] != stu_id else row['user2']
            cursor.execute("""
                SELECT s.stu_id, s.name, s.dept_id, d.dept_name
                FROM student s
                JOIN department d ON s.dept_id = d.dept_id
                WHERE s.stu_id = %s
            """, (other_user,))
            student_info = cursor.fetchone()
            if student_info:
                recommendations.append({
                    'student': student_info,
                    'common_friends': row['common_count']
                })
        
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'message': f'推荐失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 获取所有表
@app.route('/api/admin/tables', methods=['GET'])
@admin_required
def get_tables():
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return jsonify({'success': True, 'tables': tables})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 获取表数据
@app.route('/api/admin/table/<table_name>', methods=['GET'])
@admin_required
def get_table_data(table_name):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 新增表数据
@app.route('/api/admin/table/<table_name>', methods=['POST'])
@admin_required
def admin_insert_table(table_name):
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    cursor = conn.cursor()
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = list(data.values())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({'success': True, 'message': '插入成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'插入失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 更新表数据
@app.route('/api/admin/table/<table_name>/<pk_name>/<pk_value>', methods=['PUT'])
@admin_required
def admin_update_table(table_name, pk_name, pk_value):
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    cursor = conn.cursor()
    try:
        set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
        values = list(data.values())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_name}=%s"
        values.append(pk_value)
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 删除表数据
@app.route('/api/admin/table/<table_name>/<pk_name>/<pk_value>', methods=['DELETE'])
@admin_required
def admin_delete_table(table_name, pk_name, pk_value):
    conn = get_connection()
    if not conn:
        return jsonify({'success': False, 'message': '数据库连接失败'})
    cursor = conn.cursor()
    try:
        sql = f"DELETE FROM {table_name} WHERE {pk_name}=%s"
        cursor.execute(sql, (pk_value,))
        conn.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# 管理员功能 - 搜索消息
@app.route('/api/admin/search_message', methods=['GET'])
@admin_required
def admin_search_message():
    keyword = request.args.get('keyword', '')
    from_stu_id = request.args.get('from_stu_id', None)
    if not keyword:
        return jsonify({'success': False, 'message': '请输入关键词'})
    # 优先用Whoosh全文检索，否则用MySQL LIKE
    try:
        from whoosh.index import open_dir
        from whoosh.qparser import QueryParser
        ix = open_dir('whoosh_index')
        with ix.searcher() as searcher:
            qp = QueryParser('content', schema=ix.schema)
            q = qp.parse(keyword)
            results = searcher.search(q, limit=100)
            filtered = []
            for r in results:
                if from_stu_id and r['from_stu_id'] != str(from_stu_id):
                    continue
                filtered.append({
                    'message_id': r['message_id'],
                    'from_stu_id': r['from_stu_id'],
                    'content': r['content']
                })
        return jsonify({'success': True, 'results': filtered})
    except Exception as e:
        # Fallback: MySQL LIKE
        conn = get_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        cursor = conn.cursor()
        try:
            sql = "SELECT message_id, from_stu_id, content FROM message WHERE content LIKE %s"
            params = [f"%{keyword}%"]
            if from_stu_id:
                sql += " AND from_stu_id = %s"
                params.append(from_stu_id)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            results = [{'message_id': str(r[0]), 'from_stu_id': str(r[1]), 'content': r[2]} for r in rows]
            return jsonify({'success': True, 'results': results})
        except Exception as e2:
            return jsonify({'success': False, 'message': f'检索失败: {str(e2)}'})
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
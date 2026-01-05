#!/usr/bin/env python
"""
初始化管理员用户脚本
用于创建第一个管理员用户（同时也是作者用户）

使用方法:
    python init_admin_user.py <username> <password> <protect_question> <protect_answer>

参数说明:
    username: 用户名
    password: 密码（需符合密码规则：至少8位，包含数字、大写字母、小写字母）
    protect_question: 密保问题
    protect_answer: 密保答案（只能包含中文、英文和数字）

示例:
    python init_admin_user.py admin Aa123456 你喜欢什么 编写代码
"""
import os
import sys
import django
import re
import argparse

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_back.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from django.db import connection, IntegrityError

# 与注册时一致的校验规则
DB_KEYWORDS = [
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
    'USER', 'USERS', 'ORDER', 'GROUP', 'KEY', 'INDEX', 'TABLE', 'PASSWORD', 'ROOT'
]

def validate_username(value: str) -> str:
    """返回错误字符串，空串表示通过"""
    if not value:
        return '请输入用户名'
    if not re.fullmatch(r'^[A-Za-z0-9_\-\u4e00-\u9fa5]+$', value):
        return '只允许字母、数字、下划线、连字符、中文'
    if value.upper() in DB_KEYWORDS:
        return '不得使用该用户名，请更换'
    return ''

def validate_password(value: str) -> str:
    """返回错误字符串，空串表示通过"""
    if not value:
        return '请输入密码'
    if len(value) < 8:
        return '密码至少 8 位'
    if not re.search(r'[0-9]', value):
        return '需包含数字'
    if not re.search(r'[A-Z]', value):
        return '需包含大写字母'
    if not re.search(r'[a-z]', value):
        return '需包含小写字母'
    return ''

def validate_answer(value: str) -> str:
    """返回错误字符串，空串表示通过"""
    if not value:
        return '请输入密保答案'
    if not re.fullmatch(r'[\u4e00-\u9fa5A-Za-z0-9]+', value):
        return '答案只能包含中文、英文和数字'
    return ''

def init_admin_user(username, password, protect_question, protect_answer):
    """初始化管理员用户"""
    print("=" * 60)
    print("初始化管理员用户")
    print("=" * 60)
    
    # 验证输入
    errors = []
    if msg := validate_username(username):
        errors.append(f"用户名错误: {msg}")
    if msg := validate_password(password):
        errors.append(f"密码错误: {msg}")
    if not protect_question.strip():
        errors.append("密保问题不能为空")
    if msg := validate_answer(protect_answer):
        errors.append(f"密保答案错误: {msg}")
    
    if errors:
        print("验证失败:")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    
    # 检查用户是否已存在
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username FROM users WHERE username = %s", [username])
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id, existing_username = existing_user
            print(f"✗ 错误: 用户名 '{existing_username}' (id={user_id}) 已存在")
            return False
        
        # 检查是否已有用户
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"警告: 数据库中已存在 {user_count} 个用户")
            response = input("是否继续创建管理员用户？(y/n): ")
            if response.lower() != 'y':
                print("已取消创建")
                return False
        
        # 生成哈希值
        password_hash = make_password(password)
        answer_hash = make_password(protect_answer)
        
        try:
            # 插入用户（id=1，is_admin=1）
            cursor.execute(
                "INSERT INTO users (id, username, password, protect, answer, registered_time, is_admin) VALUES (1, %s, %s, %s, %s, NOW(), 1)",
                [username, password_hash, protect_question.strip(), answer_hash]
            )
            
            print()
            print("✓ 管理员用户创建成功！")
            print()
            print("用户信息:")
            print(f"  用户名: {username}")
            print(f"  密码: {password}")
            print(f"  密保问题: {protect_question}")
            print(f"  密保答案: {protect_answer}")
            print(f"  用户ID: 1")
            print(f"  管理员权限: 是")
            print()
            print("=" * 60)
            return True
            
        except IntegrityError as e:
            if 'PRIMARY' in str(e) or 'id' in str(e).lower():
                print(f"✗ 错误: ID=1 的用户已存在")
            elif 'username' in str(e).lower() or 'Duplicate' in str(e):
                print(f"✗ 错误: 用户名 '{username}' 已存在")
            else:
                print(f"✗ 错误: {e}")
            return False
        except Exception as e:
            print(f"✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='初始化管理员用户（同时也是作者用户）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python init_admin_user.py admin Aa123456 你喜欢什么 编写代码

注意:
  - 密码需符合规则：至少8位，包含数字、大写字母、小写字母
  - 密保答案只能包含中文、英文和数字
  - 用户名不能使用数据库保留字
        """
    )
    
    parser.add_argument('username', help='用户名')
    parser.add_argument('password', help='密码')
    parser.add_argument('protect_question', help='密保问题')
    parser.add_argument('protect_answer', help='密保答案')
    
    args = parser.parse_args()
    
    success = init_admin_user(
        args.username,
        args.password,
        args.protect_question,
        args.protect_answer
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()


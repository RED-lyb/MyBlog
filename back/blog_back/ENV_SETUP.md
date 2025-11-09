# 环境变量配置说明

## 📋 配置步骤

### 1. 创建环境变量文件

在 `back/blog_back/` 目录下创建 `.env` 文件：

```bash
cd back/blog_back
# Windows (PowerShell)
New-Item -ItemType File -Path .env

# Linux/Mac
touch .env
```

### 2. 配置环境变量

将以下内容复制到 `.env` 文件中，并填入实际值：

```env
# Django Secret Key（生产环境必须修改）
# 生成方式：python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=your-secret-key-here

# 数据库配置
DB_NAME=webproject
DB_USER=admin
DB_PASSWORD=your-database-password
DB_HOST=127.0.0.1
```

### 3. 生成 Secret Key

使用以下命令生成安全的 Secret Key：

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

将生成的密钥复制到 `.env` 文件的 `DJANGO_SECRET_KEY` 中。

## 重要提示

1. **`.env` 文件不会被提交到 Git**，请妥善保管
2. **生产环境必须设置所有配置项**，不能使用默认值
3. **开发环境**可以使用默认值，但建议也配置环境变量
4. **不要将 `.env` 文件分享给他人**，每个人应该创建自己的配置文件

## 使用方式

### 方式一：使用 .env 文件（推荐）

安装 `python-dotenv` 包（如果还没有安装）：

```bash
pip install python-dotenv
```

在 `settings.py` 文件开头添加：

```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

### 方式二：直接设置环境变量

**Windows (PowerShell):**
```powershell
$env:DJANGO_SECRET_KEY="your-secret-key"
$env:DB_PASSWORD="your-password"
```

**Linux/Mac:**
```bash
export DJANGO_SECRET_KEY="your-secret-key"
export DB_PASSWORD="your-password"
```

| 环境变量 | 说明 | 是否必需 | 默认值 |
|---------|------|---------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | 生产环境必需 | `SECRET_KEY_REMOVED_FROM_HISTORY` |
| `DB_NAME` | 数据库名称 | 可选 | `webproject` |
| `DB_USER` | 数据库用户名 | 可选 | `admin` |
| `DB_PASSWORD` | 数据库密码 | 生产环境必需 | 无（生产环境必须设置） |
| `DB_HOST` | 数据库主机 | 可选 | `127.0.0.1` |


"""应用配置：密钥、token 有效期、用户名/密码规则、CORS。"""

import os

# JWT 密钥：生产环境务必通过环境变量覆盖（默认仅用于本地开发）
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "dev-insecure-change-me-please-override-in-production"
)
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

# 用户名规则
USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 32
USERNAME_PATTERN = r"^[A-Za-z0-9_]+$"

# 密码规则
PASSWORD_MIN_LEN = 6

# CORS 允许源（逗号分隔）
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# 静态文件托管（Windows 便携版/安装版启用）
SERVE_STATIC = os.environ.get("SERVE_STATIC", "").lower() in ("1", "true", "yes")
STATIC_DIR = os.environ.get("STATIC_DIR", "")

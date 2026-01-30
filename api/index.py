import os
import sys

# 将根目录添加到 Python 路径，确保能找到 app 模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app

import os
import sys

# 强制将当前目录和上级目录加入路径，解决 Vercel 模块找不到的问题
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from app.main import app

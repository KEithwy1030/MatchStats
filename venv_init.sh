#!/bin/bash
# MatchStats 虚拟环境初始化脚本 (Linux/Mac)
# 使用方法: chmod +x venv_init.sh && ./venv_init.sh

echo "================================"
echo "MatchStats 虚拟环境初始化"
echo "================================"
echo ""

# 检查 Python
echo "检查 Python..."
python3 --version
echo ""

# 创建虚拟环境
echo "创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  虚拟环境已创建: venv/"
else
    echo "  虚拟环境已存在"
fi
echo ""

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建 .env 文件
echo ""
echo "检查配置文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  已创建 .env 文件，请配置你的 API Token"
else
    echo "  .env 文件已存在"
fi

# 创建数据目录
echo ""
echo "创建数据目录..."
mkdir -p data logs

echo ""
echo "================================"
echo "初始化完成！"
echo "================================"
echo ""
echo "使用方法:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 编辑 .env 文件，配置 FD_API_TOKEN"
echo "3. 运行服务: python -m app.main"
echo ""

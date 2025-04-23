# 在项目目录中创建名为 venv 的虚拟环境
python3 -m venv venv

# 使用绝对路径激活
source /path/to/your/project/venv/bin/activate

# 激活后终端提示符变化示例：
(venv) user@server:~/project$

# 安装 Python 3.8 并创建新虚拟环境
sudo yum install -y python38 python38-devel
python3.8 -m venv venv38
source venv38/bin/activate

# 生成完整依赖列表
pip freeze > requirements.txt

# 安装项目依赖
pip install -r requirements.txt


# 在虚拟环境中操作
pip uninstall -y -r requirements.txt
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall


pip install flask
pip freeze > requirements.txt
python run.py
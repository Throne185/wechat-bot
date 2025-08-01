"""
云服务器部署脚本
"""
import os
import sys
import subprocess
import platform

def create_systemd_service():
    """创建systemd服务文件"""
    service_content = """[Unit]
Description=WeChat Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wechat-bot
ExecStart=/usr/bin/python3 wechat_bot.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/wechat-bot

[Install]
WantedBy=multi-user.target
"""
    
    print("创建systemd服务文件...")
    try:
        with open("/etc/systemd/system/wechat-bot.service", "w") as f:
            f.write(service_content)
        print("✅ 服务文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 服务文件创建失败: {e}")
        return False

def create_nginx_config():
    """创建Nginx配置（如果需要Web管理界面）"""
    nginx_content = """server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 静态文件
    location /static/ {
        alias /opt/wechat-bot/static/;
    }
}
"""
    
    print("创建Nginx配置文件...")
    try:
        with open("/etc/nginx/sites-available/wechat-bot", "w") as f:
            f.write(nginx_content)
        
        # 创建软链接
        if not os.path.exists("/etc/nginx/sites-enabled/wechat-bot"):
            os.symlink("/etc/nginx/sites-available/wechat-bot", 
                      "/etc/nginx/sites-enabled/wechat-bot")
        
        print("✅ Nginx配置创建成功")
        return True
    except Exception as e:
        print(f"❌ Nginx配置创建失败: {e}")
        return False

def install_system_dependencies():
    """安装系统依赖"""
    print("安装系统依赖...")
    
    commands = [
        "apt update",
        "apt install -y python3 python3-pip python3-venv",
        "apt install -y nginx supervisor",  # 可选的进程管理工具
        "apt install -y git curl wget"
    ]
    
    for cmd in commands:
        try:
            print(f"执行: {cmd}")
            subprocess.run(cmd.split(), check=True)
            print(f"✅ {cmd} 执行成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {cmd} 执行失败: {e}")
            return False
    
    return True

def setup_project_directory():
    """设置项目目录"""
    project_dir = "/opt/wechat-bot"
    
    print(f"设置项目目录: {project_dir}")
    
    try:
        # 创建项目目录
        os.makedirs(project_dir, exist_ok=True)
        
        # 设置权限
        os.chmod(project_dir, 0o755)
        
        # 创建子目录
        subdirs = ["data", "logs", "utils", "plugins", "static"]
        for subdir in subdirs:
            os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)
        
        print("✅ 项目目录设置成功")
        return True
        
    except Exception as e:
        print(f"❌ 项目目录设置失败: {e}")
        return False

def create_deployment_script():
    """创建部署脚本"""
    deploy_script = """#!/bin/bash

# 微信机器人部署脚本

echo "🚀 开始部署微信机器人..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 设置变量
PROJECT_DIR="/opt/wechat-bot"
SERVICE_NAME="wechat-bot"

# 停止现有服务
echo "停止现有服务..."
systemctl stop $SERVICE_NAME 2>/dev/null || true

# 备份现有配置
if [ -f "$PROJECT_DIR/config.yaml" ]; then
    echo "备份现有配置..."
    cp "$PROJECT_DIR/config.yaml" "$PROJECT_DIR/config.yaml.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 安装Python依赖
echo "安装Python依赖..."
cd $PROJECT_DIR
pip3 install -r requirements.txt

# 设置权限
echo "设置文件权限..."
chown -R root:root $PROJECT_DIR
chmod +x $PROJECT_DIR/*.py

# 重新加载systemd
echo "重新加载systemd..."
systemctl daemon-reload

# 启用并启动服务
echo "启动服务..."
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# 检查服务状态
echo "检查服务状态..."
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服务启动成功"
    systemctl status $SERVICE_NAME --no-pager
else
    echo "❌ 服务启动失败"
    journalctl -u $SERVICE_NAME --no-pager -n 20
    exit 1
fi

echo "🎉 部署完成！"
echo ""
echo "📋 管理命令："
echo "  查看状态: systemctl status $SERVICE_NAME"
echo "  查看日志: journalctl -u $SERVICE_NAME -f"
echo "  重启服务: systemctl restart $SERVICE_NAME"
echo "  停止服务: systemctl stop $SERVICE_NAME"
"""
    
    try:
        with open("deploy.sh", "w") as f:
            f.write(deploy_script)
        
        # 设置执行权限
        os.chmod("deploy.sh", 0o755)
        
        print("✅ 部署脚本创建成功: deploy.sh")
        return True
        
    except Exception as e:
        print(f"❌ 部署脚本创建失败: {e}")
        return False

def create_monitoring_script():
    """创建监控脚本"""
    monitor_script = """#!/bin/bash

# 微信机器人监控脚本

SERVICE_NAME="wechat-bot"
LOG_FILE="/opt/wechat-bot/logs/monitor.log"

# 检查服务状态
check_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "$(date): 服务运行正常" >> $LOG_FILE
        return 0
    else
        echo "$(date): 服务异常，尝试重启" >> $LOG_FILE
        systemctl restart $SERVICE_NAME
        sleep 10
        
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo "$(date): 服务重启成功" >> $LOG_FILE
        else
            echo "$(date): 服务重启失败" >> $LOG_FILE
            # 发送告警邮件或其他通知
        fi
        return 1
    fi
}

# 检查日志文件大小
check_log_size() {
    LOG_DIR="/opt/wechat-bot/logs"
    MAX_SIZE=100  # MB
    
    for log_file in $LOG_DIR/*.log; do
        if [ -f "$log_file" ]; then
            size=$(du -m "$log_file" | cut -f1)
            if [ $size -gt $MAX_SIZE ]; then
                echo "$(date): 日志文件 $log_file 过大，进行轮转" >> $LOG_FILE
                mv "$log_file" "$log_file.old"
                touch "$log_file"
            fi
        fi
    done
}

# 主监控逻辑
main() {
    check_service
    check_log_size
}

main
"""
    
    try:
        with open("monitor.sh", "w") as f:
            f.write(monitor_script)
        
        os.chmod("monitor.sh", 0o755)
        
        print("✅ 监控脚本创建成功: monitor.sh")
        print("💡 建议添加到crontab: */5 * * * * /opt/wechat-bot/monitor.sh")
        return True
        
    except Exception as e:
        print(f"❌ 监控脚本创建失败: {e}")
        return False

def main():
    """主部署流程"""
    print("🤖 微信机器人云服务器部署工具")
    print("=" * 50)
    
    # 检查操作系统
    if platform.system() != "Linux":
        print("❌ 此脚本仅支持Linux系统")
        sys.exit(1)
    
    # 检查是否为root用户
    if os.geteuid() != 0:
        print("❌ 请使用root用户运行此脚本")
        sys.exit(1)
    
    print("📋 部署步骤：")
    print("1. 安装系统依赖")
    print("2. 设置项目目录")
    print("3. 创建系统服务")
    print("4. 创建部署脚本")
    print("5. 创建监控脚本")
    print("")
    
    # 确认继续
    response = input("是否继续部署？(y/N): ")
    if response.lower() != 'y':
        print("部署已取消")
        sys.exit(0)
    
    # 执行部署步骤
    steps = [
        ("安装系统依赖", install_system_dependencies),
        ("设置项目目录", setup_project_directory),
        ("创建系统服务", create_systemd_service),
        ("创建部署脚本", create_deployment_script),
        ("创建监控脚本", create_monitoring_script),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ {step_name}失败，部署中止")
            sys.exit(1)
        print(f"✅ {step_name}完成")
    
    print("\n" + "=" * 50)
    print("🎉 云服务器部署准备完成！")
    print("\n📋 下一步操作：")
    print("1. 将项目文件上传到 /opt/wechat-bot/")
    print("2. 配置 config.yaml 文件")
    print("3. 运行 ./deploy.sh 完成部署")
    print("4. 使用 systemctl status wechat-bot 检查状态")
    print("\n💡 管理命令：")
    print("  启动: systemctl start wechat-bot")
    print("  停止: systemctl stop wechat-bot")
    print("  重启: systemctl restart wechat-bot")
    print("  查看日志: journalctl -u wechat-bot -f")

if __name__ == "__main__":
    main()

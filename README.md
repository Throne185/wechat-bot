# 微信群机器人自动回复系统

一个基于微信的智能影视资源搜索机器人，支持根据剧名、演员名称自动回复相关资源信息。

## ✨ 主要功能

- 🎬 **智能搜索**: 支持剧名、演员名称的模糊搜索
- 🔗 **资源回复**: 自动回复夸克网盘和百度网盘链接
- 🛡️ **防封号策略**: 智能延迟发送、频率控制、群人数检测
- 📊 **数据管理**: 基于Excel的数据存储，支持热更新
- 💬 **多平台支持**: 支持群聊和私聊
- 🔍 **高级搜索**: 分词搜索、同义词匹配、相似度排序

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- Windows/Linux/macOS
- 微信PC版或网页版

### 2. 安装

```bash
# 克隆项目
git clone <项目地址>
cd 微信机器人

# 自动安装依赖
python install.py
```

### 3. 配置数据

将你的影视资源数据整理成Excel文件，包含以下列：

| 媒体类型 | 剧名 | 集数 | 演员名称 | 夸克网盘链接 | 百度网盘链接 |
|---------|------|------|----------|-------------|-------------|
| 电视剧 | 庆余年 | 46 | 张若昀、李沁、陈道明 | https://pan.quark.cn/s/... | https://pan.baidu.com/s/... |

保存为 `data/media_database.xlsx`

### 4. 启动机器人

```bash
python start.py
```

扫描二维码登录微信，机器人即可开始工作。

## 📋 使用说明

### 群聊使用
- @机器人 + 搜索词
- 直接发送搜索关键词
- 示例：`@机器人 庆余年` 或 `张若昀`

### 私聊使用
- 直接发送搜索词
- 示例：`庆余年` 或 `张若昀 古装`

### 特殊命令
- `帮助` - 查看使用说明
- `统计` - 查看数据统计
- `重新加载` - 重新加载Excel数据

## ⚙️ 配置说明

主要配置文件：`config.yaml`

### 安全策略配置

```yaml
security:
  # 群人数检测
  group_member_check:
    enabled: true
    threshold: 20  # 群人数超过20人时启用延迟发送
    
  # 发送频率控制
  rate_limit:
    enabled: true
    max_per_minute: 10  # 每分钟最大发送次数
    max_per_hour: 50    # 每小时最大发送次数
    
  # 延迟发送配置
  delay_send:
    enabled: true
    base_delay: 2       # 基础延迟时间(秒)
    random_delay: 3     # 随机延迟范围(秒)
    group_extra_delay: 5 # 群人数多时额外延迟(秒)
```

### 搜索配置

```yaml
search:
  similarity_threshold: 60  # 模糊搜索相似度阈值
  max_results: 10          # 最大返回结果数
  max_items_per_message: 3 # 单次发送最大条数
```

### 消息格式配置

```yaml
message_format:
  single_template: |
    🎬《{drama_name}》
    主演：{actors}
    集数：{episodes}集
    夸克：{quark_link}
    百度：{baidu_link}
```

## 🛡️ 安全机制

### 防封号策略

1. **智能延迟发送**
   - 根据群人数自动调整延迟时间
   - 随机延迟避免机器行为特征

2. **频率控制**
   - 全局发送频率限制
   - 用户请求频率限制
   - 群消息频率限制

3. **安全时间检测**
   - 避免深夜时间发送消息
   - 可配置安全发送时间段

4. **消息内容检测**
   - 过滤敏感词汇
   - 消息长度限制

### 维护安全设置

你可以通过修改 `config.yaml` 来调整安全策略：

- **降低风险**: 增加延迟时间，减少发送频率
- **提高响应**: 减少延迟时间，增加发送频率
- **群人数阈值**: 根据实际群大小调整阈值

## 📁 项目结构

```
微信机器人/
├── wechat_bot.py          # 主程序
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖列表
├── install.py            # 安装脚本
├── start.py              # 启动脚本
├── create_sample_excel.py # 示例数据生成
├── data/                 # 数据目录
│   └── media_database.xlsx
├── logs/                 # 日志目录
├── utils/                # 工具模块
│   ├── data_manager.py   # 数据管理
│   ├── search_engine.py  # 搜索引擎
│   ├── message_formatter.py # 消息格式化
│   └── security_manager.py  # 安全管理
└── plugins/              # 插件目录（预留）
```

## 🔧 高级功能

### 数据热更新
机器人运行时可以更新Excel文件，然后发送"重新加载"命令即可生效。

### 自定义搜索
支持多种搜索方式：
- 精确匹配
- 模糊搜索
- 分词搜索
- 同义词搜索

### 批量发送
当搜索结果较多时，自动分批发送，避免刷屏。

## 🌐 云服务器部署

### 部署要求
- 云服务器（推荐1核2G以上）
- Python 3.7+ 环境
- 稳定的网络连接

### 部署步骤

1. **上传项目文件**
```bash
scp -r 微信机器人/ root@62.234.185.61:/opt/
```

2. **安装依赖**
```bash
ssh root@62.234.185.61
cd /opt/微信机器人
python install.py
```

3. **配置服务**
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/wechat-bot.service
```

服务文件内容：
```ini
[Unit]
Description=WeChat Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/微信机器人
ExecStart=/usr/bin/python3 wechat_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **启动服务**
```bash
sudo systemctl enable wechat-bot
sudo systemctl start wechat-bot
sudo systemctl status wechat-bot
```

### 云服务器优势
- 24小时稳定运行
- 不占用本地资源
- 更好的网络稳定性
- 便于远程管理

## ⚠️ 注意事项

1. **账号安全**
   - 建议使用小号测试
   - 避免在重要群聊中频繁使用
   - 定期检查账号状态

2. **数据安全**
   - 定期备份Excel数据文件
   - 不要在配置文件中存储敏感信息
   - 注意网盘链接的有效性

3. **合规使用**
   - 遵守微信使用规范
   - 不要用于商业推广
   - 尊重版权，仅供学习交流

## 🐛 故障排除

### 常见问题

1. **登录失败**
   - 检查网络连接
   - 尝试重新扫码
   - 确认微信版本兼容性

2. **搜索无结果**
   - 检查Excel文件格式
   - 确认数据文件路径
   - 查看日志文件排错

3. **发送失败**
   - 检查安全策略配置
   - 确认群聊权限
   - 查看频率限制设置

### 日志查看
```bash
tail -f logs/wechat_bot.log
```

## 📞 技术支持

如有问题，请查看：
1. 项目日志文件
2. 配置文件设置
3. 网络连接状态

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

"""
机器人功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.search_engine import SearchEngine
from utils.message_formatter import MessageFormatter
from utils.security_manager import SecurityManager

def test_data_loading():
    """测试数据加载"""
    print("🔍 测试数据加载...")
    
    data_manager = DataManager()
    success = data_manager.load_excel_data()
    
    if success:
        stats = data_manager.get_stats()
        print(f"✅ 数据加载成功")
        print(f"   总剧集数: {stats.get('total_dramas', 0)}")
        print(f"   剧名关键词: {stats.get('drama_keywords', 0)}")
        print(f"   演员关键词: {stats.get('actor_keywords', 0)}")
        return True
    else:
        print("❌ 数据加载失败")
        return False

def test_search_functionality():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    data_manager = DataManager()
    if not data_manager.load_excel_data():
        print("❌ 数据加载失败，无法测试搜索")
        return False
    
    search_engine = SearchEngine(data_manager)
    
    # 测试用例
    test_queries = [
        "庆余年",
        "张若昀", 
        "胡歌",
        "古装",
        "他的玫瑰"
    ]
    
    for query in test_queries:
        print(f"\n🔎 搜索: '{query}'")
        results = search_engine.intelligent_search(query)
        
        if results:
            print(f"   找到 {len(results)} 个结果:")
            for i, result in enumerate(results[:2], 1):  # 只显示前2个
                print(f"   {i}. {result.get('drama_name', '未知')} - {result.get('actors', '未知')}")
        else:
            print("   无结果")
    
    return True

def test_message_formatting():
    """测试消息格式化"""
    print("\n🔍 测试消息格式化...")
    
    formatter = MessageFormatter()
    
    # 模拟搜索结果
    test_results = [
        {
            'drama_name': '庆余年',
            'actors': '张若昀、李沁、陈道明',
            'episodes': '46',
            'quark_link': 'https://pan.quark.cn/s/example1',
            'baidu_link': 'https://pan.baidu.com/s/example1'
        },
        {
            'drama_name': '琅琊榜',
            'actors': '胡歌、刘涛、王凯',
            'episodes': '54',
            'quark_link': 'https://pan.quark.cn/s/example2',
            'baidu_link': 'https://pan.baidu.com/s/example2'
        }
    ]
    
    messages = formatter.format_search_results(test_results, "张若昀")
    
    print("✅ 格式化结果:")
    for i, message in enumerate(messages, 1):
        print(f"\n--- 消息 {i} ---")
        print(message)
    
    return True

def test_security_manager():
    """测试安全管理器"""
    print("\n🔍 测试安全管理器...")
    
    security_manager = SecurityManager()
    
    # 测试频率限制
    test_group = "test_group_123"
    test_user = "test_user_456"
    
    print("测试频率限制...")
    for i in range(3):
        can_respond, reason = security_manager.should_respond(test_group, test_user, "测试消息")
        print(f"   第{i+1}次请求: {'允许' if can_respond else '拒绝'} - {reason}")
        
        if can_respond:
            security_manager.record_message_sent(test_group, test_user)
    
    # 测试延迟计算
    delay = security_manager.calculate_send_delay(test_group, 1)
    print(f"   计算延迟时间: {delay:.2f}秒")
    
    # 测试安全状态
    status = security_manager.get_security_status()
    print(f"   安全状态: {status}")
    
    return True

def test_integration():
    """集成测试"""
    print("\n🔍 集成测试...")
    
    try:
        # 初始化所有组件
        data_manager = DataManager()
        search_engine = SearchEngine(data_manager)
        formatter = MessageFormatter()
        security_manager = SecurityManager()
        
        # 加载数据
        if not data_manager.load_excel_data():
            print("❌ 数据加载失败")
            return False
        
        # 模拟完整的搜索流程
        query = "庆余年"
        test_group = "integration_test_group"
        test_user = "integration_test_user"
        
        print(f"模拟搜索流程: '{query}'")
        
        # 1. 安全检查
        can_respond, reason = security_manager.should_respond(test_group, test_user, query)
        if not can_respond:
            print(f"❌ 安全检查失败: {reason}")
            return False
        
        # 2. 执行搜索
        results = search_engine.intelligent_search(query)
        if not results:
            print("❌ 搜索无结果")
            return False
        
        # 3. 格式化消息
        messages = formatter.format_search_results(results, query)
        if not messages:
            print("❌ 消息格式化失败")
            return False
        
        # 4. 计算延迟
        delay = security_manager.calculate_send_delay(test_group, len(messages))
        
        # 5. 记录发送
        security_manager.record_message_sent(test_group, test_user)
        
        print("✅ 集成测试成功")
        print(f"   搜索结果: {len(results)} 个")
        print(f"   消息数量: {len(messages)} 条")
        print(f"   发送延迟: {delay:.2f} 秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🤖 微信机器人功能测试")
    print("=" * 50)
    
    # 测试项目
    tests = [
        ("数据加载", test_data_loading),
        ("搜索功能", test_search_functionality),
        ("消息格式化", test_message_formatting),
        ("安全管理器", test_security_manager),
        ("集成测试", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！机器人功能正常")
        print("\n📋 下一步:")
        print("1. 运行 python start.py 启动机器人")
        print("2. 扫码登录微信")
        print("3. 在群聊或私聊中测试搜索功能")
    else:
        print("⚠️ 部分测试失败，请检查配置和数据文件")
        print("\n🔧 排查建议:")
        print("1. 检查 config.yaml 配置文件")
        print("2. 确认 data/media_database.xlsx 文件存在")
        print("3. 检查所有依赖是否正确安装")

if __name__ == "__main__":
    main()

"""
创建示例Excel文件
"""
import pandas as pd
import os

def create_sample_excel():
    """创建示例Excel文件"""
    
    # 示例数据
    data = [
        ["电视剧", "庆余年", 46, "张若昀、李沁、陈道明", "https://pan.quark.cn/s/dce2b4ab906e", "https://pan.baidu.com/s/1rAsbcpaUw1tUopqDz7fCAA?pwd=8888"],
        ["电视剧", "琅琊榜", 54, "胡歌、刘涛、王凯", "https://pan.quark.cn/s/abc123def456", "https://pan.baidu.com/s/1abc123def456?pwd=1234"],
        ["电影", "流浪地球", 1, "吴京、屈楚萧、李光洁", "https://pan.quark.cn/s/xyz789uvw012", "https://pan.baidu.com/s/1xyz789uvw012?pwd=5678"],
        ["电视剧", "甄嬛传", 76, "孙俪、陈建斌、蔡少芬", "https://pan.quark.cn/s/zhen123huan456", "https://pan.baidu.com/s/1zhen123huan456?pwd=9999"],
        ["电视剧", "三生三世十里桃花", 58, "杨幂、赵又廷、于朦胧", "https://pan.quark.cn/s/sansheng123", "https://pan.baidu.com/s/1sansheng123?pwd=0000"],
        ["电视剧", "步步惊心", 35, "刘诗诗、吴奇隆、郑嘉颖", "https://pan.quark.cn/s/bubu123jingxin", "https://pan.baidu.com/s/1bubu123jingxin?pwd=1111"],
        ["电视剧", "仙剑奇侠传三", 37, "胡歌、杨幂、刘诗诗", "https://pan.quark.cn/s/xianjian3", "https://pan.baidu.com/s/1xianjian3?pwd=2222"],
        ["电视剧", "还珠格格", 48, "赵薇、林心如、苏有朋", "https://pan.quark.cn/s/huanzhu123", "https://pan.baidu.com/s/1huanzhu123?pwd=3333"],
        ["电视剧", "延禧攻略", 70, "吴谨言、秦岚、聂远", "https://pan.quark.cn/s/yanxi123", "https://pan.baidu.com/s/1yanxi123?pwd=4444"],
        ["电视剧", "如懿传", 87, "周迅、霍建华、张钧甯", "https://pan.quark.cn/s/ruyi123", "https://pan.baidu.com/s/1ruyi123?pwd=5555"],
        ["电视剧", "他的玫瑰与寒霜", 60, "闵星翰、林琦婷、李曾", "https://pan.quark.cn/s/dce2b4ab906e", "https://pan.baidu.com/s/1rAsbcpaUw1tUopqDz7fCAA?pwd=8888"],
        ["电影", "战狼2", 1, "吴京、弗兰克·格里罗、吴刚", "https://pan.quark.cn/s/zhanlang2", "https://pan.baidu.com/s/1zhanlang2?pwd=6666"],
        ["电影", "红海行动", 1, "张译、黄景瑜、海清", "https://pan.quark.cn/s/honghai123", "https://pan.baidu.com/s/1honghai123?pwd=7777"],
        ["电视剧", "长安十二时辰", 48, "易烊千玺、雷佳音、周一围", "https://pan.quark.cn/s/changan12", "https://pan.baidu.com/s/1changan12?pwd=8888"],
        ["电视剧", "陈情令", 50, "肖战、王一博、孟子义", "https://pan.quark.cn/s/chenqing123", "https://pan.baidu.com/s/1chenqing123?pwd=9999"]
    ]
    
    # 创建DataFrame
    columns = ["媒体类型", "剧名", "集数", "演员名称", "夸克网盘链接", "百度网盘链接"]
    df = pd.DataFrame(data, columns=columns)
    
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    
    # 保存为Excel文件
    excel_file = "data/media_database.xlsx"
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"示例Excel文件已创建: {excel_file}")
    print(f"包含 {len(data)} 条示例数据")
    
    return excel_file

if __name__ == "__main__":
    create_sample_excel()

import requests
import os

#下载最新的VIX指数
# 定义文件下载地址
url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"

# 获取文件名
file_name = os.path.basename(url)

# 拼接保存路径
save_path = os.path.join("stock_data", file_name)

# 发送请求并下载文件
response = requests.get(url)
if response.status_code == 200:
    # 创建保存目录（如果不存在）
    os.makedirs("stock_data", exist_ok=True)
    
    # 保存文件到指定路径
    with open(save_path, "wb") as f:
        f.write(response.content)
        
    print("文件下载成功，保存路径为:", save_path)
else:
    print("文件下载失败")

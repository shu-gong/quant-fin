import pandas as pd

# 读取AAPL.csv文件
file_path = "./stock_data/AAPL.csv" # 文件路径
df = pd.read_csv(file_path)

# 输出读取的数据量
print("成功读取AAPL.csv文件，数据已存入名为df的dataframe中。")
print("数据量：")
print(df.shape)

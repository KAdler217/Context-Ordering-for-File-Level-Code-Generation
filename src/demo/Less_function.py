import os
import json

# 指定文件夹名称
folder_name = "sheer"

# 定义大小限制（10KB）
size_limit = 10 * 1024  # 10KB = 10 * 1024 字节

# 获取文件夹中的所有文件名
file_names = os.listdir(folder_name)

# 筛选大小小于 10KB 的文件
small_files = []

for file_name in file_names:
    file_path = os.path.join(folder_name, file_name)

    # 确保是一个文件而不是目录
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)

        # 检查文件大小是否小于 10KB
        if file_size < size_limit:
            small_files.append({
                "file_name": file_name,
                "file_size": file_size
            })

# 将结果写入 JSONL 文件
output_file = "CoderEval4Java_small.jsonl"
with open(output_file, 'w', encoding='utf-8') as f:
    for file_info in small_files:
        json_str = json.dumps(file_info, ensure_ascii=False)
        f.write(json_str + "\n")

print(f"已将小于 10KB 的文件信息保存到 {output_file}")
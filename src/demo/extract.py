def extract_specific_lines(input_path, output_path, target_indices):
    """
    从JSONL文件中提取特定索引的行并保存为新文件

    参数:
    input_path (str): 输入JSONL文件路径
    output_path (str): 输出JSONL文件路径
    target_indices (list): 需要提取的索引列表
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        # 筛选指定索引的行
        selected_lines = [lines[i] for i in target_indices if i < len(lines)]

        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(selected_lines)

        print(f"成功提取 {len(selected_lines)} 行数据到 {output_path}")

    except FileNotFoundError:
        print(f"错误：文件 {input_path} 未找到")
    except IndexError:
        print("警告：部分索引超出文件行数范围，已自动跳过")
    except Exception as e:
        print(f"发生未知错误：{str(e)}")


# 使用示例
input_file = "CoderEval4Java_31K.jsonl"
output_file = "CoderEval4Java_9.jsonl"
target_indices = [2, 11, 12, 17, 22, 26, 29, 30, 31, 32, 33, 36, 37, 38, 39, 42, 44, 59, 64, 65, 68, 69, 70, 71, 73, 74, 75, 76, 78, 80, 82, 86, 88, 90, 94, 97, 98, 100, 103, 104, 105, 109, 113, 114, 116, 125, 126, 129, 131, 132, 134, 139, 149, 150, 151, 153, 154, 156, 157, 161, 162, 166, 170, 174, 175, 178, 181, 184, 186, 192, 193, 201]


extract_specific_lines(input_file, output_file, target_indices)


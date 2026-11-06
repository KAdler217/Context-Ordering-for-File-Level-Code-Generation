import json
import os
from transformers import AutoTokenizer


def count_tokens(text, delimiter=' '):
    """
    计算文本中的token数量。
    这里假设token是由空格分隔的单词，但你可以根据需要修改分隔符。
    """
    model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # 使用 tokenizer 编码文本，但不截断也不添加特殊 token
    encoded_ref = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    return len(encoded_ref)


def filter_jsonl(input_file, output_file, max_tokens=15000):
    """
    筛选JSONL文件，去除file_content字段中token数量超过max_tokens的数据。
    """
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            try:
                data = json.loads(line)

                if 'file_content' in data and len((data['file_content']).encode('utf-8')) <= max_tokens:
                    outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
            except json.JSONDecodeError:
                # 如果遇到无法解析的JSON行，可以选择记录错误或跳过该行
                # 这里选择打印错误并跳过该行
                print(f"Error decoding JSON: {line.strip()}")


# 使用示例
input_jsonl_file = 'CoderEval4Java.jsonl'  # 输入的JSONL文件路径
output_jsonl_file = 'CoderEval4Java_15K.jsonl'  # 输出的JSONL文件路径

filter_jsonl(input_jsonl_file, output_jsonl_file)
import os
import json
from pathlib import Path


def parse_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into solution and result parts
    parts = content.split('result:\n')
    if len(parts) != 2:
        raise ValueError(f"Unexpected format in file: {file_path}")

    solution_part = parts[0].strip().replace('solution:\n', '')
    result_part = parts[1].strip()

    # Check if result part is empty or has fewer than 5 lines including "result:" line
    result_lines = ['result:\n'] + [line + '\n' for line in result_part.split('\n')]
    # if len(result_lines) < 5:
    #     raise ValueError(f"Result section too short (less than 5 lines) in file: {file_path}")

    return {
        "solution": solution_part,
        "result": ''.join(result_lines)
    }


def write_to_jsonl(jsonl_file_path, data):
    with open(jsonl_file_path, 'a', encoding='utf-8') as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')


def main(input_folder, output_file):
    input_folder_path = Path(input_folder)
    output_file_path = Path(output_file)

    # Clear the output file if it exists
    if output_file_path.exists():
        output_file_path.unlink()

    all_data = []

    for txt_file in input_folder_path.glob('*.txt'):
        try:
            parsed_data = parse_txt_file(txt_file)
            all_data.append(parsed_data)
        except Exception as e:
            print(f"Error processing file {txt_file}: {e}")
            continue

    write_to_jsonl(output_file_path, all_data)
    print(f"Data has been written to {output_file}")


if __name__ == "__main__":
    input_folder = 'perm_hlh_2t_input'  # 输入文件夹路径 perm_5_emb_input
    output_file = 'DeepSeekV3_perm_hlh_2t_input.jsonl'  # 输出JSONL文件路径 DeepSeekV3_perm_5_emb.jsonl
    main(input_folder, output_file)
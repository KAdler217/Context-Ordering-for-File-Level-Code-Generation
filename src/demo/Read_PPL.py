import json
import os
import re
import shutil

from chutes import invoke_chute1

dataset_path = 'CoderEval4Java_31K.jsonl'

def main():
    perm_5_dir = 'perm_h4_2t'
    result_dir = 'perm_h4_2t_result'

    # 确保结果目录存在
    os.makedirs(result_dir, exist_ok=True)
    index = 0
    # 0,5,8,20,21,33,53,57,79,83,84,86,87,89,98,107,108,110,120,126,130,133,137,139,157,172,176,
    # specified_folders = ['line_1','line_13','line_44','line_105','line_108','line_129','line_133','line_137','line_152','line_168','line_200','line_201']
    folder_path = 'perm_h4_2t_result'  # 替换为  实际文件夹路径
    a = find_missing_indices(folder_path)
    # a = [0,5,8,20,21,33,53,57,79,83,84,86,87,89,98,107,108,110,120,126,130,133,137,139,157,172,176]
    specified_folders = [f'line_{index}' for index, _ in enumerate(a)]
    # 遍历 perm_5 文件夹中的每个子文件夹
    for subfolder in specified_folders:
        subfolder_path = os.path.join(perm_5_dir, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        # 初始化最低分数和对应文件路径
        min_score = float('inf')
        min_score_file = None
        func_name = None
        with (open(dataset_path, 'r', encoding='utf-8') as file):
            lines = file.readlines()
            index = int(subfolder.split('_')[1])  # 假设子文件夹名为 lineX 格式
            print(index)
            if 0 <= index < len(lines):
                json_line = lines[index].strip()
                json_obj = json.loads(json_line)
                print(json_obj)
                func_name = json_obj['func_name']
        print(func_name)

        # 遍历子文件夹中的每个文件
        for file_name in os.listdir(subfolder_path):

            if file_name[0].isdigit():

                file_path = os.path.join(subfolder_path, file_name)
                print(file_path)
                with (open(file_path, 'r', encoding='utf-8') as file):
                    content = file.read()
                    score = invoke_chute1(content,func_name,1)
                    print(score)
                    if score < min_score:
                        min_score = score
                        min_score_file = file_path
        print(min_score)

        # 如果找到了最低分数的文件，则将其复制到结果文件夹中并重命名
        if min_score_file:
            new_file_name = subfolder + '.txt'
            new_file_path = os.path.join(result_dir, new_file_name)
            shutil.copy2(min_score_file, new_file_path)


def find_missing_indices(folder_path):
    # 获取所有匹配的文件
    files = os.listdir(folder_path)
    pattern = re.compile(r'line_(\d+)\.txt')

    existing_indices = set()
    for file in files:
        match = pattern.match(file)
        if match:
            index = int(match.group(1))
            existing_indices.add(index)

    # 完整索引集合
    full_indices = set(range(202))  # 0-10

    # 缺失的索引
    missing_indices = sorted(full_indices - existing_indices)
    return missing_indices

if __name__ == "__main__":
    main()

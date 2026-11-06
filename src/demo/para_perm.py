import os
import shutil
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from chutes import invoke_chute1, invoke_chute2, invoke_chute3, invoke_chute4


# 示例打分函数
def score_function1(content, func_name):
    # 这是一个示例打分函数1，你需要根据实际需求实现具体的打分逻辑
    return invoke_chute1(content, func_name, 0)


def score_function2(content, func_name):
    # 这是一个示例打分函数2，你需要根据实际需求实现具体的打分逻辑
    return invoke_chute2(content, func_name, 1)


def score_function3(content, func_name):
    # 这是一个示例打分函数3，你需要根据实际需求实现具体的打分逻辑
    return invoke_chute3(content, func_name, 2)


def score_function4(content, func_name):
    # 这是一个示例打分函数4，你需要根据实际需求实现具体的打分逻辑
    return invoke_chute4(content, func_name, 3)


def process_subfolder(subfolder, dataset_path, result_dir,score_func):
    subfolder_path = os.path.join(dataset_path, subfolder)
    if not os.path.isdir(subfolder_path):
        return

        # 读取 1.jsonl 文件的相应行
    func_name = None
    with open(os.path.join(dataset_path, 'CoderEval4Java_31K.jsonl'), 'r', encoding='utf-8') as file:
        lines = file.readlines()
        index = int(subfolder.split('_')[1])  # 假设子文件夹名为 lineX 格式
        if 0 <= index < len(lines):
            json_line = lines[index].strip()
            json_obj = json.loads(json_line)

            func_name = json_obj['func_name']
    print(func_name)
    # 初始化最低分数和对应文件路径
    min_score = float('inf')
    min_score_file = None

    # 遍历子文件夹中的每个文件
    for file_name in os.listdir(subfolder_path):
        if file_name[0].isdigit():
            file_path = os.path.join(subfolder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                score = score_func(content, func_name)
                print(f"File: {file_path}, Score: {score}")
                if score < min_score:
                    min_score = score
                    min_score_file = file_path
                new_name = 'ppl.txt'
                file_path1 = os.path.join(subfolder_path, new_name)
                with open(file_path1, 'a', encoding='utf-8') as file:
                    # 构造要写入的内容
                    content = f"File Name: {file_name} Score: {score}\n"
                    # 写入内容到文件
                    file.write(content)

    # 将最低分数的文件复制到结果文件夹中并重命名
    if min_score_file:
        new_file_name = subfolder + '.txt'
        new_file_path = os.path.join(result_dir, new_file_name)
        shutil.copy2(min_score_file, new_file_path)
        print(f"Copied {min_score_file} to {new_file_path}")


def main():
    dataset_path = 'perm_hlh_2t'  # 替换为你的数据集目录路径
    perm_5_dir = 'perm_hlh'
    result_dir = 'perm_hlh_2t_result'

    # 确保结果目录存在
    os.makedirs(result_dir, exist_ok=True)

    # 定义四个 func_name 和对应的打分函数
    # func_names = ['func1', 'func2', 'func3', 'func4']
    score_functions = [score_function1, score_function2, score_function3, score_function4]

    # 使用 ThreadPoolExecutor 并行处理四个子文件夹
    with ThreadPoolExecutor() as executor:
        futures = []
        for j in range(51):
            if j >= 0:
                for i in range(4):
                    subfolder = f'line_{i + 4 * j}'
                    futures.append(
                        executor.submit(process_subfolder, subfolder, dataset_path, result_dir,score_functions[i]))

                # 等待所有任务完成
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()



import json
import os
import sys
import time
import re

import openai
import tree_sitter
from openai import OpenAI
import tree_sitter_java as tsjv
from tree_sitter import Language, Parser

from ABC_order import read_file_in_ABC_order
# from Perplexity import get_perplexity

JAVA_LANGUAGE = tree_sitter.Language(tsjv.language())
parser = Parser(JAVA_LANGUAGE)
file_path = 'CoderEval4Java_31K.jsonl'
cpp_query_text = '''
( method_declaration
	name: (identifier) @1
)

'''
query = JAVA_LANGUAGE.query(cpp_query_text)

bleu_score = 0
codebleu_score = 0
sentence_BERT_score = 0
count = 0


def read_first_file_content_of_jsonl(file_path, isABC):
    with (open(file_path, 'r', encoding='utf-8') as file):
        global bleu_score
        global codebleu_score
        global sentence_BERT_score
        global count
        func_lists = []
        for index, (line) in enumerate(file):
            if index >= 169:
                if line.strip():  # 确保行不为空或仅包含空白字符

                    first_json_obj = json.loads(line)
                    func_name = first_json_obj['func_name']
                    print(func_name)
                    docstring = first_json_obj['docstring']
                    func_code = first_json_obj['func_code']

                    func_body = first_json_obj['func_body']

                    lines = func_code.split('\n')

                    # 提取第一行和最后一行
                    first_line = lines[0]
                    last_line = lines[-1]

                    # 替换func_code中的func_body部分为空格
                    func_null = first_line + " \n" + last_line
                    global prefix_code
                    global suffix_code
                    base_string = ""

                    if isABC:
                        # read_files_in_directories(func_name,index)

                        prefix_code = ""
                        base_string = "DeepSeekV3"
                        suffix_code = read_codes("perm_5_emb_result", index, func_null, docstring, base_string, func_code)

                        # func_num = read_file_in_ABC_order(file_path,index)
                        # if func_num < 10:
                        #     func_lists.append(index)
                        #     print(func_num)

                        # folder_name = 'permutations'
                        # codes = read_codes_from_folder(folder_name)
                        # base_string = "PERM(test)_Qwen_32B"
                        # for i, (prefix, suffix) in enumerate(codes, start=1):
                        #   if i > 22:
                        #     prefix_code, suffix_code = prefix,suffix
                        #
                        #     content = prefix_code + "\n HELLO \n" + suffix_code
                        #     if False:
                        #         func = ""
                        #     else:
                        #         func = train(func_null, docstring, prefix_code, suffix_code)
                        #         time.sleep(25)
                        #
                        #     folder_path = os.path.join("test_function")
                        #     filename = os.path.join(folder_path, f"{base_string}_{i}.txt")
                        #     folder_path1 = os.path.join("Input")
                        #     filename1 = os.path.join(folder_path1, f"{base_string}_{index}.txt")
                        #
                        #     first_line_of_func_code = func_code.splitlines()[0]
                        #     last_line_of_func_code = func_code.splitlines()[-1]
                        #
                        #     # res = (
                        #     #         first_line_of_func_code + "\n" + func + "\n" + last_line_of_func_code  # 插入最后一行
                        #     # )
                        #     res = func
                        #     # print(res)
                        #     with open(filename, 'w', encoding='utf-8') as file1:
                        #         file1.write("solution:\n" + func_code + "\n result:\n" + res)
                        #
                        #     with open(filename1, 'w', encoding='utf-8') as file2:
                        #         file2.write(content)
                        #     print(index)



                    # if isABC:
                    #     prefix_code, suffix_code = read_file_in_Embedding_order(file_path, index)
                    #     base_string = "Embedding(chlhc)_with_llama"
                    else:
                        file_content = first_json_obj['file_content']  # 获取字段值
                        tree = parser.parse(bytes(file_content, "utf8"))
                        root_node = tree.root_node
                        capture = query.captures(root_node)
                        # 打印函数名
                        # showName(capture['1'],file_content)

                        start_line = get_start_lines(capture, file_content, func_name, func_code)

                        # prefix_line = start_line - len(docstring.splitlines())
                        # print(len(docstring.splitlines()))
                        # suffix_line = start_line + len(func_code.splitlines())

                        prefix_line = start_line + 1
                        suffix_line = start_line + len(func_code.splitlines()) - 1

                        lines = file_content.splitlines()
                        prefix = lines[0:prefix_line]
                        suffix = lines[suffix_line:]

                        prefix_code = '\n'.join(prefix)
                        suffix_code = '\n'.join(suffix)
                        # print(is_string_too_large(prefix_code))
                        # print(is_string_too_large(suffix_code))
                        base_string = "DeepSeekV3"
                    # train_content(func_null, docstring, prefix_code, suffix_code, base_string)


def train_content(func_null, docstring, prefix_code, suffix_code, base_string, index, func_code):
    content = prefix_code + "\n HELLO \n" + suffix_code

    if False:
        func = ""
    else:
        func = train(func_null, docstring, prefix_code, suffix_code)
        time.sleep(25)

    folder_path = os.path.join("perm_5_emb_input")
    filename = os.path.join(folder_path, f"{base_string}_{index}.txt")
    folder_path1 = os.path.join("Input")
    filename1 = os.path.join(folder_path1, f"{base_string}_{index}.txt")

    first_line_of_func_code = func_code.splitlines()[0]
    last_line_of_func_code = func_code.splitlines()[-1]
    res = func
    # print(res)
    with open(filename, 'w', encoding='utf-8') as file1:
        file1.write("solution:\n" + func_code + "\n result:\n" + res)

    with open(filename1, 'w', encoding='utf-8') as file2:
        file2.write(content)
    print(index)


def read_files_in_directories(func_name, index, base_path='permutations'):
    # 遍历从 line_0 到 line_71 的文件夹
    # for i in range(72):
    #     if i >= 6:
    directory_name = f'line_{index}'
    directory_path = os.path.join(base_path, directory_name)

    if os.path.isdir(directory_path):
        # 获取文件夹中的所有文件，并按文件名排序
        files = os.listdir(directory_path)

        # 排除最后一个文件
        files_to_read = files
        start_time = time.time()
        # 每个文件夹
        max_p = []

        txt_name = "f50_tokens.txt"
        infile_path = os.path.join(directory_path, txt_name)
        for index1, (file_name) in enumerate(files_to_read):
            # if index1 > 4:
            if file_name[0].isdigit():
                file_path = os.path.join(directory_path, file_name)

                if os.path.isfile(file_path):
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # p = get_perplexity(content, func_name)
                        max_p.append(p)
                    with open(infile_path, 'a', encoding='utf-8') as file:
                        file.write(f"{p}" + "\n")
                        print(index1)

        max_line = min(max_p)
        max_index = max_p.index(max_line)
        print(max_line, max_index)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"代码执行时间: {execution_time:.6f} 秒")


def extract_index(file_name):
    # 使用正则表达式提取 'line_' 后面的数字
    match = re.search(r'line_(\d+)', file_name)
    if match:
        return int(match.group(1))
    return float('inf')  # 如果没有匹配到，返回一个很大的数，确保这些文件排在最后


def read_codes(folder_name, index, func_null, docstring, base_string, func_code):
    # 获取文件夹中的所有文件名，并按字母顺序排序
    file_names = os.listdir(folder_name)

    # 限制读取的文件数量为前 24 个
    max_files = 202

    # 读取前 24 个文件的内容
    for i, file_name in enumerate(file_names):
        file_id = extract_index(file_name)
        if file_id == index:

            file_path = os.path.join(folder_name, file_name)
            print(file_path)
            # 确保是一个文件而不是目录
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    prefix_code = ""
                    suffix_code = content
                    train_content(func_null, docstring, prefix_code, suffix_code, base_string, index, func_code)

    return content


def read_codes_from_folder(folder_name):
    # 获取文件夹中所有文件的列表
    files = sorted([f for f in os.listdir(folder_name) if f.endswith('.txt')],
                   key=lambda x: int(re.search(r'\d+', x).group()))

    codes = []

    for file_name in files:
        file_path = os.path.join(folder_name, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 使用正则表达式匹配 prefix: 和 suffix: 后面的内容
        prefix_match = re.search(r'prefix:\n(.*?)(?=\nsuffix:|\Z)', content, re.DOTALL)
        suffix_match = re.search(r'suffix:\n(.*?)(?=\n|\Z)', content, re.DOTALL)

        if prefix_match and suffix_match:
            prefix_content = prefix_match.group(1).strip()
            suffix_content = suffix_match.group(1).strip()
            codes.append((prefix_content, suffix_content))
        else:
            print(f"Warning: File {file_name} does not match the expected format.")

    return codes


def showName(func_name, file_content):
    func_name_lists = []
    for node in func_name:
        # for node in node_list:
        start_point = node.start_point
        end_point = node.end_point

        line_number, column_number = start_point

        # 提取所有函数签名
        extracted_string = extract_string_from_content(file_content, start_point, end_point)
        tuple = (extracted_string, line_number)
        func_name_lists.append(tuple)
    func_name_lists = sorted(func_name_lists, key=lambda x: x[1])
    for f in func_name_lists:
        print(f[0] + ' ')


# 定义一个函数来从file_content中提取字符串
def extract_string_from_content(file_content, start_point, end_point):
    line_number, column_number = start_point
    end_line_number, end_column_number = end_point

    # 分割文件内容到行
    lines = file_content.split('\n')
    start_line = lines[line_number]
    extracted_string = start_line[column_number:end_column_number if end_line_number == line_number else None]
    # 如果结束点不在同一行，则需要添加后续行的内容
    if end_line_number != line_number:
        pass
    return start_line


def get_start_lines(capture, file_content, func_name, func_code):
    # 遍历字典并提取每个节点的字符串
    match_line = func_code.splitlines()[0]
    if match_line == "    @Override":
        match_line = func_code.splitlines()[1]
    print(match_line)

    for key, node_list in capture.items():
        for node in node_list:
            start_point = node.start_point
            end_point = node.end_point
            line_number, column_number = start_point

            # 提取字符串
            extracted_string = extract_string_from_content(file_content, start_point, end_point)

            # 按行提取字符串，避免重名函数
            if extracted_string == match_line:
                print(line_number)
                return line_number
            else:
                return line_number + 1


def train(func_name, docstring, prefix_code, suffix_code):
    try:
        client = OpenAI(
            api_key=os.environ.get("LLM_API_KEY", ""),  # 从https://cloud.siliconflow.cn/account/ak获取
            base_url="https://api.siliconflow.cn/v1"
        )
        messages = [
            {"role": "user",
             "content": "这是该函数的上下文" + prefix_code + suffix_code + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"},
        ]

        response = client.chat.completions.create(
            # client,
            model="deepseek-ai/DeepSeek-V3",
            messages=messages,
            stream=True,
            temperature=0.2,
        )

        ans = ''
        for chunk in response:
            ans += chunk.choices[0].delta.content
        lines = ans.split('\n')
        ans = lines[1:-1]  # 提取第二行到倒数第二行的内容（不包括第一行和最后一行）
        ans = '\n'.join(ans)


    except openai.BadRequestError as e:
        # print(f"BadRequestError: {e.message}")  # 注意：根据您的库版本，访问错误信息的方式可能有所不同
        ans = ''

        return ans  # 或者返回其他表示错误的值
    return ans


if __name__ == '__main__':
    read_first_file_content_of_jsonl(file_path, True)

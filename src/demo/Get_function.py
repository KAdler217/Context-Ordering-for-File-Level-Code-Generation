import json
import os

import numpy as np
import tree_sitter
from sklearn.metrics.pairwise import cosine_similarity
from tree_sitter import Language, Parser
import tree_sitter_java as tsjv

from Text_embedding import get_embedding

JAVA_LANGUAGE = tree_sitter.Language(tsjv.language())
parser = Parser(JAVA_LANGUAGE)
file_path = 'CoderEval4Java_31K.jsonl'
cpp_query_text = '''

( method_declaration
	name: (identifier) @1
	body: (block) @2
)
( block_comment )@3
( class_declaration)@4

'''
query = JAVA_LANGUAGE.query(cpp_query_text)


def read_file_to_get_function(file_path, num):
    with open(file_path, 'r', encoding='utf-8') as file:
        # for line in file:
        lines = [next(file) for _ in range(202)]
        line = lines[num]
        if line.strip():
            first_json_obj = json.loads(line)
            file_content = first_json_obj['file_content']  # 获取字段值
            func_name = first_json_obj['func_name']
            docstring = first_json_obj['docstring']
            func_code = first_json_obj['func_code']
            print(func_name)

            tree = parser.parse(bytes(file_content, "utf8"))
            root_node = tree.root_node
            capture = query.captures(root_node)

            #保留第一个函数注释（prefix_line）前面的所有内容，分隔符为prefix_num
            name_count, funcname_list,target_called = get_start_lines(file_content,
                                                        capture['2'],
                                                        capture['1'],
                                                        capture['3'],
                                                        capture['4'],
                                                        func_name)

            tree = parser.parse(bytes(func_code, "utf8"))
            root_node = tree.root_node
            function_calls = traverse_and_extract_function_calls(root_node)  #调用别人
            invocated = 0  # 被调
            invocate = 0
            target_call = []
            # 他调用的
            for f in function_calls:
                for n in funcname_list:
                    if f == n[0]:
                        target_call.append(f)

            return target_call, target_called


def get_start_lines(file_content, block, func_name, comment, classbody, signature):
    func_name_lists = []
    block_lists = []
    classbody_lists = []
    # 遍历字典并提取每个节点的字符串
    for node in func_name:
        # for node in node_list:
        start_point = node.start_point
        end_point = node.end_point

        line_number, column_number = start_point

        # 提取所有函数签名
        extracted_string = extract_string_from_content(file_content, start_point, end_point)
        tuple = (extracted_string, line_number)
        func_name_lists.append(tuple)
    # 提取函数body范围
    for node in block:
        # for node in node_list:
        start_point = node.start_point
        end_point = node.end_point

        line_number, column_number = start_point
        end_line_number, end_column_number = end_point

        # 提取所有函数签名

        tuple = [line_number, end_line_number]
        block_lists.append(tuple)
        # 提取注释范围
    for node in classbody:
        # for node in node_list:
        start_point = node.start_point
        end_point = node.end_point

        line_number, column_number = start_point
        end_line_number, end_column_number = end_point

        # 提取所有函数签名

        tuple = (line_number, end_line_number)
        classbody_lists.append(tuple)

    block_lists = sorted(block_lists, key=lambda x: x[1])
    func_name_lists = sorted(func_name_lists, key=lambda x: x[1])
    combined_triplets = []
    prefix = 0
    class_index = 0

    for list1, list2 in zip(block_lists, func_name_lists):
        # 提取第一个三元组的第一个元素和第二个三元组的后两个元素（函数名，注释起，函数尾，函数头）
        new_triplet = (list2[0], list1[0], list1[1] + 1, list2[1])
        # 将新三元组添加到列表中
        combined_triplets.append(new_triplet)

    for index, (list1) in enumerate(combined_triplets):
        if list1[0] == signature:
            prefix = index
    t = combined_triplets[prefix]  # 目标函数

    # 确定在哪个类里面
    for index, (interval) in enumerate(classbody_lists):
        if t[1] >= interval[0] and t[2] <= interval[1]:
            class_index = index

    # 确定类内的所有代码块
    covered_intervals = []
    s = classbody_lists[class_index]
    for index, (interval) in enumerate(combined_triplets):
        if s[0] <= interval[1] and s[1] >= interval[2]:
            covered_intervals.append(interval)
    lines = file_content.splitlines()

    name_count = []
    target_called = []
    for i in covered_intervals:
        func = lines[i[1]:i[2]]
        JAVA_LANGUAGE = tree_sitter.Language(tsjv.language())
        parser = Parser(JAVA_LANGUAGE)
        func = '\n'.join(func) + '\n'
        tree = parser.parse(bytes(func, "utf8"))
        root_node = tree.root_node
        function_calls = traverse_and_extract_function_calls(root_node)
        count = 0
        for f in function_calls:
            if f == signature:
                target_called.append(f)
                count = count + 1
        name_count.append(count)

    return name_count, func_name_lists,target_called

    # 类内代码块,插入起始行，目标函数序号，结束行


def extract_string_from_content(file_content, start_point, end_point):
    line_number, column_number = start_point
    end_line_number, end_column_number = end_point

    # 分割文件内容到行
    lines = file_content.split('\n')

    # 获取起始行和结束行
    start_line = lines[line_number]

    # 提取起始行中的子字符串
    extracted_string = start_line[column_number:end_column_number if end_line_number == line_number else None]

    # 如果结束点不在同一行，则需要添加后续行的内容（这里简化处理，只处理同一行的情况）
    if end_line_number != line_number:
        pass
    return extracted_string


def traverse_and_extract_function_calls(node):
    function_calls = []  # 用于存储函数调用的列表

    # 检查当前节点是否是函数调用节点
    if node.type == 'method_invocation':  # 或其他表示函数调用的类型名称
        function_call = ''
        for child in node.children:
            if child.type == 'identifier':
                # 提取函数调用信息
                function_call = str(child.text, 'utf-8')

        function_calls.append(function_call)

    # 递归遍历子节点
    for child in node.children:
        function_calls.extend(traverse_and_extract_function_calls(child))

    return function_calls


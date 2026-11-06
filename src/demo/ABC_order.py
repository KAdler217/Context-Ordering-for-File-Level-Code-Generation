import json
import os

import tree_sitter
from tree_sitter import Language, Parser
import tree_sitter_java as tsjv

JAVA_LANGUAGE = tree_sitter.Language(tsjv.language())
parser = Parser(JAVA_LANGUAGE)
file_path = 'CoderEval4Java.jsonl'
cpp_query_text = '''

( method_declaration
	name: (identifier) @1
	body: (block) @2
)
( block_comment )@3
( class_declaration)@4

'''
query = JAVA_LANGUAGE.query(cpp_query_text)


def read_file_in_ABC_order(file_path, num):
    with open(file_path, 'r', encoding='utf-8') as file:
        # for line in file:
        lines = [next(file) for _ in range(202)]
        line = lines[num]
        if line.strip():

            first_json_obj = json.loads(line)
            file_content = first_json_obj['file_content']  # 获取字段值
            func_name = first_json_obj['func_name']
            # docstring = first_json_obj['docstring']
            # func_code = first_json_obj['func_code']
            # print(func_name)

            tree = parser.parse(bytes(file_content, "utf8"))
            root_node = tree.root_node
            capture = query.captures(root_node)

            #保留第一个函数注释（prefix_line）前面的所有内容，分隔符为prefix_num
            block_lists, prefix_line, prefix_num, end_line,name_line = get_start_lines(file_content, capture['2'], capture['1'],
                                                                             capture['3'], capture['4'], func_name)
            # print(block_lists)

            # lines = file_content.splitlines()
            #
            # prefix = lines[0:prefix_line - 1]
            # prefix_code = '\n'.join(prefix)
            #
            # suffix = lines[end_line:]
            # suffix_code = '\n'.join(suffix)
            #
            # full_code_pre = ""
            # full_code_suf = ""
            # full_code_pre += prefix_code
            #
            # for index, (item) in enumerate(block_lists):
            #     if index < prefix_num:
            #         line = lines[item[1]:item[2]]
            #         new_code = '\n'.join(line) + '\n'
            #         full_code_pre += new_code
            #     if index == prefix_num:
            #         line1 = lines[name_line]
            #         print(line1)
            #         full_code_pre += line1
            #         full_code_suf += '    }'
            #
            #     if index > prefix_num:
            #         line = lines[item[1]:item[2]]
            #         new_code = '\n'.join(line) + '\n'
            #         full_code_suf += new_code
            #
            # full_code_suf += suffix_code
            # print(full_code)

            return len(block_lists)


def get_start_lines(file_content, block, func_name, comment, classbody, signature):
    func_name_lists = []
    block_lists = []
    comment_lists = []
    classbody_lists = []
    name_line = 0
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
        if extracted_string == signature:
            name_line = line_number
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
    for node in comment:
        # for node in node_list:
        start_point = node.start_point
        end_point = node.end_point

        line_number, column_number = start_point
        end_line_number, end_column_number = end_point

        # 提取所有函数签名

        tuple = (line_number, end_line_number)
        comment_lists.append(tuple)

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
    comment_lists = sorted(comment_lists, key=lambda x: x[1])
    combined_triplets = []
    prefix = 0
    class_index = 0
    # 函数体中加上注释
    for b in block_lists:
        for c in comment_lists:
            if c[1] + 1 == b[0]:
                b[0] = c[0]
                break
    # print(block_lists)
    # print(classbody_lists)
    original = 0
    for index,(list1, list2) in enumerate(zip(block_lists, func_name_lists)):
        # 提取第一个三元组的第一个元素和第二个三元组的后两个元素
        new_triplet = (list2[0], list1[0], list1[1] + 1)
        # 将新三元组添加到列表中
        combined_triplets.append(new_triplet)


    prefix_line = combined_triplets[0][1]
    combined_triplets = sorted(combined_triplets, key=lambda x: x[0])
    for index, (list1) in enumerate(combined_triplets):
        if list1[0] == signature:
            prefix = index
    t = combined_triplets[prefix]

    for index, (interval) in enumerate(classbody_lists):
        if t[1] >= interval[0] and t[2] <= interval[1]:
            class_index = index

    covered_intervals = []
    s = classbody_lists[class_index]
    for index, (interval) in enumerate(combined_triplets):
        if s[0] <= interval[1] and s[1] >= interval[2]:
            covered_intervals.append(interval)

    min_first_element = covered_intervals[0][1]

    # 找到在类中的初始顺序
    new_triplets = sorted(covered_intervals, key=lambda x: x[1])
    for index,(list1) in enumerate(new_triplets):
        if list1[0] == signature:
            original = index

    # 遍历数组中的每个区间
    for index, (interval) in enumerate(covered_intervals):
        # 比较当前区间的第一个元素和已知的最小值

        if interval[1] < min_first_element:
            # 如果当前区间的第一个元素更小，则更新最小值
            min_first_element = interval[1]
        if interval[0] == signature:
            prefix = index

    covered_intervals = move_element(covered_intervals,prefix,original)
    return covered_intervals, min_first_element, original, classbody_lists[class_index][1],name_line
    # 类内代码块,插入起始行，目标函数序号，结束行


def move_element(covered_intervals, prefix, original):
    # 检查索引是否有效
    if not (0 <= prefix < len(covered_intervals)) or not (0 <= original < len(covered_intervals)):
        raise IndexError("Prefix or Original index is out of range")

    # 如果prefix和original相同，则无需移动
    if prefix == original:
        return covered_intervals

    # 使用列表切片和拼接来移动元素
    # 取出prefix位置的元素
    element_to_move = covered_intervals[prefix]

    # 创建新的列表，将prefix之前的部分、要移动的元素放在original位置、以及original之后的部分拼接起来
    new_covered_intervals = covered_intervals[:prefix] + [None] * (original - prefix + 1 if original > prefix else 0) + \
                            [element_to_move] + (covered_intervals[prefix + 1:original] if original > prefix else []) + \
                            (covered_intervals[original:prefix:-1] if original < prefix else []) + (covered_intervals[original + 1:] if original < len(covered_intervals) - 1 and original != prefix else [])

    element_to_move = covered_intervals.pop(prefix)
    covered_intervals.insert(original, element_to_move)

    return covered_intervals
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

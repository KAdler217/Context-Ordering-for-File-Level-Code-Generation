import json
import os

import numpy as np
import tree_sitter
from sklearn.metrics.pairwise import cosine_similarity
from tree_sitter import Language, Parser
import tree_sitter_java as tsjv

from Get_function import read_file_to_get_function
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


def read_file_in_Embedding_order(file_path, num):
    with open(file_path, 'r', encoding='utf-8') as file:
        # for line in file:
        lines = [next(file) for _ in range(202)]
        line = lines[num]
        if line.strip():

            first_json_obj = json.loads(line)
            file_content = first_json_obj['file_content']  # 获取字段值
            func_name = first_json_obj['func_name']
            docstring = first_json_obj['docstring']
            # func_code = first_json_obj['func_code']
            print(func_name)

            tree = parser.parse(bytes(file_content, "utf8"))
            root_node = tree.root_node
            capture = query.captures(root_node)

            #保留第一个函数注释（prefix_line）前面的所有内容，分隔符为prefix_num
            block_lists, prefix_line, prefix_num, end_line, front, back, funcname_line = get_start_lines(file_content,
                                                                                                         capture['2'],
                                                                                                         capture['1'],
                                                                                                         capture['3'],
                                                                                                         capture['4'],
                                                                                                         func_name)
            # print(block_lists)

            lines = file_content.splitlines()

            prefix = lines[0:prefix_line - 1]
            prefix_code = '\n'.join(prefix)

            suffix = lines[end_line:]
            suffix_code = '\n'.join(suffix)

            full_code_pre = ""
            full_code_suf = ""
            full_code_pre += prefix_code

            lenf = len(front)
            merged = front + back
            target_call, target_called = read_file_to_get_function(file_path, num)
            # print(target_call)
            # print(target_called)

            front_part = []
            back_part = []
            middle_part = []  # 这个列表将存储既不在target_called中也不在target_call中的元素
            for sublist in merged:
                second_value = sublist[1]  # 获取子列表的第二个值
                if second_value in target_called:
                    front_part.append(sublist)  # 如果在target_called中，则移动到最前面
                elif second_value in target_call:
                    back_part.append(sublist)  # 如果在target_call中，则移动到末尾
                else:
                    middle_part.append(sublist)  # 否则，留在中间
            result = front_part + middle_part + back_part
            front = result[:lenf]
            back = result[lenf:]
            # print(front)
            # print(result)

            for f in front:
                # Embedding line = lines[f[2]:f[3]]

                line = lines[f[2]:f[3]]  # ABC

                new_code = '\n'.join(line) + '\n'
                full_code_pre += new_code
            # 加入 target
            line1 = lines[funcname_line-len(docstring.splitlines()):funcname_line+1]

            full_code_pre += '\n'.join(line1) + '\n'
            full_code_suf += '    }\n'

            for b in back:
                # Embedding line = lines[b[2]:b[3]]
                line = lines[b[2]:b[3]]  # ABC
                new_code = '\n'.join(line) + '\n'
                full_code_suf += new_code

            full_code_suf += suffix_code
            # print(full_code)

            return full_code_pre, full_code_suf


def get_start_lines(file_content, block, func_name, comment, classbody, signature):
    func_name_lists = []
    block_lists = []
    comment_lists = []
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
    funcname_line = 0
    for func_name in func_name_lists:
        if func_name[0] == signature:
            funcname_line = func_name[1]

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

    for list1, list2 in zip(block_lists, func_name_lists):
        # 提取第一个三元组的第一个元素和第二个三元组的后两个元素（函数名，注释起，函数尾，函数头）
        new_triplet = (list2[0], list1[0], list1[1] + 1, list2[1])
        # 将新三元组添加到列表中
        combined_triplets.append(new_triplet)

    prefix_line = combined_triplets[0][1]
    # combined_triplets = sorted(combined_triplets, key=lambda x: x[0])
    for index, (list1) in enumerate(combined_triplets):
        if list1[0] == signature:
            prefix = index
    t = combined_triplets[prefix]  # 目标函数
    # print(combined_triplets)

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

    min_first_element = covered_intervals[0][1]

    # 遍历数组中的每个区间
    for index, (interval) in enumerate(covered_intervals):
        # 比较当前区间的第一个元素和已知的最小值

        if interval[1] < min_first_element:
            # 如果当前区间的第一个元素更小，则更新最小值
            min_first_element = interval[1]
        if interval[0] == signature:
            prefix = index

    lines = file_content.splitlines()
    funcblock = lines[funcname_line]

    target_embedding = get_embedding(funcblock)
    # hl
    # new_covered_intervals = covered_intervals[:prefix - 1] + covered_intervals[prefix + 1:]
    # whole = process_intervals(new_covered_intervals, lines, target_embedding)
    # whole = sorted(whole, key=lambda x: x[0], reverse=True)
    # front_intervals,back_intervals = split_descending_array(whole)

    # back_intervals = whole
    front, back = split_array(covered_intervals, prefix)

    # # 分段首字母
    # front_intervals = sorted(front, key=lambda x: x[0], reverse=False)
    # back_intervals = sorted(back, key=lambda x: x[0], reverse=False)

    front_intervals = process_intervals(front, lines, target_embedding)
    back_intervals = process_intervals(back, lines, target_embedding)
    #
    # 中间高两头低
    # front_intervals = sorted(front_intervals, key=lambda x: x[0], reverse=False)
    # back_intervals = sorted(back_intervals, key=lambda x: x[0], reverse=True)
    #
    #中间低两头高
    front_intervals = sorted(front_intervals, key=lambda x: x[0], reverse=True)
    back_intervals = sorted(back_intervals, key=lambda x: x[0], reverse=False)
    # for f in front_intervals:
    #     print(f[1])
    # print(signature)
    # for b in back_intervals:
    #     print(b[1])

    return covered_intervals, min_first_element, prefix, classbody_lists[class_index][
        1], front_intervals, back_intervals, funcname_line
    # 类内代码块,插入起始行，目标函数序号，结束行


def split_descending_array(back_intervals):
    n = len(back_intervals)
    # 初始化两个空列表来存储拆分后的数组
    first_half = []
    second_half = []

    # 交替选择元素
    for i in range(n):
        if i % 2 == 0:
            first_half.append(back_intervals[i])
        else:
            second_half.append(back_intervals[i])

    second_half.reverse()
    # 由于我们是交替选择的，所以两个数组都保持降序
    return first_half, second_half


def process_intervals(intervals, lines, target_embedding):
    new_intervals = []

    for interval in intervals:

        tag, block_line, end_line, start_line = interval

        # 提取对应的行内容,不含注释
        code_segment_lines = lines[start_line:end_line]
        code_segment = '\n'.join(code_segment_lines)
        # print(code_segment)

        # 获取代码片段的嵌入向量
        embedding = get_embedding(code_segment)
        target_emb = np.array(target_embedding).reshape(1, -1)
        emb = np.array(embedding).reshape(1, -1)

        # 计算余弦相似度
        if embedding != 0:
            similarity = cosine_similarity(emb, target_emb)[0][0]
        else:
            similarity = 0

        # 更新区间信息
        new_interval = (similarity, tag, block_line, end_line)
        print(new_interval)
        new_intervals.append(new_interval)

    return new_intervals


def split_array(covered_intervals, prefix):
    # Ensure prefix is within the bounds of the list
    if prefix < 0 or prefix >= len(covered_intervals):
        raise IndexError("Prefix index out of range")

    # Split the array into two parts, excluding the element at 'prefix'
    part1 = covered_intervals[:prefix]
    part2 = covered_intervals[prefix + 1:]

    return part1, part2


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

import json
import os
import math

import numpy as np
import tree_sitter
from sklearn.metrics.pairwise import cosine_similarity
from tree_sitter import Language, Parser
import tree_sitter_java as tsjv

from Perplexity import get_perplexity
from Text_embedding import get_embedding

JAVA_LANGUAGE = tree_sitter.Language(tsjv.language())
parser = Parser(JAVA_LANGUAGE)
file_path = 'CoderEval4Java_15K.jsonl'
cpp_query_text = '''

( method_declaration
	name: (identifier) @1
	body: (block) @2
)
( block_comment )@3
( class_declaration)@4

'''
query = JAVA_LANGUAGE.query(cpp_query_text)


def greedy_order(file_path, num):
    with open(file_path, 'r', encoding='utf-8') as file:
        for index1, (line) in enumerate(file):
                first_json_obj = json.loads(line)
                file_content = first_json_obj['file_content']  # 获取字段值
                func_name = first_json_obj['func_name']

                tree = parser.parse(bytes(file_content, "utf8"))
                root_node = tree.root_node
                capture = query.captures(root_node)
                result = ""

                #保留第一个函数注释（prefix_line）前面的所有内容，分隔符为prefix_num
                # block_lists 含有注释的代码块
                # prefix_line 前缀保留内容的首行和后缀
                # prefix_num 目标函数位置
                # end_line 后缀保留的起始行
                # name_line 目标函数首行
                block_lists, prefix_line, prefix_num, end_line, name_line = get_start_lines(file_content, capture['2'],
                                                                                            capture['1'], capture['3'],
                                                                                            capture['4'], func_name)
                lines = file_content.splitlines()
                embedding_lists = get_allemb(block_lists, lines)
                combined_triplets = []
                for index, (list1, list2) in enumerate(zip(block_lists, embedding_lists)):
                    new_triplet = (list1[0], list1[1], list1[2], list2[0])
                    # 将新三元组添加到列表中
                    combined_triplets.append(new_triplet)

                # 组装过程
                # 一个动态的函数列表
                update_lists = [combined_triplets[prefix_num]]
                del combined_triplets[prefix_num]
                # print(combined_triplets)
                prefix_num = 0
                length = min(5, len(combined_triplets))
                stack = []
                stack.extend(combined_triplets)
                # print(stack)

                for k in range(length):
                    # 每一次加入的所有排列
                    # 记住所有排列
                    perm_lists = []
                    # 记住所有分数
                    score_lists = []
                    prefix_lists = []
                    if not stack:
                        break
                    element = stack.pop()
                    for i in range(len(update_lists) + 1):
                        new_list = update_lists[:i] + [element] + update_lists[i:]

                        if i <= prefix_num:
                            prefix_num += 1
                        codes = generate_code(update_lists, lines, name_line, prefix_num, prefix_line, end_line)
                        prefix_lists.append(prefix_num)
                        if i <= prefix_num:
                            prefix_num -= 1
                        score = get_perplexity(codes,func_name)
                        score_lists.append(score)
                        perm_lists.append(new_list)

                    # 找到最小的困惑度
                    min_value = min(score_lists)
                    min_index = score_lists.index(min_value)
                    update_lists = perm_lists[min_index]
                    prefix_num = prefix_lists[min_index]
                    print(prefix_num)
                    print(update_lists)

                while stack:
                    score_lists = []
                    element = stack.pop()
                    target_emb = np.array(element[3]).reshape(1, -1)
                    sim_lists = []
                    for index, (item) in enumerate(update_lists):
                        emb = np.array(item[3]).reshape(1, -1)
                        # 计算余弦相似度
                        if emb != 0:
                            similarity = cosine_similarity(emb, target_emb)[0][0]
                        else:
                            similarity = 0
                        sim_lists.append(similarity)

                    perm, prefix_lists = insert_around_max_elements(sim_lists, element, update_lists, prefix_num)

                    for index, (list1, list2) in enumerate(zip(perm, prefix_lists)):
                        codes = generate_code(list1, lines, name_line, list2, prefix_line, end_line)
                        score = get_perplexity(codes,func_name)
                        score_lists.append(score)

                        # 找到最小的困惑度
                    min_value = min(score_lists)
                    min_index = score_lists.index(min_value)
                    update_lists = perm[min_index]
                    prefix_num = prefix_lists[min_index]
                    print(prefix_num)
                    print(update_lists)

                # 根据列表生成代码
                result = generate_code(update_lists, lines, name_line, prefix_num, prefix_line, end_line)
                file_name = f"sheer1_{index1}.txt"
                folder_name = "Sheer_small"
                file_path = os.path.join(folder_name, file_name)

                # 打开文件进行写入
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(result)


def generate_code(update_lists, lines, name_line, prefix_num, prefix_line, end_line):
    prefix = lines[0:prefix_line - 1]
    prefix_code = '\n'.join(prefix)

    suffix = lines[end_line:]
    suffix_code = '\n'.join(suffix)
    full_code = prefix_code
    for index, (item) in enumerate(update_lists):
        if index < prefix_num:
            line = lines[item[1]:item[2]]
            new_code = '\n'.join(line) + '\n'
            # print(new_code)
            full_code += new_code
        if index == prefix_num:
            line1 = lines[name_line]
            full_code += line1
            full_code += '    } \n'

        if index > prefix_num:
            line = lines[item[1]:item[2]]
            new_code = '\n'.join(line) + '\n'
            # print(new_code)
            full_code += new_code
    full_code += suffix_code
    return full_code


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
    print(func_name_lists)

    original = 0
    for index, (list1, list2) in enumerate(zip(block_lists, func_name_lists)):
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
    new_triplets = covered_intervals
    for index, (list1) in enumerate(new_triplets):
        if list1[0] == signature:
            original = index
    print(original)
    # 遍历数组中的每个区间
    for index, (interval) in enumerate(covered_intervals):
        # 比较当前区间的第一个元素和已知的最小值

        if interval[1] < min_first_element:
            # 如果当前区间的第一个元素更小，则更新最小值
            min_first_element = interval[1]
        if interval[0] == signature:
            prefix = index

    print(covered_intervals)

    return covered_intervals, min_first_element, original, classbody_lists[class_index][1], name_line
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


def generate_permutations(stack, current_list=[]):
    # 如果栈为空，输出当前列表
    if not stack:
        return

    # 从栈中弹出一个元素
    element = stack.pop()

    # 遍历当前列表的所有可能插入位置
    for i in range(len(current_list) + 1):
        # 创建一个新的列表，并在指定位置插入弹出的元素
        new_list = current_list[:i] + [element] + current_list[i:]

        # 递归调用，继续处理剩余的栈元素
        generate_permutations(stack, new_list)

    # 回溯：将弹出的元素重新压回栈中


def get_allemb(block_lists, lines):
    embedding_lists = []
    for index, (item) in enumerate(block_lists):
        line = '\n'.join(lines[item[1]:item[2]])
        embedding_lists.append(get_embedding(line))
    return embedding_lists


# 给出当前序列和插入函数，求算相似度
def insert_around_max_elements(arr, new_element, update_lists, prefix_num):
    if len(arr) < 2:
        raise ValueError("Array is too small to have two distinct maximum elements.")

    # 找到最大的两个元素及其索引
    max1, max2 = float('-inf'), float('-inf')
    max1_index, max2_index = -1, -1

    for index, value in enumerate(arr):
        if value > max1:
            max2, max2_index = max1, max1_index
            max1, max1_index = value, index
        elif value > max2:
            max2, max2_index = value, index

    # 确保 max1_index < max2_index 方便后续操作
    # if max1_index > max2_index:
    #     max1_index, max2_index = max2_index, max1_index

    # 定义四个可能的插入操作
    def insert_at(position):
        new_arr = update_lists[:]
        new_arr.insert(position, new_element)
        return new_arr

    # 计算 prefix_num 的变化
    def calculate_prefix_list(position):
        if position <= prefix_num:
            new_prefix_list = prefix_num + 1
        else:
            new_prefix_list = prefix_num
        return new_prefix_list

    modifications = []
    prefix_lists = []
    positions = [
        max1_index,  # 在第一个最大值之前插入
        max1_index + 1,  # 在第一个最大值之后插入
        # max2_index + 1,  # 在第二个最大值之后插入
        # max2_index  # 在第二个最大值之前插入
    ]

    for pos in positions:
        mod = insert_at(pos)
        prefix_list = calculate_prefix_list(pos)
        modifications.append(mod)
        prefix_lists.append(prefix_list)

    return modifications, prefix_lists


greedy_order(file_path, 33)

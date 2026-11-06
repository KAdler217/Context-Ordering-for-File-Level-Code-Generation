import json
import os
from itertools import permutations

import numpy as np
import openai
import tree_sitter
from openai import OpenAI
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


def read_file_in_all_order(file_path, num):
    with open(file_path, 'r', encoding='utf-8') as file:

        for line_index, (line) in enumerate(file):

            if line_index >= 183:
                print(line_index)

                first_json_obj = json.loads(line)
                file_content = first_json_obj['file_content']  # 获取字段值
                func_name = first_json_obj['func_name']
                func_code = first_json_obj['func_code']
                print(func_name)
                # docstring = first_json_obj['docstring']
                # func_code = first_json_obj['func_code']

                tree = parser.parse(bytes(file_content, "utf8"))
                root_node = tree.root_node
                capture = query.captures(root_node)


                start_line = get_original_lines(capture, file_content, func_name, func_code)

                prefix_line = start_line + 1
                suffix_line = start_line + len(func_code.splitlines()) - 1

                lines = file_content.splitlines()
                prefix = lines[0:prefix_line]
                suffix = lines[suffix_line:]

                prefix_code = '\n'.join(prefix)
                suffix_code = '\n'.join(suffix)

                pre_target = first_train(prefix_code,suffix_code,func_name)


                #保留第一个函数注释（prefix_line）前面的所有内容，分隔符为prefix_num
                block_listss, prefix_line, prefix_num, end_line, name_line, permutations = get_start_lines(file_content,
                                                                                                           capture['2'],
                                                                                                           capture['1'],
                                                                                                           capture['3'],
                                                                                                           capture['4'],
                                                                                                           func_name,pre_target)
                folder_name = os.path.join('perm_hlh_2t', f"line_{line_index}")
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                file_name = "order.txt"
                infile_path = os.path.join(folder_name, file_name)

                for index1, (block_lists) in enumerate(permutations):

                    lines = file_content.splitlines()

                    prefix = lines[0:prefix_line - 1]
                    prefix_code = '\n'.join(prefix)

                    suffix = lines[end_line:]
                    suffix_code = '\n'.join(suffix)

                    full_code_pre = ""
                    full_code_suf = ""
                    full_code_pre += prefix_code
                    print(block_listss)

                    for index, (item) in enumerate(block_lists):
                        # if index < prefix_num:
                        #     line = lines[item[1]:item[2]]
                        #     new_code = '\n'.join(line) + '\n'
                        #     full_code_pre += new_code
                        # if index == prefix_num:
                        #     line1 = lines[name_line]
                        #     full_code_pre += line1
                        #     full_code_suf += '    }'
                        #
                        #
                        # if index > prefix_num:
                        #     line = lines[item[1]:item[2]]
                        #     new_code = '\n'.join(line) + '\n'
                        #     full_code_suf += new_code
                        if item[0] == func_name:
                            line1 = lines[name_line]
                            full_code_pre += line1
                            full_code_pre += '    }'
                        else:

                            print(item)
                            line = lines[item[1]:item[2]]
                            new_code = '\n'.join(line) + '\n'
                            full_code_pre += new_code

                    full_code_suf += suffix_code

                    with open(infile_path, 'a') as file:
                        file.write(f"{index1}: " + f"{block_lists}" + "\n")
                    write_code_to_file(index1, full_code_pre, full_code_suf, folder_name)

                # return full_code_pre, full_code_suf

def get_original_lines(capture, file_content, func_name, func_code):
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
def write_code_to_file(num, full_code_pre, full_code_suf, folder_name):
    # 创建文件夹 permutations（如果不存在）

    # 文件名
    file_name = f"{num}.txt"
    file_path = os.path.join(folder_name, file_name)

    # 文件内容
    content = f"prefix:\n{full_code_pre}\nsuffix:\n{full_code_suf}"

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def get_start_lines(file_content, block, func_name, comment, classbody, signature,pre_target):
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
    # print(func_name_lists)

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
    new_triplets = sorted(covered_intervals, key=lambda x: x[1])
    for index, (list1) in enumerate(new_triplets):
        if list1[0] == signature:
            original = index
            # 比较当前区间的第一个元素和已知的最小值
        if list1[1] < min_first_element:
            # 如果当前区间的第一个元素更小，则更新最小值
            min_first_element = interval[1]

    permutations = permute_local(new_triplets, original, file_content,pre_target)
    print(new_triplets)
    print(new_triplets[original])

    return new_triplets, min_first_element, original, classbody_lists[class_index][1], name_line, permutations
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


def permute(nums, prefix, file_content):
    # 如果数组为空或仅含一个元素，则直接返回该数组（它自身就是一个有效的排列）
    if len(nums) <= 1:
        return [nums]

    # 初始化一个空列表，用于存储所有排列结果
    permutations = []

    if len(nums) > 5:
        permutations = get_subarray_and_sort(nums, prefix, file_content)
    else:

        # 遍历数组中的每一个元素
        for i in range(len(nums)):
            # 提取当前元素
            current_num = nums[i]
            # 创建一个不包含当前元素的新数组
            remaining_nums = nums[:i] + nums[i + 1:]
            # 递归地对剩余元素进行全排列，并将当前元素添加到每个排列的前面
            for p in permute(remaining_nums, prefix, file_content):
                permutations.append([current_num] + p)

    # 返回包含所有排列的列表
    return permutations

def first_train(prefix_code,suffix_code,func_name):
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
            temperature=0.0,
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
def get_emb_and_sort(arr, index, file_content,pre_target):

    lines = file_content.splitlines()
    target_line = arr[index][1]
    end_line = arr[index][2]
    target_embedding = get_embedding(pre_target)
    new_intervals = []

    for interval in arr:

        func_name, start_line, end_line = interval

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
        new_interval = (func_name, start_line, end_line, similarity)
        new_intervals.append(new_interval)
    # lhl
    final_intervals,max_index = process_array(new_intervals)
    return new_intervals,final_intervals,max_index

    # hlh
    # new_intervals.sort(key=lambda x: x[1][3], reverse=True)
    # return new_intervals



def process_array(arr):
    # Step 1: 找出 element[3] 最大的5个元素及其索引
    indexed_elements = list(enumerate(arr))

    indexed_elements.sort(key=lambda x: x[1][3], reverse=True)  # 按 element[3] 降序排序
    print(indexed_elements)
    original = list(enumerate(arr))
    top_five_elements = indexed_elements[:5]  # 获取前5个最大的元素及其索引

    # 提取最大值元素的信息（但不从原逻辑中移除）
    max_element_info = top_five_elements[0]  # 最大的元素的信息
    max_element = max_element_info[1]

    # 提取其他4个最大元素（用于插入）
    other_top_four_elements = [elem[1] for elem in top_five_elements[0:]]

    # Step 2: 创建一个新数组，从原数组中“逻辑上”移除这5个最大元素（但保留最大值用于后续不删除）
    # 实际上我们只是暂时不考虑它们，用集合来记录要排除的索引（除了最大值）
    exclude_indices = {elem[0] for elem in top_five_elements[0:]}  # 排除其他4个最大值的索引

    # 创建新数组，不包含需要排除的4个最大元素
    new_arr = [elem for idx, elem in original if idx not in exclude_indices]


    # Step 3: 找到新数组中最大元素的位置
    if not new_arr:
        raise ValueError("New array is empty after removing top 4 (excluding the absolute max) elements.")

    max_index_in_new_arr = max(range(len(new_arr)), key=lambda i: new_arr[i][3])

    # # Step 4: 将其他4个最大元素插入到新数组中最大元素的位置
    # # 在最大元素位置前插入2个，后插入2个
    # insert_before = max(0, max_index_in_new_arr)  # 确保不越界
    # insert_after = min(len(new_arr), max_index_in_new_arr + 1)  # 确保不越界
    #
    # # 插入逻辑
    # # 插入前两个元素
    # if len(other_top_four_elements) >= 2:
    #     new_arr.insert(insert_before, other_top_four_elements.pop(0))
    #     new_arr.insert(insert_before + 1, other_top_four_elements.pop(0))
    #
    # # 更新插入后的索引位置（因为插入了2个元素）
    # max_index_in_new_arr += 2 if len(other_top_four_elements) >= 2 else (
    #     1 if len(other_top_four_elements) == 1 else 0)
    # insert_after = min(len(new_arr), max_index_in_new_arr + 1)  # 重新计算插入后的位置
    #
    # # 插入后两个元素
    # if len(other_top_four_elements) >= 1:
    #     new_arr.insert(insert_after, other_top_four_elements.pop(0))
    # if len(other_top_four_elements) >= 1:
    #     new_arr.insert(insert_after + 1, other_top_four_elements.pop(0))

    return new_arr, max_index_in_new_arr


def get_subarray_and_sort(arr, index, file_content):
    # Calculate the start and end indices for the subarray
    arr, max_index = get_emb_and_sort(arr, index, file_content)
    index = max_index
    start = max(0, index - 2)
    end = min(len(arr), index + 3)  # +6 because we want to include the index itself and 5 more elements

    # Extract the subarray
    subarray = arr[start:end]

    # Generate all permutations of the subarray
    all_permutations = list(permutations(subarray))

    # Convert each permutation from tuple back to list (optional, depending on use case)
    all_permutations_as_lists = [list(perm) for perm in all_permutations]

    return all_permutations_as_lists


# 更好的五排序
def permute_local(arr, index, file_content,pre_target):
    if len(arr) > 5:
        unsorted,sorted_arr, max_index = get_emb_and_sort(arr, index, file_content,pre_target)
        unsorted.sort(key=lambda x: x[3], reverse=True)

        # index = max_index
        # # 检查索引是否在有效范围内
        # if index < 2 or index >= len(arr) - 2:
        #     raise ValueError("Index is too close to the array boundary to permute 5 elements.")

        # 提取需要排列的子数组
        # lhl
        # subarray = sorted_arr[index-2:index+3]
        # hlh
        subarray = unsorted[1:5]
        # 生成子数组的全排列
        sub_permutations = list(permutations(subarray))

        # 存储结果的列表
        result = []
        tuple = (unsorted[0])

        # 重建数组，将每个排列结果与原数组的其他部分组合
        for perm in sub_permutations:
            # 提取 perm 的元素
            first_two = perm[:2]  # 前两个元素
            # print(first_two)
            last_two = perm[2:4]  # 后两个元素

            # last = list(last_two)
            # last.append(tuple)
            # 构造新的数组
            new_arr = list(first_two) + sorted_arr + list(last_two)
            # new_arr = arr[:index - 2] + list(perm) + arr[index + 3:]
            result.append(new_arr)
    else:
        result = permutations(arr)

    return result


read_file_in_all_order(file_path, 1)

import re
import string


def del_spaces(txt: str) -> str:
    if not txt:
        return ""
    return re.compile("\\s").sub('', txt)


def count_hit_lines(expect: str, actual: str):
    expects = expect.split("\n")
    actuals = actual.split("\n")
    expect_set = set()

    expect_line_cnt = 0

    # 将模型生成的行符合条件的行加到set里
    for line in expects:
        format_txt = del_spaces(line)
        if format_txt and format_txt not in "{}":
            expect_line_cnt += 1
            expect_set.add(format_txt)

    match_count = 0
    for line in actuals:
        format_txt = del_spaces(line)
        if format_txt and format_txt not in "{}":
            if format_txt in expect_set:
                match_count += 1

    return min(1., match_count / expect_line_cnt) * 100


def count_hit_lines_method(expect: str, actual: str, call_method="precision"):
    """
        expect: 参考代码
        actual: 模型生成代码
        call_method: recall 期望生成行数为分母 | precision 模型生成行数为分母
    """
    expects = expect.split("\n")
    actuals = actual.split("\n")
    except_list = []
    actual_list = []
    for exp in expects:
        exp = del_spaces(exp)
        if exp and exp not in "{}":
            except_list.append(exp)

    for act in actuals:
        act = del_spaces(act)
        if act and act not in "{}":
            actual_list.append(act)

    len_expect = len(except_list)
    len_actual = len(actual_list)

    match_cnt = cal_intersection(except_list, actual_list)
    denominator = len_expect if call_method == "recall" else len_actual
    if denominator == 0:
        return 0
    return min(1., match_cnt / denominator) * 100


def find_first_no_comment_line(lines: list):
    # 合法字符
    valid_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + "*" + "_"
    # 找到不为注释的第一行
    continuous_comment_cnt = 0
    for idx, line in enumerate(lines):
        line = line.lstrip()
        # 不在连续注释内，不为空行且为正常行起始字符
        if not continuous_comment_cnt and line and line[0] in valid_chars:
            return idx

        # 连续注释起始符，跳过
        if "/*" in line:
            continuous_comment_cnt += 1
        if "*/" in line:
            continuous_comment_cnt = max(0, continuous_comment_cnt - 1)
    return -1


def first_line_match(expect: str, actual: str):
    expect_lines = expect.split("\n")
    actual_lines = actual.split("\n")
    expect_idx = find_first_no_comment_line(expect_lines)
    actual_idx = find_first_no_comment_line(actual_lines)
    if expect_idx < 0 or actual_idx < 0:
        return 0
    if expect_lines[expect_idx].strip() == actual_lines[actual_idx].strip():
        return 100
    return 0


def cal_intersection(expects: list, actuals: list):
    cnt = 0
    for item in expects:
        if item in actuals:
            cnt += 1
            actuals.remove(item)
    return cnt


if __name__ == '__main__':
    print(find_first_no_comment_line("    /* test  \n  123 \n  12344 */ \n 66"))
    print(first_line_match("    /* test  \n  123 \n  12344 */ \n 66", "66\n"))

import json
import os
import glob
from metric import evaluate_rouge, evaluate_es_singleline, evaluate_bleu, evaluate_codebleu, evaluate_sbert
# from local_metric import evaluate_rouge, evaluate_es_singleline, evaluate_bleu
from lines_hit_ratio import count_hit_lines_method, first_line_match
import numpy as np
from tqdm import tqdm
import os
import sys
from datasets import load_dataset

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.setrecursionlimit(10000)  # 设置最大递归深度为10000


def get_jsonl_file_list(input_file_or_dir):
    jsonl_file_list = []
    # 文件夹处理
    if os.path.isdir(input_file_or_dir):
        jsonl_file_list += glob.glob(os.path.join(input_file_or_dir, "*.jsonl"))
    # 单文件处理
    elif input_file_or_dir.endswith(".jsonl"):
        jsonl_file_list.append(input_file_or_dir)
    else:
        raise ValueError("入参错误")
    return jsonl_file_list


class LocalEvaluator:
    @staticmethod
    def FromData(content):
        counter_es = []
        counter_bleu = []
        counter_rouge = []
        counter_line_hit = []
        counter_line_hit_at_50 = []
        counter_first_line_hit = []
        counter_line_hit_recall = []
        skip_num = 0

        for idx, single_qa in enumerate(content):
            prompt = single_qa["prompt"]
            # generation_truncate = single_qa["generation"][0][len(prompt):]  # 截取方式注意
            generation_truncate = single_qa["result"]

            generation_truncate = generation_truncate \
                .replace("```cpp", "") \
                .replace("```c", "") \
                .replace("```java", "") \
                .replace("```go", "") \
                .replace("```arkts", "") \
                .replace("```", "") \
                .replace("<unused1>", "").rstrip("\n")
            solution = single_qa["solution"]
            if len(solution) == 0:
                skip_num += 1
                continue

            counter_es.append(evaluate_es_singleline(solution, generation_truncate))
            counter_bleu.append(evaluate_bleu(solution, generation_truncate))
            counter_rouge.append(evaluate_rouge(solution, generation_truncate))
            counter_line_hit.append(count_hit_lines_method(solution, generation_truncate))
            counter_line_hit_at_50.append(100. if counter_line_hit[-1] >= 50 else 0.)
            counter_first_line_hit.append(first_line_match(solution, generation_truncate))
            counter_line_hit_recall.append(count_hit_lines_method(solution, generation_truncate, call_method="recall"))

        es_score = np.mean(np.array(counter_es))
        rouge_l_score = np.mean(np.array(counter_rouge))
        bleu_score = np.mean(np.array(counter_bleu))
        score_info = {
            "from": "data",
            "es": es_score,
            "bleu": bleu_score,
            "rouge": rouge_l_score,
            "line_hit": np.mean(np.array(counter_line_hit)),
            "line_hit_recall": np.mean(np.array(counter_line_hit_recall)),
            "line_hit_at_50": np.mean(np.array(counter_line_hit_at_50)),
            "first_line_hit": np.mean(np.array(counter_first_line_hit)),
            "acc": 0.5 * es_score + 0.2 * bleu_score + 0.3 * rouge_l_score,
            "skip_num": skip_num,
        }
        print(json.dumps(score_info, indent=4))
        return score_info

    @staticmethod
    def FromFiles(input_file):
        return main(input_file)


def main(input_file_or_dir=r"D:\workspace\maas_predict\0512测评\测试", eval_list=None):
    jsonl_file_list = get_jsonl_file_list(input_file_or_dir)
    score_data = []
    for jsonl_file in jsonl_file_list:
        with open(jsonl_file, "r", encoding="utf8") as f:
            content = [json.loads(i) for i in f.readlines()]
        counter_es = []
        counter_bleu = []
        counter_rouge = []
        counter_syntax = []
        counter_dataflow = []
        counter_codebleu = []
        counter_sbert = []
        counter_line_hit = []
        counter_line_hit_at_50 = []
        counter_first_line_hit = []
        counter_line_hit_recall = []
        skip_num = 0

        for idx, single_qa in tqdm(enumerate(content), total=len(content), position=0, leave=True, desc="Evaluation"):
            # prompt = single_qa["prompt"]
            # generation_truncate = single_qa["generation"][0][len(prompt):]  # 截取方式注意
            #
            # generation_truncate = generation_truncate \
            #     .replace("```cpp", "") \
            #     .replace("```c", "") \
            #     .replace("```java", "") \
            #     .replace("```go", "") \
            #     .replace("```arkts", "") \
            #     .replace("```", "") \
            #     .replace("<unused1>", "").rstrip("\n")
            # solution = single_qa["solution"]
            # if len(solution) == 0:
            #     skip_num += 1
            #     continue

            # counter_es.append(evaluate_es_singleline(solution, generation_truncate))
            # counter_bleu.append(evaluate_bleu(solution, generation_truncate))
            # counter_rouge.append(evaluate_rouge(solution, generation_truncate))
            # counter_line_hit.append(count_hit_lines_method(solution, generation_truncate))
            # counter_line_hit_at_50.append(100. if counter_line_hit[-1] >= 50 else 0.)
            # counter_first_line_hit.append(first_line_match(solution, generation_truncate))
            # counter_line_hit_recall.append(count_hit_lines_method(solution, generation_truncate, call_method="recall"))

            if eval_list:
                if idx not in eval_list:
                    skip_num += 1
                    continue

            solution = single_qa['solution']
            result = single_qa['result']

            counter_es.append(evaluate_es_singleline(solution, result))
            counter_bleu.append(evaluate_bleu(solution, result))
            counter_rouge.append(evaluate_rouge(solution, result))
            codebleu_score = evaluate_codebleu(solution, result)
            counter_syntax.append(codebleu_score[0])
            counter_dataflow.append(codebleu_score[1])
            counter_codebleu.append(codebleu_score[2])
            counter_sbert.append(evaluate_sbert(solution, result))
            counter_line_hit.append(count_hit_lines_method(solution, result))
            counter_line_hit_at_50.append(100. if counter_line_hit[-1] >= 50 else 0.)
            counter_first_line_hit.append(first_line_match(solution, result))
            counter_line_hit_recall.append(count_hit_lines_method(solution, result, call_method="recall"))

            cur_score_data = {
                "result": result,
                "solution": solution,
                "es": counter_es[-1],
                "bleu": counter_bleu[-1],
                "rouge": counter_rouge[-1],
                "syntax": counter_syntax[-1],
                "dataflow": counter_dataflow[-1],
                "codebleu": counter_codebleu[-1],
                "sbert": counter_sbert[-1],
                "line_hit": counter_line_hit[-1],
                "line_hit_recall": counter_line_hit_recall[-1],
                "first_line_hit": counter_first_line_hit[-1],
            }
            score_data.append(cur_score_data)

        es_score = np.mean(np.array(counter_es))
        rouge_l_score = np.mean(np.array(counter_rouge))
        bleu_score = np.mean(np.array(counter_bleu))
        syntax_score = np.mean(np.array(counter_syntax))
        dataflow_score = np.mean(np.array(counter_dataflow))
        codebleu_score = np.mean(np.array(counter_codebleu))
        sbert_score = np.mean(np.array(counter_sbert))   

        score_info = {
            "from": "data",
            "es": es_score,
            "bleu": bleu_score,
            "rouge": rouge_l_score,
            "syntax": syntax_score,
            "dataflow": dataflow_score,
            "codebleu": codebleu_score,
            "sbert": sbert_score,
            "line_hit": np.mean(np.array(counter_line_hit)),
            "line_hit_recall": np.mean(np.array(counter_line_hit_recall)),
            "line_hit_at_50": np.mean(np.array(counter_line_hit_at_50)),
            "first_line_hit": np.mean(np.array(counter_first_line_hit)),
            "acc": 0.5 * es_score + 0.2 * bleu_score + 0.3 * rouge_l_score,
            "skip_num": skip_num,
            "num": len(counter_line_hit),
        }


        # with open("../../Demo/test2find/DeepSeek_best.txt", 'w', encoding='utf-8') as f:
        #     for b,c,s,l in zip(counter_bleu,counter_codebleu,counter_sbert,counter_line_hit):
        #       f.write(f"{b} {c} {s} {l} \n")


        print(json.dumps(score_info, indent=4))
        return score_info, score_data


if __name__ == '__main__':
    # idx = "../data/CoderEval/hw_java.jsonl"
    # idx = load_dataset('json', data_files=idx, split="train")['sample_index']
    #
    # print('CoderEval Function Java response score=>')
    file_name = '../../Demo/DeepSeekV3_perm_hlh_2t_input.jsonl'
    info, _ = main(input_file_or_dir=file_name)
    # with open("../../Demo/Embedding(chlhc)_with_llama_eval.json", 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval Raw Java response score=>')
    # file_name = '../CoderEval/qwencoder/raw_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open("../CoderEval/qwencoder/raw_java_1.5B/eval_hw_part.json", 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval Random Score Java response score=>')
    # file_name = '../CoderEval/qwencoder/random_score_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/random_score_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval Function Similarity Java response score=>')
    # file_name = '../CoderEval/qwencoder/function_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/function_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval Keywords Similarity Java response score=>')
    # file_name = '../CoderEval/qwencoder/keywords_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/keywords_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval TTT Similarity Java response score=>')
    # file_name = '../CoderEval/qwencoder/ttt_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/ttt_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval KeyToken Similarity Java response score=>')
    # file_name = '../CoderEval/qwencoder/keytoken_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/keytoken_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval HW Java response score=>')
    # file_name = '../CoderEval/qwencoder/hw_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name)
    # with open('../CoderEval/qwencoder/hw_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('CoderEval Summary Similarity Java response score=>')
    # file_name = '../CoderEval/qwencoder/summary_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../CoderEval/qwencoder/summary_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # **************************************************************************
    # **************************************************************************
    # **************************************************************************
    # **************************************************************************
    # **************************************************************************

    # idx = "../data/RepoBenchmark/hw_java.jsonl"
    # idx = load_dataset('json', data_files=idx, split="train")['sample_index']

    # print('RepoBenchmark Function Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/func_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open("../RepoBenchmark/qwencoder/func_java_1.5B/eval_hw_part.json", 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark Raw Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/raw_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open("../RepoBenchmark/qwencoder/raw_java_1.5B/eval_hw_part.json", 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark Random Score Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/random_score_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../RepoBenchmark/qwencoder/random_score_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark Function Similarity Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/function_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../RepoBenchmark/qwencoder/function_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark Keywords Similarity Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/keywords_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../RepoBenchmark/qwencoder/keywords_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark TTT Similarity Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/ttt_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../RepoBenchmark/qwencoder/ttt_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark KeyToken Similarity Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/keytoken_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name, eval_list=idx)
    # with open('../RepoBenchmark/qwencoder/keytoken_similarity_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark HW Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/hw_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name)
    # with open('../RepoBenchmark/qwencoder/hw_java_1.5B/eval_hw_part.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # print('RepoBenchmark Summary Similarity Java response score=>')
    # file_name = '../RepoBenchmark/qwencoder/summary_similarity_java_1.5B/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name)
    # with open('../RepoBenchmark/qwencoder/summary_similarity_java_1.5B/eval.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

    # **************************************************************************
    # **************************************************************************
    # **************************************************************************
    # **************************************************************************
    # **************************************************************************

    # print('Random Score SFT Checkpoint-180 response score=>')
    # file_name = '../CoderEval/sft_random/random_score_java_180/result.jsonl'
    # info, _ = main(input_file_or_dir=file_name)
    # with open('../CoderEval/sft_random/random_score_java_180/eval.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(info))

from fuzzywuzzy import fuzz
from rouge import Rouge
import nltk.translate.bleu_score as bleu
from nltk.translate.bleu_score import SmoothingFunction
from codebleu import calc_codebleu
from sentence_transformers import SentenceTransformer, util

from tokenizer import Tokenizer13a

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def evaluate_rouge(reference: str, generation: str) -> float:
    """
    计算rouge值，包括rouge-1, rouge-2, rouge-L
    :param generation: a str of hypothesis sentences
    :type generation: str
    :param reference: a str of reference sentences
    :type reference: str
    """
    reference = reference.strip()
    generation = generation.strip()

    if not reference or not generation:
        return 0.

    # 初始化rouge object
    rouge = Rouge()

    # calculate rouge scores
    # try:
    #     scores = rouge.get_scores(generation, reference)
    # except ValueError:
    #     return 0.
    scores = rouge.get_scores(generation, reference)

    # 返回一个包含ROUGE-1、ROUGE-2和ROUGE-L指标的字典列表，其中每个字典包含各自指标的f、p、r值。
    return scores[0]["rouge-l"]["f"] * 100.


def evaluate_es_singleline(reference, generation):
    generation = generation.strip()
    reference = reference.strip()
    edit_sim = fuzz.ratio(generation, reference)
    return edit_sim


def evaluate_bleu(reference: str, generation: str, tokenizer=Tokenizer13a(),
                  smoothing_function=SmoothingFunction().method1,
                  auto_reweigh=False, ):
    weights = (0.25, 0.25, 0.25, 0.25)
    references = [reference]
    generations = [generation]
    reference_lists = [[ref] for ref in references]
    reference_lists = [[tokenizer(r) for r in ref] for ref in reference_lists]
    generation_lst = [tokenizer(g) for g in generations]
    bleu_score = bleu.corpus_bleu(reference_lists, generation_lst, weights, smoothing_function, auto_reweigh)
    return round(bleu_score * 100.0, 4)


def evaluate_codebleu(reference, generation):
    result = calc_codebleu([reference], [generation], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
    syntax_score = result['syntax_match_score']
    dataflow_score = result['dataflow_match_score']
    codebleu = result['codebleu']
    return round(syntax_score * 100.0, 4), round(dataflow_score * 100.0, 4), round(codebleu * 100.0, 4)


def evaluate_sbert(reference, prediction):
    embedding1 = model.encode(reference, convert_to_tensor=True)
    embedding2 = model.encode(prediction, convert_to_tensor=True)

    score = util.cos_sim(embedding1, embedding2).item()
    return round(score * 100, 4)


if __name__ == "__main__":
    pass

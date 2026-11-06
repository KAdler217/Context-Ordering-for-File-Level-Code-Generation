import os
import numpy as np
from openai import OpenAI
from decimal import Decimal, getcontext


def get_perplexity(content, func_name):
    # client = OpenAI(api_key=os.environ.get("LLM_API_KEY", ""), base_url="https://api.deepseek.com")
    client = OpenAI(api_key=os.environ.get("CHUTES_API_TOKEN", ""), base_url="https://llm.chutes.ai/v1/chat/completions")

    response = client.chat.completions.create(
        # model="deepseek-chat",
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user",
             "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"},
        ],

        logprobs=True,
        temperature=0.2,
        # top_p=0.95,
        max_tokens=30,
        # stop="\n\n",
        stream=False,
    )

    choice = response.choices[0]

    getcontext().prec = 10
    # 假设logprobs_list是一个包含每个token自然对数概率的列表
    logprob_list = [token.logprob for token in choice.logprobs.content]  # 从Choice对象中提取logprob
    total_logprob = 0
    for i in logprob_list:
        total_logprob += i
    # 计算token的总数
    n = len(logprob_list)

    # 计算平均每个token的对数概率
    average_logprob = -total_logprob / n

    print(average_logprob)
    return average_logprob
get_perplexity("...","quicksort()")

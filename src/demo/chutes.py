import os
import requests
import json
import numpy as np

import requests
import json
import numpy as np
import time


def invoke_chute1(content, func_name, api):
    def make_request():
        if api == 0:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")  # Replace with your actual API token
        if api == 1:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 2:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 3:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")

        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json"
        }

        body = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "user",
                    "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"
                }
            ],
            "stream": True,
            "max_tokens": 50,
            "temperature": 0.2,
            "logprobs": True
        }

        try:
            response = requests.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=body,
                stream=True,
                timeout=30  # 设置请求超时
            )

            total = 0
            n = 0
            for line in response.iter_lines(decode_unicode=True):
                line = line.strip()

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break
                    try:
                        n += 1
                        chunk = json.loads(data)
                        logprobs = chunk["choices"][0]["logprobs"]["content"]
                        total_logprobs = sum(logprob["logprob"] for logprob in logprobs)
                        total += total_logprobs

                    except Exception as e:
                        print(f"Error parsing chunk: {e}")

            response.close()
            if n == 0:
                return None
            else:
                print(total / n)
                return np.exp(-total / n)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    max_retries = 3
    retries = 0
    while retries < max_retries:
        result = make_request()
        if result is not None:
            return result
        retries += 1
        print(f"Retrying in 20 seconds... ({retries}/{max_retries})")
        time.sleep(60)

    print("Max retries reached. Failed to get a response.")
    return None

def invoke_chute2(content, func_name, api):
    def make_request():
        if api == 0:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")  # Replace with your actual API token
        if api == 1:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 2:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 3:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")

        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json"
        }

        body = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "user",
                    "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"
                }
            ],
            "stream": True,
            "max_tokens": 50,
            "temperature": 0.2,
            "logprobs": True
        }

        try:
            response = requests.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=body,
                stream=True,
                timeout=30  # 设置请求超时
            )

            total = 0
            n = 0
            for line in response.iter_lines(decode_unicode=True):
                line = line.strip()

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break
                    try:
                        n += 1
                        chunk = json.loads(data)
                        logprobs = chunk["choices"][0]["logprobs"]["content"]
                        total_logprobs = sum(logprob["logprob"] for logprob in logprobs)
                        total += total_logprobs

                    except Exception as e:
                        print(f"Error parsing chunk: {e}")

            response.close()
            if n == 0:
                return None
            else:
                print(total / n)
                return np.exp(-total / n)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    max_retries = 3
    retries = 0
    while retries < max_retries:
        result = make_request()
        if result is not None:
            return result
        retries += 1
        print(f"Retrying in 20 seconds... ({retries}/{max_retries})")
        time.sleep(60)

    print("Max retries reached. Failed to get a response.")
    return None

def invoke_chute3(content, func_name, api):
    def make_request():
        if api == 0:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")  # Replace with your actual API token
        if api == 1:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 2:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 3:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")

        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json"
        }

        body = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "user",
                    "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"
                }
            ],
            "stream": True,
            "max_tokens": 50,
            "temperature": 0.2,
            "logprobs": True
        }

        try:
            response = requests.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=body,
                stream=True,
                timeout=30  # 设置请求超时
            )

            total = 0
            n = 0
            for line in response.iter_lines(decode_unicode=True):
                line = line.strip()

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break
                    try:
                        n += 1
                        chunk = json.loads(data)
                        logprobs = chunk["choices"][0]["logprobs"]["content"]
                        total_logprobs = sum(logprob["logprob"] for logprob in logprobs)
                        total += total_logprobs

                    except Exception as e:
                        print(f"Error parsing chunk: {e}")

            response.close()
            if n == 0:
                return None
            else:
                print(total / n)
                return np.exp(-total / n)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    max_retries = 3
    retries = 0
    while retries < max_retries:
        result = make_request()
        if result is not None:
            return result
        retries += 1
        print(f"Retrying in 20 seconds... ({retries}/{max_retries})")
        time.sleep(60)

    print("Max retries reached. Failed to get a response.")
    return None

def invoke_chute4(content, func_name, api):
    def make_request():
        if api == 0:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")  # Replace with your actual API token
        if api == 1:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 2:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")
        if api == 3:
            api_token = os.environ.get("CHUTES_API_TOKEN", "")

        headers = {
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json"
        }

        body = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "user",
                    "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"
                }
            ],
            "stream": True,
            "max_tokens": 50,
            "temperature": 0.2,
            "logprobs": True
        }

        try:
            response = requests.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=body,
                stream=True,
                timeout=30  # 设置请求超时
            )

            total = 0
            n = 0
            for line in response.iter_lines(decode_unicode=True):
                line = line.strip()

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break
                    try:
                        n += 1
                        chunk = json.loads(data)
                        logprobs = chunk["choices"][0]["logprobs"]["content"]
                        total_logprobs = sum(logprob["logprob"] for logprob in logprobs)
                        total += total_logprobs

                    except Exception as e:
                        print(f"Error parsing chunk: {e}")

            response.close()
            if n == 0:
                return None
            else:
                print(total / n)
                return np.exp(-total / n)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    max_retries = 3
    retries = 0
    while retries < max_retries:
        result = make_request()
        if result is not None:
            return result
        retries += 1
        print(f"Retrying in 20 seconds... ({retries}/{max_retries})")
        time.sleep(60)

    print("Max retries reached. Failed to get a response.")
    return None
# def invoke_chute(content, func_name,api):
#     if api == 0:api_token = os.environ.get("CHUTES_API_TOKEN", "")  # Replace with your actual API token
#     if api == 1:api_token = os.environ.get("CHUTES_API_TOKEN", "")
#     if api == 2:api_token = os.environ.get("CHUTES_API_TOKEN", "")
#     if api == 3:api_token = os.environ.get("CHUTES_API_TOKEN", "")
#
#     headers = {
#         "Authorization": "Bearer " + api_token,
#         "Content-Type": "application/json"
#     }
#
#     body = {
#         "model": "deepseek-ai/DeepSeek-V3",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "这是该函数的上下文" + content + "请补全该函数:" + func_name + "并返回完整的函数体，包括函数签名，不要生成注释"
#             }
#         ],
#         "stream": True,
#         "max_tokens": 50,
#         "temperature": 0.2,
#         "logprobs": True
#     }
#
#     response = requests.post(
#         "https://llm.chutes.ai/v1/chat/completions",
#         headers=headers,
#         json=body,
#         stream=True
#     )
#
#     total = 0
#     n = 0
#     for line in response.iter_lines(decode_unicode=True):
#         line = line.strip()
#
#         if line.startswith("data: "):
#             data = line[6:]
#
#             if data == "[DONE]":
#                 break
#             try:
#                 n += 1
#                 chunk = json.loads(data)
#                 logprobs = chunk["choices"][0]["logprobs"]["content"]
#                 total_logprobs = sum(logprob["logprob"] for logprob in logprobs)
#                 total += total_logprobs
#
#             except Exception as e:
#                 print(f"Error parsing chunk: {e}")
#
#     print(total / n)
#     return np.exp(-total / n)

# 示例用法
# result = invoke_chute("some content", "some_function_name")
# print(result)

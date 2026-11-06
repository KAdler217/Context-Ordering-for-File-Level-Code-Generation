import os
import json
import requests
from transformers import AutoTokenizer


def get_embedding(funcode):
    model_name = "BAAI/bge-large-en-v1.5"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    ref = tokenizer.encode(funcode, truncation=True, add_special_tokens=False)[:500]
    funcode = tokenizer.decode(ref)

    url = "https://api.siliconflow.cn/v1/embeddings"

    payload = {
        "model": "BAAI/bge-large-en-v1.5",
        "input": funcode,
        "encoding_format": "float"
    }
    headers = {
        "Authorization": "Bearer " + os.environ.get("EMBEDDING_API_KEY", ""),
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    response_dict = json.loads(response.text)
    data = response_dict.get('data')
    if data is None or not isinstance(data, list) or len(data) == 0:
        print("No valid embeddings found in the response. Setting embedding to zero vector.")
        return 0
    else:
        embeddings = [item['embedding'] for item in response_dict.get('data', [])]
        return embeddings[0]

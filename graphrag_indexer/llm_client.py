# llm_client.py
from openai import OpenAI
from config import LLM_API_BASE, LLM_MODEL

client = OpenAI(
    base_url=LLM_API_BASE,
    #api_key="local"
)

def call_llm(prompt, temperature=0.1):
    MAX_CHARS = 12000   # ~3000 tokens safety

    if len(prompt) > MAX_CHARS:
        prompt = prompt[:MAX_CHARS] + "\n\n[TRUNCATED]"

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content


from typing import List, Dict

from openai import OpenAI

from src.conf.settings import OPENAI_API_KEY

gpt_client = OpenAI(
    api_key=OPENAI_API_KEY,
)


async def chat_completion(
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
) -> str:
    """
    Gửi danh sách messages theo chuẩn OpenAI Chat API và trả về content của assistant.

    :param messages: list of {"role": "system|user|assistant", "content": "..."}
    :param model: model name, ví dụ "gpt-4o-mini"
    :param temperature: độ ngẫu nhiên
    :param max_tokens: số token tối đa trả về
    :param kwargs: thêm các param OpenAI (nếu cần)
    """
    resp = await gpt_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return resp.choices[0].message["content"]

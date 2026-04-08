import json
from openai import AsyncOpenAI
from app.core.config import settings

# Initialize AsyncOpenAI client pointing to DeepSeek
client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY or "dummy",
    base_url="https://api.deepseek.com/v1"
)

async def generate_json(system_prompt: str, user_prompt: str, model="deepseek-chat") -> dict:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback if it didn't output clean JSON
        # basic cleaning
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        raise ValueError("Failed to parse JSON from model output")

async def generate_text(system_prompt: str, user_prompt: str, model="deepseek-chat") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

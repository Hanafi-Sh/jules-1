import json
import re
from openai import AsyncOpenAI
from app.core.config import settings

# Initialize AsyncOpenAI client pointing to DeepSeek
client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY or "dummy",
    base_url="https://api.deepseek.com/v1"
)

def extract_json_from_text(text: str) -> dict:
    """Safely extracts JSON from a text block that might contain markdown formatting."""
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find json block using regex
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # As a last resort, just look for the first { and last }
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(text[start_idx:end_idx+1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse JSON from model output. Content snippet: {text[:200]}")

async def generate_json(system_prompt: str, user_prompt: str, model="deepseek-reasoner") -> dict:
    """Generates JSON output. Defaults to deepseek-reasoner for deep thinking."""

    # For deepseek-reasoner, we typically shouldn't force response_format={"type": "json_object"}
    # as it might not be fully supported or might interfere with the reasoning trace.
    # We rely on prompting and extraction.

    # Append a strong JSON instruction if not using native json mode
    full_user_prompt = f"{user_prompt}\n\nIMPORTANT: You must output ONLY valid JSON without any surrounding text or explanation outside of the JSON block."

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_prompt}
        ],
        temperature=0.6, # Slightly lower for more deterministic JSON
    )
    content = response.choices[0].message.content
    return extract_json_from_text(content)

async def generate_text(system_prompt: str, user_prompt: str, model="deepseek-reasoner") -> str:
    """Generates text output. Defaults to deepseek-reasoner."""
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

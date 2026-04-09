import json
import re
import logging
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AsyncOpenAI client pointing to DeepSeek
client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY or "dummy",
    base_url="https://api.deepseek.com/v1"
)

def extract_json_from_text(text: str) -> dict:
    """Safely extracts JSON from a text block that might contain markdown formatting."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(text[start_idx:end_idx+1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse JSON from model output. Content snippet: {text[:200]}")

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(f"Retrying JSON generation... Attempt {retry_state.attempt_number}")
)
async def generate_json(system_prompt: str, user_prompt: str, model="deepseek-reasoner") -> dict:
    """Generates JSON output. Defaults to deepseek-reasoner for deep thinking. Includes auto-retry."""

    full_user_prompt = f"{user_prompt}\n\nIMPORTANT: You must output ONLY valid JSON without any surrounding text or explanation outside of the JSON block."

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_prompt}
        ],
        temperature=0.6,
    )
    content = response.choices[0].message.content
    return extract_json_from_text(content)

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(f"Retrying Text generation... Attempt {retry_state.attempt_number}")
)
async def generate_text(system_prompt: str, user_prompt: str, model="deepseek-reasoner") -> str:
    """Generates text output. Defaults to deepseek-reasoner. Includes auto-retry."""
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

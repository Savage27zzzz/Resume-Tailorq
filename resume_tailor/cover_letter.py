import os
import time
from .client import get_client
from .prompts import COVER_LETTER_SYSTEM_PROMPT, COVER_LETTER_PROMPT


def generate_cover_letter(resume_text: str, job_description: str, model: str = "gpt-4o") -> dict:
    """
    Generate a tailored cover letter from a resume and job description.

    Returns:
        dict with keys:
            - "cover_letter": str (the generated cover letter in markdown)
            - "usage": dict with token counts and timing
    """
    client = get_client()

    user_prompt = COVER_LETTER_PROMPT.format(
        resume=resume_text,
        job_description=job_description
    )

    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": COVER_LETTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    elapsed = time.time() - start_time
    raw_content = response.choices[0].message.content

    if raw_content is None:
        raise RuntimeError(
            "OpenAI returned an empty response. This may be due to content filtering or an API error."
        )

    return {
        "cover_letter": raw_content.strip(),
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "elapsed_seconds": round(elapsed, 2),
            "model": model,
        }
    }

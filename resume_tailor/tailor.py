import os
import time
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, TAILOR_PROMPT


def tailor_resume(resume_text: str, job_description: str, model: str = "gpt-4o") -> dict:
    """
    Sends the resume and job description to OpenAI and returns the tailored result.

    Returns:
        dict with keys:
            - "tailored_resume": str (the rewritten resume markdown)
            - "changes": str (the top 5 changes explanation)
            - "usage": dict with token counts and timing
    """
    client = OpenAI()

    user_prompt = TAILOR_PROMPT.format(
        resume=resume_text,
        job_description=job_description
    )

    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    elapsed = time.time() - start_time
    raw_content = response.choices[0].message.content

    if raw_content is None:
        raise RuntimeError(
            "OpenAI returned an empty response. This may be due to content filtering or an API error. "
            "Try again or check your input for content policy violations."
        )

    tailored_resume = _extract_section(raw_content, "---BEGIN RESUME---", "---END RESUME---")
    changes = _extract_section(raw_content, "---BEGIN CHANGES---", "---END CHANGES---")

    if not tailored_resume:
        tailored_resume = raw_content
        changes = ""

    return {
        "tailored_resume": tailored_resume.strip(),
        "changes": changes.strip(),
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "elapsed_seconds": round(elapsed, 2),
            "model": model,
        }
    }


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    """Extract content between two markers."""
    try:
        start_idx = text.index(start_marker) + len(start_marker)
        end_idx = text.index(end_marker)
        return text[start_idx:end_idx].strip()
    except ValueError:
        return ""

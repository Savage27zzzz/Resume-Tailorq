#!/usr/bin/env python3
"""Launch the Resume Tailor web interface."""

import os
import sys
import logging

from dotenv import load_dotenv


def main():
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Add it to your .env file.", file=sys.stderr)
        sys.exit(1)

    import uvicorn
    print("\U0001f310 Resume Tailor Web starting at http://localhost:8000")
    uvicorn.run("resume_tailor.web:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

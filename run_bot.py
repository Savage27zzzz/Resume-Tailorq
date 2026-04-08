#!/usr/bin/env python3
"""Launch the Resume Tailor Telegram bot."""

import os
import sys
import logging

from dotenv import load_dotenv

from resume_tailor.bot import create_bot_app


def main():
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set. Add it to your .env file.", file=sys.stderr)
        sys.exit(1)

    provider = os.environ.get("AI_PROVIDER", "openai").lower()
    if provider == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            print("Error: GEMINI_API_KEY not set. Add it to your .env file.", file=sys.stderr)
            sys.exit(1)
    else:
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not set. Add it to your .env file.", file=sys.stderr)
            sys.exit(1)

    print("🤖 Resume Tailor Bot starting...")
    app = create_bot_app(token)
    app.run_polling()


if __name__ == "__main__":
    main()

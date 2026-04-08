import asyncio
import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .tailor import tailor_resume

logger = logging.getLogger(__name__)

WAITING_RESUME = 0
WAITING_JOB = 1

ALLOWED_EXTENSIONS = (".txt", ".md")


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """Split text into chunks that respect Telegram's message limit, breaking at newlines."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_idx = text.rfind("\n", 0, max_length)
        if split_idx == -1:
            split_idx = max_length
        chunks.append(text[:split_idx])
        text = text[split_idx:].lstrip("\n")
    return [c for c in chunks if c]


async def _read_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Download an uploaded document and return its text content, or None on failure."""
    doc = update.message.document
    file_name = doc.file_name or ""
    lower_name = file_name.lower()

    if lower_name.endswith(".pdf"):
        await update.message.reply_text(
            "⚠️ PDF support is not yet available. Please paste your text directly or upload a `.txt` / `.md` file.",
            parse_mode="Markdown",
        )
        return None

    if not any(lower_name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        await update.message.reply_text(
            "⚠️ Unsupported file type. Please upload a `.txt` or `.md` file.",
            parse_mode="Markdown",
        )
        return None

    tg_file = await doc.get_file()
    data = await tg_file.download_as_bytearray()
    return data.decode("utf-8")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Resume Tailor Bot*\n\n"
        "I rewrite your resume to match a specific job description using AI.\n\n"
        "*How to use:*\n"
        "1. Send /tailor to start\n"
        "2. Send me your resume (paste text or upload a .txt/.md file)\n"
        "3. Send me the job description\n"
        "4. Get your tailored resume back!\n\n"
        "Send /tailor to begin.",
        parse_mode="Markdown",
    )


async def tailor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "📄 Send me your *resume*.\n\n"
        "You can paste it as text or upload a `.txt` or `.md` file.",
        parse_mode="Markdown",
    )
    return WAITING_RESUME


async def receive_resume_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["resume"] = update.message.text
    await update.message.reply_text(
        "✅ Got your resume!\n\n"
        "Now send me the *job description*. Paste it as text or upload a file.",
        parse_mode="Markdown",
    )
    return WAITING_JOB


async def receive_resume_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = await _read_document(update, context)
    if text is None:
        return WAITING_RESUME

    context.user_data["resume"] = text
    await update.message.reply_text(
        "✅ Got your resume!\n\n"
        "Now send me the *job description*. Paste it as text or upload a file.",
        parse_mode="Markdown",
    )
    return WAITING_JOB


async def _process_tailoring(update: Update, context: ContextTypes.DEFAULT_TYPE, job_text: str):
    """Run the tailoring logic and send results back to the user."""
    resume_text = context.user_data.get("resume", "")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")

    await update.message.reply_text("⏳ Tailoring your resume...")

    try:
        result = await asyncio.to_thread(tailor_resume, resume_text, job_text, model)
    except RuntimeError as exc:
        logger.error("OpenAI RuntimeError: %s", exc)
        await update.message.reply_text(
            "⚠️ The AI returned an empty response. This may be due to content filtering or an API error. "
            "Please try again with /tailor."
        )
        context.user_data.clear()
        return ConversationHandler.END
    except Exception:
        logger.exception("Unexpected error during tailoring")
        await update.message.reply_text(
            "Something went wrong. Please try again with /tailor"
        )
        context.user_data.clear()
        return ConversationHandler.END

    for chunk in split_message(result["tailored_resume"]):
        await update.message.reply_text(chunk)

    if result["changes"]:
        for chunk in split_message(result["changes"]):
            await update.message.reply_text(chunk)

    context.user_data.clear()
    return ConversationHandler.END


async def receive_job_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _process_tailoring(update, context, update.message.text)


async def receive_job_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = await _read_document(update, context)
    if text is None:
        return WAITING_JOB
    return await _process_tailoring(update, context, text)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. Send /tailor to start again.")
    return ConversationHandler.END


def create_bot_app(token: str) -> Application:
    """Create and configure the Telegram bot application."""
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("tailor", tailor_command)],
        states={
            WAITING_RESUME: [
                MessageHandler(filters.Document.ALL, receive_resume_document),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_resume_text),
            ],
            WAITING_JOB: [
                MessageHandler(filters.Document.ALL, receive_job_document),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_job_text),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(conv_handler)

    return app

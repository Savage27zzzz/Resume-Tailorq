"""Vercel serverless entry point for the FastAPI web app."""

from dotenv import load_dotenv
load_dotenv()

from resume_tailor.web import app

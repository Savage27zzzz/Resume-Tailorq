FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run the Telegram bot
# Override with: docker run <image> python run_web.py
CMD ["python", "run_bot.py"]

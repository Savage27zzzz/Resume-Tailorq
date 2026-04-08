# Resume-Tailor

A Python CLI tool that uses OpenAI to intelligently rewrite your resume for a specific job description. It maximizes keyword alignment, reorders experience by relevance, quantifies achievements, and optimizes for ATS — while keeping your authentic voice intact.

## Features

- **AI-powered tailoring** — rewrites your resume to mirror the language and requirements of a target job posting
- **ATS optimization** — matches keywords, action verbs, and phrasing from the job description
- **Change transparency** — outputs the top 5 changes made and explains why each was applied
- **Markdown in, markdown out** — reads and writes clean markdown resumes
- **Configurable model** — use any OpenAI chat model (`gpt-4o`, `gpt-4o-mini`, etc.)
- **Verbose mode** — view token usage, cost estimates, and timing stats

## Prerequisites

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Installation

```bash
git clone https://github.com/Savage27zzzz/Resume-Tailorq.git
cd Resume-Tailorq

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

```bash
python -m resume_tailor --resume <resume_file> --job <job_description_file>
```

### Arguments

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--resume` | `-r` | Yes | Path to your current resume (markdown or plain text) |
| `--job` | `-j` | Yes | Path to the target job description (text file) |
| `--output` | `-o` | No | Output file path (default: `output/tailored_resume.md`) |
| `--model` | `-m` | No | OpenAI model to use (default: `OPENAI_MODEL` env var or `gpt-4o`) |
| `--verbose` | `-v` | No | Print token usage and timing info |

### Examples

Basic usage with the included samples:

```bash
python -m resume_tailor -r examples/sample_resume.md -j examples/sample_job_description.txt
```

Specify an output path and model:

```bash
python -m resume_tailor \
  -r my_resume.md \
  -j job_posting.txt \
  -o tailored_resume.md \
  -m gpt-4o-mini
```

Verbose mode for debugging:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt -v
```

## Telegram Bot

You can also use Resume Tailor as a Telegram bot.

### Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram and copy the token
2. Add the token to your `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your-token-here
   ```
3. Start the bot:
   ```bash
   python run_bot.py
   ```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and usage instructions |
| `/tailor` | Start a new resume tailoring session |
| `/help` | Show usage instructions |
| `/cancel` | Cancel the current session |

### How It Works

1. Send `/tailor` to the bot
2. Paste your resume as text or upload a `.txt`, `.md`, or `.pdf` file
3. Paste the job description or upload a file
4. The bot returns your tailored resume and a summary of changes

## Web Interface

A browser-based UI for resume tailoring.

### Setup

```bash
python run_web.py
```

Then open http://localhost:8000 in your browser.

### Features

- Paste or upload your resume and job description
- One-click resume tailoring
- Optional cover letter generation
- Optional ATS keyword score analysis
- Copy results to clipboard

## Example Output

```
============================================================
TAILORED RESUME
============================================================
# Alex Chen
**Senior Software Engineer** | San Francisco, CA
...

============================================================
CHANGES MADE
============================================================
## CHANGES MADE

1. **Reframed Summary for Platform Engineering**: Rewrote the professional
   summary to emphasize microservices, TypeScript, and cloud-native
   architecture — key terms from the job posting.

2. **Added Quantified Impact Metrics**: Transformed vague bullet points
   into measurable achievements (e.g., "reduced query latency by 40%",
   "serving 2M+ requests/day").
...

✅ Tailored resume saved to: output/tailored_resume.md
```

## How It Works

1. **Parse inputs** — reads your resume and the target job description from disk
2. **Build prompt** — constructs a detailed prompt pairing your resume with the job posting, guided by a system prompt that encodes expert recruiter heuristics
3. **Call OpenAI** — sends the prompt to the specified model and receives a tailored resume plus a change summary
4. **Extract sections** — parses the structured response using `---BEGIN/END---` markers to cleanly separate the resume from the change log
5. **Write output** — saves the tailored resume to disk and prints both the resume and change summary to stdout

## Configuration

Environment variables (set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Default model when `--model` is not passed |

## License

MIT

# Resume-Tailor

A Python CLI tool that uses OpenAI to intelligently rewrite your resume for a specific job description. It maximizes keyword alignment, reorders experience by relevance, quantifies achievements, and optimizes for ATS — while keeping your authentic voice intact.

> **💡 Free to use!** Set `AI_PROVIDER=gemini` with a [free Gemini API key](https://aistudio.google.com/apikey) — no credit card required.

## Features

- **AI-powered tailoring** — rewrites your resume to mirror the language and requirements of a target job posting
- **Cover letter generation** — generates a tailored cover letter from your resume and the job description
- **ATS keyword scoring** — computes keyword overlap between your resume and the job description (before and after tailoring)
- **Export to PDF and DOCX** — save your tailored resume and cover letter as formatted PDF or DOCX files
- **ATS optimization** — matches keywords, action verbs, and phrasing from the job description
- **Change transparency** — outputs the top 5 changes made and explains why each was applied
- **Markdown in, markdown out** — reads and writes clean markdown resumes
- **Configurable model** — use any OpenAI chat model (`gpt-4o`, `gpt-4o-mini`, etc.) or Google Gemini (`gemini-2.0-flash`)
- **Verbose mode** — view token usage, cost estimates, and timing stats

## Prerequisites

- Python 3.9+
- An AI API key (choose one):
  - [OpenAI API key](https://platform.openai.com/api-keys) (paid)
  - [Google Gemini API key](https://aistudio.google.com/apikey) (free tier available)

## Installation

```bash
git clone https://github.com/Savage27zzzz/Resume-Tailorq.git
cd Resume-Tailorq

pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   For OpenAI: set AI_PROVIDER=openai and OPENAI_API_KEY=your-key
#   For Gemini (free): set AI_PROVIDER=gemini and GEMINI_API_KEY=your-key
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
| `--cover-letter` | `-c` | No | Also generate a tailored cover letter (saved to `output/cover_letter.md`) |
| `--ats-score` | `-a` | No | Show ATS keyword match score before and after tailoring |
| `--format` | `-f` | No | Output format: `md` (default), `pdf`, or `docx` |

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

Generate a cover letter alongside the tailored resume:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt --cover-letter
```

Show ATS keyword score before and after tailoring:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt --ats-score
```

Combine all features:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt -a -c -v
```

Export as PDF:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt -f pdf
```

Export as DOCX:

```bash
python -m resume_tailor -r my_resume.md -j job_posting.txt -f docx
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
| `/coverletter` | Generate a tailored cover letter |
| `/ats` | Check your ATS keyword score |
| `/help` | Show usage instructions |
| `/cancel` | Cancel the current session |

### How It Works

1. Send `/tailor`, `/coverletter`, or `/ats` to the bot
2. Paste your resume as text or upload a `.txt`, `.md`, or `.pdf` file
3. Paste the job description or upload a file
4. The bot returns your tailored resume, cover letter, or ATS score

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

### ATS Score Output

```
============================================================
ATS KEYWORD SCORE
============================================================
Before tailoring:  42.3% (22/52 keywords)
After tailoring:   87.5% (45/52 keywords)
Improvement:       +45.2%

Missing keywords: terraform, aws cdk, graphql, websockets, pub/sub, event-driven, observability
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
| `AI_PROVIDER` | `openai` | AI backend: `openai` or `gemini` |
| `OPENAI_API_KEY` | *(required for openai)* | Your OpenAI API key |
| `GEMINI_API_KEY` | *(required for gemini)* | Your Google Gemini API key ([free](https://aistudio.google.com/apikey)) |
| `AI_MODEL` | auto | Model override (default: `gpt-4o` for OpenAI, `gemini-2.0-flash` for Gemini) |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token from @BotFather |
| `RATE_LIMIT_PER_HOUR` | `20` | Max API requests per IP per hour (web UI only) |

## Deployment

### Web UI on Vercel

1. Fork or push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repository
3. Add environment variables in the Vercel dashboard:
   - `OPENAI_API_KEY` — your OpenAI API key
   - `OPENAI_MODEL` — model to use (default: `gpt-4o`)
   - `RATE_LIMIT_PER_HOUR` — max requests per IP per hour (default: `20`)
4. Deploy — Vercel auto-detects the config from `vercel.json`

### Telegram Bot on Railway

1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repo
3. Add environment variables:
   - `OPENAI_API_KEY` — your OpenAI API key
   - `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
   - `OPENAI_MODEL` — model to use (default: `gpt-4o`)
4. Railway auto-detects the Dockerfile and deploys

### Docker (anywhere)

```bash
docker build -t resume-tailor .

# Run Telegram bot
docker run -d --env-file .env resume-tailor

# Run web UI instead
docker run -d --env-file .env -p 8000:8000 resume-tailor python run_web.py
```

## License

MIT

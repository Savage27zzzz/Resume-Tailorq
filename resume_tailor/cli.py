import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .tailor import tailor_resume


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Tailor your resume to match a specific job description using AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m resume_tailor -r my_resume.md -j job_posting.txt
  python -m resume_tailor -r my_resume.md -j job_posting.txt -o tailored.md
  python -m resume_tailor -r my_resume.md -j job_posting.txt -m gpt-4o -v
        """
    )

    parser.add_argument("-r", "--resume", required=True, help="Path to your current resume (markdown or text)")
    parser.add_argument("-j", "--job", required=True, help="Path to the target job description (text)")
    parser.add_argument("-o", "--output", default="output/tailored_resume.md", help="Output file path (default: output/tailored_resume.md)")
    parser.add_argument("-m", "--model", default=None, help="OpenAI model (default: OPENAI_MODEL env var or gpt-4o)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print token usage and timing info")

    args = parser.parse_args()

    if not os.path.isfile(args.resume):
        print(f"Error: Resume file not found: {args.resume}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.job):
        print(f"Error: Job description file not found: {args.job}", file=sys.stderr)
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Copy .env.example to .env and add your key.", file=sys.stderr)
        sys.exit(1)

    resume_text = Path(args.resume).read_text(encoding="utf-8")
    job_text = Path(args.job).read_text(encoding="utf-8")

    model = args.model or os.environ.get("OPENAI_MODEL", "gpt-4o")

    print(f"🔄 Tailoring resume for job description using {model}...\n")

    result = tailor_resume(resume_text, job_text, model)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    full_output = result["tailored_resume"]
    if result["changes"]:
        full_output += "\n\n---\n\n" + result["changes"]

    output_path.write_text(full_output, encoding="utf-8")

    print("=" * 60)
    print("TAILORED RESUME")
    print("=" * 60)
    print(result["tailored_resume"])
    print()

    if result["changes"]:
        print("=" * 60)
        print("CHANGES MADE")
        print("=" * 60)
        print(result["changes"])
        print()

    print(f"✅ Tailored resume saved to: {args.output}")

    if args.verbose:
        usage = result["usage"]
        print(f"\n📊 Usage Stats:")
        print(f"   Model: {usage['model']}")
        print(f"   Prompt tokens: {usage['prompt_tokens']}")
        print(f"   Completion tokens: {usage['completion_tokens']}")
        print(f"   Total tokens: {usage['total_tokens']}")
        print(f"   Time: {usage['elapsed_seconds']}s")


if __name__ == "__main__":
    main()

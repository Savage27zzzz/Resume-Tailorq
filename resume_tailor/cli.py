import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .client import get_default_model
from .tailor import tailor_resume
from .cover_letter import generate_cover_letter
from .ats_score import compute_ats_score
from .export import markdown_to_docx, markdown_to_pdf


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
  python -m resume_tailor -r my_resume.md -j job_posting.txt --ats-score
  python -m resume_tailor -r my_resume.md -j job_posting.txt --cover-letter
  python -m resume_tailor -r my_resume.md -j job_posting.txt -a -c -v
  python -m resume_tailor -r my_resume.md -j job_posting.txt -f pdf
  python -m resume_tailor -r my_resume.md -j job_posting.txt -f docx
        """
    )

    parser.add_argument("-r", "--resume", required=True, help="Path to your current resume (markdown or text)")
    parser.add_argument("-j", "--job", required=True, help="Path to the target job description (text)")
    parser.add_argument("-o", "--output", default="output/tailored_resume.md", help="Output file path (default: output/tailored_resume.md)")
    parser.add_argument("-m", "--model", default=None, help="OpenAI model (default: OPENAI_MODEL env var or gpt-4o)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print token usage and timing info")
    parser.add_argument("-c", "--cover-letter", action="store_true", help="Also generate a tailored cover letter")
    parser.add_argument("-a", "--ats-score", action="store_true", help="Show ATS keyword match score before and after tailoring")
    parser.add_argument("-f", "--format", choices=["md", "pdf", "docx"], default="md",
                        help="Output format: md (default), pdf, or docx")

    args = parser.parse_args()

    if not os.path.isfile(args.resume):
        print(f"Error: Resume file not found: {args.resume}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.job):
        print(f"Error: Job description file not found: {args.job}", file=sys.stderr)
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

    resume_text = Path(args.resume).read_text(encoding="utf-8")
    job_text = Path(args.job).read_text(encoding="utf-8")

    model = args.model or get_default_model()

    if args.ats_score:
        before_ats = compute_ats_score(resume_text, job_text)

    print(f"🔄 Tailoring resume for job description using {model}...\n")

    result = tailor_resume(resume_text, job_text, model)

    output_path = Path(args.output)

    if args.format == "pdf":
        output_path = output_path.with_suffix(".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_bytes = markdown_to_pdf(result["tailored_resume"])
        output_path.write_bytes(pdf_bytes)
    elif args.format == "docx":
        output_path = output_path.with_suffix(".docx")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        docx_bytes = markdown_to_docx(result["tailored_resume"])
        output_path.write_bytes(docx_bytes)
    else:
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

    print(f"✅ Tailored resume saved to: {output_path}")

    if args.verbose:
        usage = result["usage"]
        print(f"\n📊 Usage Stats:")
        print(f"   Model: {usage['model']}")
        print(f"   Prompt tokens: {usage['prompt_tokens']}")
        print(f"   Completion tokens: {usage['completion_tokens']}")
        print(f"   Total tokens: {usage['total_tokens']}")
        print(f"   Time: {usage['elapsed_seconds']}s")

    if args.ats_score:
        after_ats = compute_ats_score(result["tailored_resume"], job_text)
        improvement = after_ats["score"] - before_ats["score"]

        print()
        print("=" * 60)
        print("ATS KEYWORD SCORE")
        print("=" * 60)
        print(f"Before tailoring:  {before_ats['score']}% ({len(before_ats['matched_keywords'])}/{before_ats['total_jd_keywords']} keywords)")
        print(f"After tailoring:   {after_ats['score']}% ({len(after_ats['matched_keywords'])}/{after_ats['total_jd_keywords']} keywords)")
        print(f"Improvement:       +{improvement}%")

        if after_ats["missing_keywords"]:
            print(f"\nMissing keywords: {', '.join(after_ats['missing_keywords'])}")

    if args.cover_letter:
        print(f"\n🔄 Generating cover letter using {model}...\n")

        cl_result = generate_cover_letter(resume_text, job_text, model)

        output_dir = output_path.parent
        if args.format == "pdf":
            cl_output_path = output_dir / "cover_letter.pdf"
            cl_output_path.write_bytes(markdown_to_pdf(cl_result["cover_letter"]))
        elif args.format == "docx":
            cl_output_path = output_dir / "cover_letter.docx"
            cl_output_path.write_bytes(markdown_to_docx(cl_result["cover_letter"]))
        else:
            cl_output_path = output_dir / "cover_letter.md"
            cl_output_path.write_text(cl_result["cover_letter"], encoding="utf-8")

        print("=" * 60)
        print("COVER LETTER")
        print("=" * 60)
        print(cl_result["cover_letter"])
        print()
        print(f"✅ Cover letter saved to: {cl_output_path}")

        if args.verbose:
            cl_usage = cl_result["usage"]
            print(f"\n📊 Cover Letter Usage Stats:")
            print(f"   Model: {cl_usage['model']}")
            print(f"   Prompt tokens: {cl_usage['prompt_tokens']}")
            print(f"   Completion tokens: {cl_usage['completion_tokens']}")
            print(f"   Total tokens: {cl_usage['total_tokens']}")
            print(f"   Time: {cl_usage['elapsed_seconds']}s")


if __name__ == "__main__":
    main()

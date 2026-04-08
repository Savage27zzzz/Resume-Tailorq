import re
from collections import Counter


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Compute ATS keyword match score between resume and job description.

    Returns:
        dict with keys:
            - "score": float (0-100 percentage)
            - "matched_keywords": list[str] (keywords found in both)
            - "missing_keywords": list[str] (JD keywords not in resume)
            - "total_jd_keywords": int
    """
    jd_keywords = _extract_keywords(job_description)
    resume_keywords = _extract_keywords(resume_text)

    resume_keyword_set = set(resume_keywords.keys())
    jd_keyword_set = set(jd_keywords.keys())

    matched = sorted(jd_keyword_set & resume_keyword_set)
    missing = sorted(jd_keyword_set - resume_keyword_set)

    score = (len(matched) / len(jd_keyword_set) * 100) if jd_keyword_set else 0.0

    return {
        "score": round(score, 1),
        "matched_keywords": matched,
        "missing_keywords": missing,
        "total_jd_keywords": len(jd_keyword_set),
    }


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "can", "shall", "it", "its", "this", "that", "these", "those",
    "i", "you", "we", "they", "he", "she", "me", "us", "them", "my", "your",
    "our", "their", "his", "her", "who", "what", "which", "when", "where", "how",
    "not", "no", "nor", "as", "if", "then", "than", "too", "very", "just",
    "about", "up", "out", "so", "also", "into", "over", "after", "before",
    "between", "through", "during", "above", "below", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "only", "own",
    "same", "well", "back", "even", "still", "new", "now", "way", "use",
    "work", "working", "including", "ability", "strong", "experience",
    "etc", "eg", "ie", "years", "year", "must", "required", "preferred",
}


def _extract_keywords(text: str) -> Counter:
    """Extract meaningful keywords from text, filtering stop words and short tokens."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())
    filtered = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
    return Counter(filtered)

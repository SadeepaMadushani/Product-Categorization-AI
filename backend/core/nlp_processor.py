from typing import List
import re


class NLPProcessor:
    """Simple NLP utilities: NER (rule-based), summarization, and preprocessing."""

    def extract_nouns(self, text: str) -> List[str]:
        words = re.findall(r"[A-Za-z]+", text or "")
        # naive nouns: words longer than 3 chars
        return [w.lower() for w in words if len(w) > 3]

    def extract_adjectives(self, text: str) -> List[str]:
        # naive adjectives: words ending with common adjective suffixes
        words = re.findall(r"[A-Za-z]+", text or "")
        return [w.lower() for w in words if w.lower().endswith(("y", "ful", "ous", "ive"))]

    def ner_entities(self, text: str) -> List[str]:
        # naive NER: capitalized tokens considered entities
        return re.findall(r"\b[A-Z][a-zA-Z]+\b", text or "")

    def summarize(self, text: str, max_sentences: int = 2) -> str:
        # naive extractive summary: first N sentences
        sentences = re.split(r"(?<=[.!?])\s+", text or "")
        return " ".join(sentences[:max_sentences]).strip()

    # Compatibility aliases used by agents
    def extract_entities(self, text: str) -> List[str]:
        return self.ner_entities(text)

    def preprocess_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").lower()).strip()



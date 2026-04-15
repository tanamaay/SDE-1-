from openai import OpenAI

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def summarize(self, text: str) -> str:
        if not text:
            return "No content available to summarize."
        if not self.client:
            return f"Summary: {text[:220]}"
        return self._summarize_with_openai(text)

    def answer_question(self, context: str, question: str) -> str:
        context_slice = context[:10000] if context else "No context"
        if not self.client:
            return f"Based on uploaded content: {context_slice[:320]}. Answer to question '{question}'."
        return self._answer_with_openai(context_slice, question)

    def _summarize_with_openai(self, text: str) -> str:  # pragma: no cover - external API branch
        response = self.client.chat.completions.create(
            model=settings.model_name,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Summarize content in 3-5 concise bullet points."},
                {"role": "user", "content": text[:12000]},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _answer_with_openai(self, context_slice: str, question: str) -> str:  # pragma: no cover
        response = self.client.chat.completions.create(
            model=settings.model_name,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": "You answer questions strictly from provided context and include exact seconds like '12.5s' if relevant.",
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_slice}\n\nQuestion: {question}",
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()

import asyncio
import os

from .reranker import rerank_documents


class RAGService:
    def __init__(self):
        self.model_name = os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-flash")

    def _format_context(self, documents):
        if not documents:
            return "No relevant context was found in the knowledge base."

        parts = []
        for index, document in enumerate(documents, 1):
            source = document.metadata.get("source", "unknown")
            department = document.metadata.get("department", "unknown")
            parts.append(f"[{index}] source={source} department={department}\n{document.page_content}")
        return "\n\n".join(parts)

    async def generate_answer(self, user_prompt, user_profile, documents):
        reranked_documents = await rerank_documents(user_prompt, documents, top_k=4)
        context = self._format_context(reranked_documents)
        sources = []
        for document in reranked_documents:
            source = document.metadata.get("source")
            if source and source not in sources:
                sources.append(source)

        answer = await asyncio.to_thread(self._generate_with_model, user_prompt, user_profile, context)
        return {
            "answer": answer,
            "sources": sources,
            "context": context,
        }

    def _generate_with_model(self, user_prompt, user_profile, context):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.2)
            messages = [
                SystemMessage(content=(
                    "You are a retrieval assistant. Use the provided context only. "
                    "If the answer is not in the context, say you could not find it."
                )),
                HumanMessage(content=(
                    f"User profile: {user_profile}\n\n"
                    f"Context:\n{context}\n\n"
                    f"Question: {user_prompt}"
                )),
            ]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print(e)
            return (
                f"I found the following relevant context for your question:\n\n{context}\n\n"
                f"Based on that, I could not generate a model-backed answer."
            )


ragsvc = RAGService()
import asyncio


def cross_encoder_rerank(query, documents, top_k=4):
    """Rerank retrieved documents with a cross-encoder model."""
    if not documents:
        return []

    try:
        from sentence_transformers import CrossEncoder

        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        reranker = CrossEncoder(model_name)
        pairs = [(query, document.page_content) for document in documents]
        scores = reranker.predict(pairs)
        ranked_documents = [document for _, document in sorted(zip(scores, documents), key=lambda item: item[0], reverse=True)]
        return ranked_documents[:top_k]
    except Exception:
        return documents[:top_k]


async def llm_rerank(query, documents, top_k=4):
    """Future LLM-based reranking implementation."""
    # The implementation below is intentionally commented out for future use.
    # It can be enabled when an LLM-backed reranking strategy is required.
    #
    # try:
    #     from langchain_google_genai import ChatGoogleGenerativeAI
    #     from langchain_core.messages import HumanMessage, SystemMessage
    #
    #     llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
    #     prompt = """
    #     Rank the following documents by relevance to the user query.
    #     Return only the document numbers in descending relevance order.
    #     Query: {query}
    #     Documents:
    #     {documents}
    #     """
    #     document_text = "\n\n".join(
    #         f"{index + 1}. {document.page_content}" for index, document in enumerate(documents)
    #     )
    #     response = llm.invoke([
    #         SystemMessage(content="You are a document reranking assistant."),
    #         HumanMessage(content=prompt.format(query=query, documents=document_text)),
    #     ])
    #     ranked_indexes = [int(item.strip()) - 1 for item in response.content.split(',') if item.strip().isdigit()]
    #     ranked_documents = [documents[index] for index in ranked_indexes if 0 <= index < len(documents)]
    #     return ranked_documents[:top_k]
    # except Exception:
    #     return documents[:top_k]
    return documents[:top_k]


async def rerank_documents(query, documents, top_k=4):
    """Apply cross-encoder reranking for the current pipeline."""
    return await asyncio.to_thread(cross_encoder_rerank, query, documents, top_k)
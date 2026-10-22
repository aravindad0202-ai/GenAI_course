from dotenv import load_dotenv
load_dotenv(r'D:\IT\AI\teaching\GenAI_course\.env')

from langchain_core.documents import Document

docs = [
        Document(
            page_content="Vector databases store data as high-dimensional arrays.", 
            metadata={"category": "vector_db", "author": "Alice", "id": "doc_1"}
        ),
        Document(
            page_content="Relational databases are best for transactional integrity.", 
            metadata={"category": "rdbms", "author": "Bob", "id": "doc_2"}
        ),
        Document(
            page_content="Approximate Nearest Neighbor (ANN) enables fast similarity search.", 
            metadata={"category": "algorithms", "author": "Alice", "id": "doc_3"}
        )
    ]

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


from langchain_chroma import Chroma

namespace_name = "project_alpha_docs"


def embedor():
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=namespace_name,
        persist_directory=r"D:\IT\AI\teaching\GenAI_course\Day_4" # Saves data to this local folder
    )

def retrievel():
    namespace_name = "project_alpha_docs"
    vectorstore = Chroma(
        collection_name=namespace_name,
        embedding_function=embeddings,
        persist_directory=r"D:\IT\AI\teaching\GenAI_course\Day_4\local_gemini_chroma"
    )

    search_query = "How do we search for similar vectors?"

    results = vectorstore.similarity_search_with_score(query=search_query, k=2)
    print(results)

    for i, (doc, score) in enumerate(results):
            print(f"{i+1}. Document: {doc.page_content}")
            print(f"   Metadata: {doc.metadata}")
            print(f"   Distance Score: {score:.4f}\n")

retrievel()
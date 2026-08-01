from embedding import generate_embedding
from prompts import QA_PROMPT
from llm import generate_response
from chroma_client import chunks_collection
def search_chunks(question: str, pdf_id: int, top_k: int = 5):
    question_embedding = generate_embedding(question)
    results = chunks_collection.query(query_embeddings=[question_embedding], n_results=top_k, where={'pdf_id': pdf_id})
    return results['documents'][0]
def ask_pdf(question:str,pdf_id:int,user_id):
    chunks = search_chunks(question,pdf_id)
    context= '\n\n'.join(chunks)
    prompt  = QA_PROMPT.format(context =context,question= question)
    answer = generate_response(prompt)
    return answer
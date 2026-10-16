from rag.config import emb,CHAT_MODEL
from rag.indexer import vector_store
from rag.retriever import retriever_data

#llm
def generate_text(question):
    vector_store()
    result=retriever_data(question)
    context="\n".join(result["documents"][0])
    prompt=f"""You are a TicketFlow support assistant. Answer the question using the context below. Only say "I don't know" if the context has nothing related.
Context:
{context}
Question: {question}"""
    resp=emb.chat.complete(model=CHAT_MODEL,messages=[{"role":"user","content":prompt}])
    pages=sorted({m["page"] for m in result["metadatas"][0]})
    return {"answer":resp.choices[0].message.content,"sources":pages}

from rag.config import emb,collection,EMBED_MODEL

# Input/Question
def retriever_data(question,n=3):
    q_emb=emb.embeddings.create(model=EMBED_MODEL,inputs=[question]).data[0].embedding
    return collection.query(query_embeddings=[q_emb],n_results=n)

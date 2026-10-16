from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.config import emb,collection,PDF_PATH,EMBED_MODEL

# loader
def doc_loader(path=PDF_PATH):
    return PyPDFLoader(path).load()

# chunking
def doc_chunking(docs):
    chunks=RecursiveCharacterTextSplitter(chunk_size=800,chunk_overlap=120,separators=["\n\n","\n"," ",""])
    return chunks.split_documents(docs)

#vector embedding
def vector_emb(texts):
    chunks_emb=emb.embeddings.create(model=EMBED_MODEL,inputs=texts)
    return [d.embedding for d in chunks_emb.data]

#vector storing 
def vector_store():
    if collection.count()>0:
        return
    chunks=doc_chunking(doc_loader())
    texts=[c.page_content for c in chunks]
    collection.upsert(
        ids=[str(i) for i in range(len(texts))],
        documents=texts,
        embeddings=vector_emb(texts),
        metadatas=[{"page":c.metadata["page"]+1} for c in chunks],
    )

from schemas import settings
import chromadb
from mistralai.client import Mistral
from mistralai.client.utils import RetryConfig, BackoffStrategy

PDF_PATH="TicketFlow_Policies.pdf"
EMBED_MODEL="mistral-embed"
CHAT_MODEL="ministral-8b-latest"

db=chromadb.PersistentClient(path="chroma_db")
collection=db.get_or_create_collection("policies")
retry=RetryConfig("backoff", BackoffStrategy(1000, 10000, 2.0, 60000), retry_connection_errors=True)
emb=Mistral(api_key=settings.MISTRAL_API_KEY, retry_config=retry)

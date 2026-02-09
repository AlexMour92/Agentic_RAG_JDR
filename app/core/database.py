import chromadb
import torch
from chromadb.utils import embedding_functions
from .config import settings

chroma_client = chromadb.PersistentClient(path=settings.DB_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=settings.EMBEDDING_MODEL,
    device="cuda" if torch.cuda.is_available() else "cpu",
)

events_collection = chroma_client.get_collection(
    name="events", embedding_function=embedding_fn
)
entities_collection = chroma_client.get_collection(
    name="entities", embedding_function=embedding_fn
)
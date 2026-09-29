import asyncio
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from dotenv import load_dotenv
from langchain_postgres import PGEngine, PGVectorStore
from embeddings import get_embeddings

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
TABLE_NAME = "smart_shopper_knowledge"

if not DATABASE_URL:
    raise ValueError(f'DATABASE_URL tidak ditemukan di .env')

engine = PGEngine.from_connection_string(
    url=DATABASE_URL
)


def get_vector_store():
    return PGVectorStore.create_sync(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=get_embeddings()
    )
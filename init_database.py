from database import engine, TABLE_NAME
from embeddings import get_embeddings


def main():
    embeddings = get_embeddings()

    sample_vector = embeddings.embed_query("test")
    vector_size = len(sample_vector)

    print(f"Embedding vector size: {vector_size}")

    engine.init_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=vector_size
    )

    print(f"Table '{TABLE_NAME}' berhasil dibuat.")


if __name__ == "__main__":
    main()
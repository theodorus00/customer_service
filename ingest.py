from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
import json

import pandas as pd
from langchain_core.documents import Document

from database import get_vector_store


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "customer_service_prepared.csv"

BATCH_SIZE = 64


def main():
    df = pd.read_csv(DATA_PATH, keep_default_na=False)

    required_columns = {
        "record_id",
        "prompt",
        "response",
        "has_placeholder",
        "review_status",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Kolom tidak ditemukan: {missing_columns}")

    # Hindari memasukkan pasangan yang sama persis dua kali.
    df = df.drop_duplicates(subset=["prompt", "response"])

    if df["prompt"].str.strip().eq("").any():
        raise ValueError("Ada prompt kosong. Periksa CSV terlebih dahulu.")

    print(f"Jumlah data: {len(df)}")
    print("Menghubungkan ke vector store...", flush=True)

    vector_store = get_vector_store()

    total_added = 0
    total_skipped = 0

    for start in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[start:start + BATCH_SIZE]

        documents = []
        ids = []

        for _, row in batch.iterrows():
            # ID tetap sama untuk pasangan prompt-response yang sama.
            identity = json.dumps(
                [row["prompt"], row["response"]],
                ensure_ascii=False,
            )

            document_id = str(
                uuid5(NAMESPACE_URL, f"smartshopper:cs:{identity}")
            )

            documents.append(
                Document(
                    id=document_id,
                    page_content=row["prompt"],
                    metadata={
                        "record_id": row["record_id"],
                        "response": row["response"],
                        "has_placeholder": (
                            str(row["has_placeholder"]).lower() == "true"
                        ),
                        "review_status": row["review_status"],
                        "source": DATA_PATH.name,
                        "source_type": "customer_service_example",
                    },
                )
            )

            ids.append(document_id)

        # Lewati dokumen yang sudah tersimpan.
        existing_documents = vector_store.get_by_ids(ids)
        existing_ids = {doc.id for doc in existing_documents}

        new_pairs = [
            (doc, doc_id)
            for doc, doc_id in zip(documents, ids)
            if doc_id not in existing_ids
        ]

        if new_pairs:
            vector_store.add_documents(
                documents=[doc for doc, _ in new_pairs],
                ids=[doc_id for _, doc_id in new_pairs],
            )

        total_added += len(new_pairs)
        total_skipped += len(documents) - len(new_pairs)

        processed = min(start + BATCH_SIZE, len(df))

        print(
            f"Progress: {processed}/{len(df)} | "
            f"Ditambahkan: {total_added} | "
            f"Sudah ada: {total_skipped}",
            flush=True,
        )

    print("\nIngestion selesai!")

if __name__ == "__main__":
    main()
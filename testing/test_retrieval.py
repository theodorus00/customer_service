from database import get_vector_store

def main(): 
    vector_store = get_vector_store()

    while True:
        question = input(
            "\nMasukkan pertanyaan (ketik 'exit' untuk keluar): "
        )
        
        if question.lower() == 'exit':
            break
        
        if not question:
            continue
        
        results = vector_store.similarity_search(
            query=question,
            k=3,
        )

        if not results:
            print("Tidak ada hasil.")
            continue

        for number, doc in enumerate(results, start=1):
            metadata = doc.metadata

            print("\n" + "=" * 60)
            print(f"Hasil #{number}")
            print("Record ID:", metadata.get("record_id"))
            print("Pertanyaan:", doc.page_content)
            print("Contoh jawaban:", metadata.get("response"))
            print("Placeholder:", metadata.get("has_placeholder"))
            print("Status review:", metadata.get("review_status"))

if __name__ == "__main__":
    main()
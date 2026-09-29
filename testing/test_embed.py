from embeddings import get_embeddings

embeddings = get_embeddings()

vector = embeddings.embed_query(
    "Aku mau tukar size baju"
)

print("Vector dimension:", len(vector))
print("First 10 values:", vector[:10])
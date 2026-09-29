from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 

input_path = DATA_DIR / "customer_service.csv"
output_path = DATA_DIR / "customer_service_prepared.csv"

df = pd.read_csv(input_path)

required_columns = {'prompt', 'response'}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(f'Kolom tidak ditemukan : {missing_columns}')

df = df.dropna(subset = ['prompt', 'response']).copy()

for column in ['prompt', 'response']:
    df[column] = df[column].astype(str).str.strip()

df = df[
    df['prompt'].ne("") & df['response'].ne("")
].copy()

# Hapus hanya pasangan pertanyaan-jawaban yang sama persis.
df = df.drop_duplicates(subset=["prompt", "response"])
df = df.reset_index(drop=True)

df["record_id"] = [
    f"CS_{number:05d}"
    for number in range(1, len(df) + 1)
]

df["has_placeholder"] = (
    df["prompt"].str.contains(r"\{\{.*?\}\}", regex=True)
    | df["response"].str.contains(r"\{\{.*?\}\}", regex=True)
)

# Semua contoh tetap perlu ditinjau sebelum dianggap kebijakan toko.
df["review_status"] = "unreviewed"

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("Jumlah data:", len(df))
print("Data dengan placeholder:", df["has_placeholder"].sum())
print("Hasil tersimpan:", output_path)

print("\nContoh data:")
print(df[["record_id", "prompt", "has_placeholder"]].head())
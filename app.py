import logging

import streamlit as st

from rag import ask_customer_assistant


st.set_page_config(
    page_title="Smart Shopper Assistant",
    page_icon="🛍️",
    layout="centered",
)

st.title("🛍️ Smart Shopper Assistant")
st.caption(
    "Tanyakan tentang pembatalan pesanan, refund, "
    "pengiriman, dan layanan pelanggan."
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def display_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        sources = message.get("sources", [])

        if sources:
            with st.expander("Lihat referensi yang ditemukan"):
                st.caption(
                    "Referensi ini berupa contoh percakapan, "
                    "bukan konfirmasi kebijakan resmi toko."
                )

                for source in sources:
                    st.write(f"**{source['record_id']}**")
                    st.write(source["question"])
                    st.caption(
                        f"Status review: {source['review_status']}"
                    )


with st.sidebar:
    st.header("Tentang aplikasi")

    st.write(
        "Demo asisten layanan pelanggan yang mencari "
        "referensi sebelum menyusun jawaban."
    )

    st.info(
        "Belum terhubung ke transaksi atau katalog produk. "
        "Asisten tidak dapat membatalkan pesanan "
        "atau memproses refund secara langsung."
    )

    if st.button("🗑️ Hapus percakapan"):
        st.session_state.messages = []
        st.rerun()


for message in st.session_state.messages:
    display_message(message)


question = st.chat_input("Apa yang ingin kamu tanyakan?")

if question and question.strip():
    question = question.strip()

    user_message = {
        "role": "user",
        "content": question,
    }

    st.session_state.messages.append(user_message)
    display_message(user_message)

    try:
        with st.spinner("Mencari informasi dan menyusun jawaban..."):
            result = ask_customer_assistant(question)

        # Simpan referensi juga agar tetap terlihat setelah rerun.
        sources = [
            {
                "record_id": doc.metadata.get("record_id", "-"),
                "question": doc.page_content,
                "review_status": doc.metadata.get(
                    "review_status", "unreviewed"
                ),
            }
            for doc in result["sources"]
        ]

        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "sources": sources,
        }

    except Exception:
        logging.exception("Gagal menjawab pertanyaan")

        assistant_message = {
            "role": "assistant",
            "content": (
                "Maaf, jawaban belum berhasil diproses. "
                "Silakan coba kembali. "
                "Detail kendala tersedia di terminal VS Code."
            ),
            "sources": [],
        }

    st.session_state.messages.append(assistant_message)
    display_message(assistant_message)
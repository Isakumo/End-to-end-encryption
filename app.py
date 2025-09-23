import streamlit as st
import base64
import json
import os
import time
from crypto_aes_gcm import AESGCMCipher
from key_kem import generate_keypair, encapsulate_key, decapsulate_key
import matplotlib.pyplot as plt
import pandas as pd

RESULTS_FILE = "encryption_results.json"

# --- Encryption / Decryption Helpers ---
def encrypt_file(file_bytes, filename, key):
    cipher = AESGCMCipher(key)
    nonce, encrypted = cipher.encrypt(file_bytes)
    return {
        "type": "file",
        "filename": filename,
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(encrypted).decode(),
    }

def decrypt_file(payload, key):
    cipher = AESGCMCipher(key)
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["ciphertext"])
    decrypted = cipher.decrypt(nonce, ciphertext)
    return decrypted

def encrypt_text(message, key):
    cipher = AESGCMCipher(key)
    nonce, encrypted = cipher.encrypt(message.encode())
    return {
        "type": "text",
        "message": message,
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(encrypted).decode(),
    }

def decrypt_text(payload, key):
    cipher = AESGCMCipher(key)
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["ciphertext"])
    decrypted = cipher.decrypt(nonce, ciphertext)
    return decrypted.decode()

# --- Result storage ---
def save_result(entry):
    results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                results = json.load(f)
            except:
                results = []
    results.append(entry)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- Streamlit UI ---
st.set_page_config(page_title="Multimedia Encryption System", layout="wide")
st.title("🔒 End-to-End Multimedia Encryption System")

option = st.sidebar.radio("Choose Action", ["Send Text", "Send File", "View Results"])

# Generate keypair (for demo, in real system each user has their own)
pk, sk = generate_keypair()
ciphertext_key, shared_secret_sender = encapsulate_key(pk)
shared_secret_receiver = decapsulate_key(sk, ciphertext_key)

if option == "Send Text":
    st.header("📝 Encrypt & Decrypt Text")
    message = st.text_area("Enter your message")
    if st.button("Encrypt & Decrypt"):
        start = time.time()
        payload = encrypt_text(message, shared_secret_sender)
        decrypted = decrypt_text(payload, shared_secret_receiver)
        end = time.time()

        st.success(f"Decrypted Message: {decrypted}")
        st.json(payload)

        save_result({
            "type": "text",
            "message": message,
            "encryption_time": round(end - start, 6)
        })

elif option == "Send File":
    st.header("📂 Encrypt & Decrypt File")
    uploaded_file = st.file_uploader("Upload a file", type=None)
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        if st.button("Encrypt & Decrypt File"):
            start = time.time()
            payload = encrypt_file(file_bytes, filename, shared_secret_sender)
            decrypted_bytes = decrypt_file(payload, shared_secret_receiver)
            end = time.time()

            # Save decrypted file for download
            decrypted_filename = f"decrypted_{filename}"
            with open(decrypted_filename, "wb") as f:
                f.write(decrypted_bytes)

            st.success(f"File decrypted successfully → {decrypted_filename}")
            st.download_button(
                label="⬇️ Download Decrypted File",
                data=decrypted_bytes,
                file_name=decrypted_filename
            )
            st.json(payload)

            save_result({
                "type": "file",
                "filename": filename,
                "encryption_time": round(end - start, 6),
                "size_bytes": len(file_bytes)
            })

elif option == "View Results":
    st.header("📊 Encryption Results")
    results = load_results()
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)

        if "encryption_time" in df:
            fig, ax = plt.subplots()
            df.plot(
                kind="bar",
                x="type",
                y="encryption_time",
                ax=ax,
                legend=False,
                title="Encryption Times"
            )
            st.pyplot(fig)
    else:
        st.warning("No results found yet.")

import argparse
import base64
import json
import socket
from crypto_aes_gcm import AESGCMCipher
from key_kem import generate_keypair, encapsulate_key, decapsulate_key

def start_receiver(receiver_id):
    # Generate keypair
    pk, sk = generate_keypair()
    ciphertext_key, shared_secret_sender = encapsulate_key(pk)
    shared_secret_receiver = decapsulate_key(sk, ciphertext_key)
    cipher = AESGCMCipher(shared_secret_receiver)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 6000 if receiver_id == "R1" else 6001))
    sock.listen(1)
    print(f"Receiver {receiver_id} listening...")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(4096).decode()
        conn.close()

        if not data:
            continue

        payload = json.loads(data)

        if payload["type"] == "text":
            nonce = base64.b64decode(payload["nonce"])
            ciphertext = base64.b64decode(payload["ciphertext"])
            decrypted = cipher.decrypt(nonce, ciphertext).decode()
            print(f"[{receiver_id}] Received text: {decrypted}")

        elif payload["type"] == "file":
            nonce = base64.b64decode(payload["nonce"])
            ciphertext = base64.b64decode(payload["ciphertext"])
            decrypted = cipher.decrypt(nonce, ciphertext)
            out_path = payload["outfile"]
            with open(out_path, "wb") as f:
                f.write(decrypted)
            print(f"[{receiver_id}] File received and saved as {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Receiver ID")
    args = parser.parse_args()

    start_receiver(args.id)

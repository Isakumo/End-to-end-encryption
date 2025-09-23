import argparse
import base64
import json
import socket
from crypto_aes_gcm import AESGCMCipher
from key_kem import generate_keypair, encapsulate_key, decapsulate_key

def send_message(receiver_id, message=None, file=None, outfile=None):
    # Generate keypair
    pk, sk = generate_keypair()
    ciphertext_key, shared_secret_sender = encapsulate_key(pk)
    shared_secret_receiver = decapsulate_key(sk, ciphertext_key)

    cipher = AESGCMCipher(shared_secret_sender)

    if file:
        # Read file bytes
        with open(file, "rb") as f:
            file_bytes = f.read()
        nonce, encrypted = cipher.encrypt(file_bytes)
        payload = {
            "type": "file",
            "filename": file.split("/")[-1],
            "outfile": outfile,
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(encrypted).decode(),
        }
    else:
        nonce, encrypted = cipher.encrypt(message.encode())
        payload = {
            "type": "text",
            "message": message,
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(encrypted).decode(),
        }

    # Send to relay server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5000))
    data = {"receiver": receiver_id, "payload": payload}
    sock.sendall(json.dumps(data).encode())
    sock.close()
    print("Message sent to relay!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receiver", required=True, help="Receiver ID")
    parser.add_argument("--msg", help="Message to send")
    parser.add_argument("--file", help="Path to file to send")
    parser.add_argument("--out", help="Output file name for receiver")
    args = parser.parse_args()

    if args.file and args.out:
        send_message(args.receiver, file=args.file, outfile=args.out)
    elif args.msg:
        send_message(args.receiver, message=args.msg)
    else:
        print("Usage:\n python sender.py --receiver R1 --msg 'hello'\n python sender.py --receiver R1 --file photo.jpg --out received.jpg")

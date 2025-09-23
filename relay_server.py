
import socket, threading, json

HOST = "127.0.0.1"
PORT = 9000

"""
Protocol (newline-delimited JSON):
- To register a receiver:
  {"type": "register", "role": "receiver", "receiver_id": "R1", "pubkey_b64": "..."}
- To send message:
  {"type": "message", "to": "R1", "payload": {...}}
The server stores receiver sockets by id and forwards messages.
"""

receivers = {}  # receiver_id -> client_socket

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    buf = b""
    try:
        while True:
            data = conn.recv(65536).decode()
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    obj = json.loads(line.decode("utf-8"))
                except Exception as e:
                    print("Bad JSON:", e)
                    continue
                t = obj.get("type")
                if t == "register" and obj.get("role") == "receiver":
                    rid = obj.get("receiver_id")
                    receivers[rid] = conn
                    print(f"Registered receiver {rid} -> {addr}")
                    # ack
                    conn.sendall(json.dumps({"type":"ack", "status":"registered"}).encode("utf-8")+b"\n")
                elif t == "message":
                    to = obj.get("to")
                    payload = obj.get("payload")
                    if to in receivers:
                        try:
                            receivers[to].sendall(json.dumps({"type":"message","payload":payload}).encode("utf-8")+b"\n")
                            conn.sendall(json.dumps({"type":"ack","status":"forwarded"}).encode("utf-8")+b"\n")
                        except Exception as e:
                            conn.sendall(json.dumps({"type":"error","error":str(e)}).encode("utf-8")+b"\n")
                    else:
                        conn.sendall(json.dumps({"type":"error","error":"receiver-not-found"}).encode("utf-8")+b"\n")
                else:
                    conn.sendall(json.dumps({"type":"error","error":"unknown-type"}).encode("utf-8")+b"\n")
    except Exception as e:
        print("Connection error:", e)
    finally:
        print("Client disconnected:", addr)
        # remove from receivers if present
        for rid, sock in list(receivers.items()):
            if sock == conn:
                del receivers[rid]

def run_server(host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(5)
        print(f"Relay server listening on {host}:{port}")
        try:
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("Server shutting down")

if __name__ == "__main__":
    run_server()

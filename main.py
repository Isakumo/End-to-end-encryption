# main.py
import threading
import time
import requests
from relay_server import create_app
from receiver import Receiver
from sender import send_message
from results import save_report, save_report_json

def start_relay():
    app = create_app()
    # run flask in a separate thread (dev server)
    server_thread = threading.Thread(target=lambda: app.run(host="127.0.0.1", port=5000, threaded=True), daemon=True)
    server_thread.start()
    # wait for server to be available
    for _ in range(20):
        try:
            r = requests.get("http://127.0.0.1:5000/health", timeout=1)
            if r.ok:
                print("Relay server is up.")
                return server_thread
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Relay server failed to start")

def demo_flow():
    # start relay
    start_relay()
    time.sleep(0.5)

    # create receiver and get its public bytes to share with sender
    receiver = Receiver("receiver1")
    receiver_pub = receiver.get_public_bytes()

    # send a couple of messages
    results_list = []
    messages = [b"Hello Alice, this is secret 1", b"Second secret message!"]
    for msg in messages:
        res = send_message(sender_id="sender1", receiver_id="receiver1", receiver_pub_bytes=receiver_pub, plaintext=msg)
        print("Sent:", res["relay_response"])
        results_list.append({"enc_time_ms": res["enc_time_ms"]})

        # give relay a moment
        time.sleep(0.3)
        # poll receiver
        rec_results = receiver.poll_once()
        print("Receiver got:", rec_results)
        # append decryption metrics if present
        for rr in rec_results:
            if "dec_time_ms" in rr:
                results_list[-1]["dec_time_ms"] = rr["dec_time_ms"]
                results_list[-1]["plaintext"] = rr["plaintext"]

    # aggregate metrics
    metrics = {
        "total_messages": len(results_list),
        "details": results_list
    }
    save_report(metrics)
    save_report_json(metrics)

if __name__ == "__main__":
    demo_flow()

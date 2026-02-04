from flask import Flask, request, jsonify
import time
import logging

# Configure logging with timestamp and message
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
app = Flask(__name__)

@app.get("/health")
def health():
    """Health check endpoint"""
    start = time.time()
    latency = int((time.time() - start) * 1000)
    logging.info(f'service=A endpoint=/health status=ok latency_ms={latency}')
    return jsonify(status="ok")

@app.get("/echo")
def echo():
    """Echo endpoint that returns the message parameter"""
    start = time.time()
    msg = request.args.get("msg", "")
    resp = {"echo": msg}
    latency = int((time.time() - start) * 1000)
    logging.info(f'service=A endpoint=/echo msg="{msg}" status=ok latency_ms={latency}')
    return jsonify(resp)

if __name__ == "__main__":
    logging.info("Starting Service A on http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080)

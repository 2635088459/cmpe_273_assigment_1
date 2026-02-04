from flask import Flask, request, jsonify
import time
import logging
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
app = Flask(__name__)

SERVICE_A = "http://127.0.0.1:8080"

@app.get("/health")
def health():
    """Health check endpoint"""
    start = time.time()
    latency = int((time.time() - start) * 1000)
    logging.info(f'service=B endpoint=/health status=ok latency_ms={latency}')
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    """Client endpoint that calls Service A echo endpoint"""
    start = time.time()
    msg = request.args.get("msg", "")
    try:
        # Call provider with timeout
        logging.info(f'service=B calling service=A endpoint=/echo msg="{msg}"')
        r = requests.get(f"{SERVICE_A}/echo", params={"msg": msg}, timeout=1.0)
        r.raise_for_status()
        data = r.json()
        latency = int((time.time() - start) * 1000)
        logging.info(f'service=B endpoint=/call-echo msg="{msg}" status=ok latency_ms={latency}')
        return jsonify(service_b="ok", service_a=data)
    
    # Handle connection errors (provider down or unreachable)
    except ConnectionError as e:
        latency = int((time.time()-start)*1000)
        logging.error(f'service=B endpoint=/call-echo status=error error="Provider unreachable: {str(e)}" latency_ms={latency}')
        return jsonify(service_b="ok", service_a="unavailable", error="Provider is down or unreachable"), 503
    
    # Handle timeout errors (request took too long)
    except Timeout as e:
        latency = int((time.time()-start)*1000)
        logging.error(f'service=B endpoint=/call-echo status=error error="Request timeout: {str(e)}" latency_ms={latency}')
        return jsonify(service_b="ok", service_a="unavailable", error="Request timed out"), 503
    
    # Handle any other request-related errors
    except RequestException as e:
        latency = int((time.time()-start)*1000)
        logging.error(f'service=B endpoint=/call-echo status=error error="Request failed: {str(e)}" latency_ms={latency}')
        return jsonify(service_b="ok", service_a="unavailable", error=str(e)), 503
    
    # Catch-all for unexpected errors
    except Exception as e:
        latency = int((time.time()-start)*1000)
        logging.error(f'service=B endpoint=/call-echo status=error error="Unexpected error: {str(e)}" latency_ms={latency}')
        return jsonify(service_b="ok", service_a="unavailable", error="Internal error"), 503

if __name__ == "__main__":
    logging.info("Starting Service B on http://127.0.0.1:8081")
    logging.info(f"Service B will call Service A at {SERVICE_A}")
    app.run(host="127.0.0.1", port=8081)

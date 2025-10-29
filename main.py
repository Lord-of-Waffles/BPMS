import asyncio
import threading
import os
from flask import Flask, jsonify
from pyzeebe import ZeebeClient, ZeebeWorker, create_camunda_cloud_channel
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

zeebe_loop = asyncio.new_event_loop()
client = None  # will initialise in worker thread


# --- Flask Routes ---

# Health check, server is alive
@app.route("/")
def index():
    return jsonify({"message": "Camunda Flask worker is running!"})

# This route triggers a new workflow instance in camunda
# 1. Check if zeebe client is ready
# 2. Call the process specified at the process_id
# 3. Return the process instance key
@app.route("/start")
def start_process():
    global client
    if client is None:
        return jsonify({"error": "Zeebe client not ready yet"}), 503

    process_id = "Process_15ezi0t"
    print(f"Starting process: {process_id}")

    async def _start():
        return await client.run_process(process_id)

    future = asyncio.run_coroutine_threadsafe(_start(), zeebe_loop)
    result = future.result()

    instance_key = result.process_instance_key

    print(f"Process instance started with key: {instance_key}")
    return jsonify({
        "message": f"Started process {process_id}",
        "process_instance_key": instance_key
    })



# --- Zeebe Worker Thread ---

# This code runs the actual tasks in the workflow :)
# task_type has to reflect EEXACTLY how it's written in the camunda modeler!!

def run_worker():
    global client
    asyncio.set_event_loop(zeebe_loop)

    # Create everything INSIDE this loop
    channel = create_camunda_cloud_channel(
        client_id=os.environ["ZEEBE_CLIENT_ID"],
        client_secret=os.environ["ZEEBE_CLIENT_SECRET"],
        cluster_id=os.environ["ZEEBE_ADDRESS"].split(".")[0],
        region="bru-2"
    )

    client = ZeebeClient(channel)
    worker = ZeebeWorker(channel)

    @worker.task(task_type="add-json-data")
    def add_json_data():
        data = {"name": "Alice", "age": 30}
        print("Generated JSON:", data)
        return {"json_data": data}

    @worker.task(task_type="send-json")
    def send_json(json_data: dict):
        print("Sending JSON:", json_data)
        return {}

    @worker.task(task_type="receive-json")
    def receive_json(json_data: dict):
        print("Received JSON:", json_data)
        return {}

    print("✅ Zeebe worker started")
    zeebe_loop.run_until_complete(worker.work())


if __name__ == "__main__":
    threading.Thread(target=run_worker, daemon=True).start()
    app.run(port=5000)

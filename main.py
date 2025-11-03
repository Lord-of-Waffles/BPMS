import asyncio
import threading
import os
import random
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

    process_id = "Process_0vfu21l"
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
# Later on, have all these tasks separated into own files so main.py not too long - Ben
    #@worker.task(task_type="add-json-data")
    #   def add_json_data():
    #       data = {"name": "Alice", "age": 30}
    #       print("Generated JSON:", data)
    #       return {"json_data": data}

    @worker.task(task_type="send-vm-request")
    def send_vm_request(vmSize: str,
                        vmImage: str,
                        vmName: str,
                        additionalFeatures: list,
                        dateNeeded: str,
                        userEmail: str):
        
        json_data = {"VM Size": vmSize,
                    "VM Image": vmImage,
                    "VM Name": vmName,
                    "Additional Features": additionalFeatures,
                    "Date Needed": dateNeeded,
                    "Email address": userEmail}
        
        print("Sending VM request with these parameters:", json_data)

        return {
            "VMRequestStatus": "SENT",
            "VMRequestID": random.randint(1,99),
            "json_data": json_data
        }

    @worker.task(task_type="receive-vm-request")
    def receive_vm_request(VMRequestStatus: str, VMRequestID: int, json_data: dict):
        print(f"Received VM request with ID: {VMRequestID} & status: {VMRequestStatus}")
        print(f"with these parameters: {json_data}")
        return {}  
    
    @worker.task(task_type="validate-request")
    def validate_request(json_data: dict, VMRequestID: int):
        if json_data.get("VM Size"):
            if json_data.get("VM Image"):
                if json_data.get("VM Name"):
                    print(f"VM Request with ID: {VMRequestID} is valid")
                    return {"requestIsValid": 1}
                
    @worker.task(task_type="send-progress-update")
    def send_progress_update(json_data: dict):
        return {"updateText": f"Your VM called {json_data['VM Name']} was configured correctly, and is currently being initialised. This process can take up to 10 minutes. Please be patient as we get it ready for you!"}    
    @worker.task(task_type="receive-progress-update")
    def receive_progress_update(updateText: str):
        print(updateText)
        return {}

    @worker.task(task_type="send-vm-config")
    def send_vm_config(VMRequestID):
        print(f"Sending VM Configuration with ID: {VMRequestID} to Data Layer")
        return {}

    @worker.task(task_type="receive-vm-config")
    def receive_vm_config(json_data: dict, VMRequestID):
        print(f"Received VM Request ID: {VMRequestID} from App Layer with this config: {json_data}")
        return {}
    
    @worker.task(task_type="start-initialisation")
    def start_initialisation():
        print("-=====================-")
        print("Initialising VM...")
        return {}

    @worker.task(task_type="allocate-ram")
    def allocate_ram(json_data: dict):
        print("Initialising RAM...")
    
        if json_data["VM Size"] == "smallVM":
            vm_ram = "2GB"
        elif json_data["VM Size"] == "mediumVM":
            vm_ram = "4GB"
        else:
            vm_ram = "8GB"
    
        return {"vm_ram": vm_ram}

    @worker.task(task_type="processing-power")
    def processing_power(json_data: dict):
        print("Initialising vCPU...")
    
        if json_data["VM Size"] == "smallVM":
            vm_vcpu = "2 Cores"
        elif json_data["VM Size"] == "mediumVM":
            vm_vcpu = "4 Cores"
        else:
            vm_vcpu = "8 Cores"
    
        return {"vm_vcpu": vm_vcpu}

    @worker.task(task_type="allocate-storage")
    def allocate_storage(json_data: dict):
        print("Initialising VM Storage...")
    
        if json_data["VM Size"] == "smallVM":
            vm_storage = "10 GB"
        elif json_data["VM Size"] == "mediumVM":
            vm_storage = "20 GB"
        else:
            vm_storage = "30 GB"
    
        return {"vm_storage": vm_storage}

    @worker.task(task_type="merge-config")
    def merge_config(json_data: dict, vm_ram: str, vm_vcpu: str, vm_storage: str):
        print("Merging configuration from parallel tasks...")
        updated_data = dict(json_data)
        updated_data["VM Ram"] = vm_ram
        updated_data["VM vCPU"] = vm_vcpu
        updated_data["VM Storage"] = vm_storage
    
        return {"json_data": updated_data}
    
    @worker.task(task_type="send-result")
    def send_result():
        print("VM Initialisation complete! Sending result...")
        return {}

    @worker.task(task_type="receive-result")
    def receive_result(json_data: dict):
        print(f"\nInitialisation process completed. VM called {json_data['VM Name']} has been initialised with \n{json_data['VM Ram']} of RAM,\na vCPU with {json_data['VM vCPU']} \nand {json_data['VM Storage']} of storage.")
        return {}
    print("Zeebe worker started")
    zeebe_loop.run_until_complete(worker.work())


if __name__ == "__main__":
    threading.Thread(target=run_worker, daemon=True).start()
    app.run(port=5000)

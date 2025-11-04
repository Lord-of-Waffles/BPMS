import random
import os
from pymongo import MongoClient
from dotenv import load_dotenv


def register_tasks(worker):
    # register all zeebe workers
    load_dotenv()

    client = MongoClient(os.getenv("MONGO_URI"), tlsAllowInvalidCertificates=True)


    @worker.task(task_type="send-vm-request")
    def send_vm_request(vmSize: str, vmImage: str, vmName: str, additionalFeatures: list, dateNeeded: str, userEmail: str):
        json_data = {
            "VM Size": vmSize,
            "VM Image": vmImage,
            "VM Name": vmName,
            "Additional Features": additionalFeatures,
            "Date Needed": dateNeeded,
            "Email address": userEmail
        }
        print("Sending VM request with these parameters:", json_data)
        return {
            "VMRequestStatus": "SENT",
            "VMRequestID": random.randint(1, 99),
            "json_data": json_data
        }

    @worker.task(task_type="receive-vm-request")
    def receive_vm_request(VMRequestStatus: str, VMRequestID: int, json_data: dict):
        print(f"Received VM request with ID: {VMRequestID} & status: {VMRequestStatus}")
        print(f"with these parameters: {json_data}")
        return {}

    @worker.task(task_type="validate-request")
    def validate_request(json_data: dict, VMRequestID: int):
        if json_data.get("VM Size") and json_data.get("VM Image") and json_data.get("VM Name"):
            print(f"VM Request with ID: {VMRequestID} is valid")
            return {"requestIsValid": 1}
        else:
            return {"requestIsValid": 0}

    @worker.task(task_type="send-progress-update")
    def send_progress_update(json_data: dict):
        return {
            "updateText": f"Your VM called {json_data['VM Name']} was configured correctly, and is currently being initialised. This process can take up to 10 minutes. Please be patient as we get it ready for you!"
        }

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
        vm_size = json_data["VM Size"]
        vm_ram = "2GB" if vm_size == "smallVM" else "4GB" if vm_size == "mediumVM" else "8GB"
        print("Initialising RAM...")
        return {"vm_ram": vm_ram}

    @worker.task(task_type="processing-power")
    def processing_power(json_data: dict):
        vm_size = json_data["VM Size"]
        vm_vcpu = "2 Cores" if vm_size == "smallVM" else "4 Cores" if vm_size == "mediumVM" else "8 Cores"
        print("Initialising vCPU...")
        return {"vm_vcpu": vm_vcpu}

    @worker.task(task_type="allocate-storage")
    def allocate_storage(json_data: dict):
        vm_size = json_data["VM Size"]
        vm_storage = "10 GB" if vm_size == "smallVM" else "20 GB" if vm_size == "mediumVM" else "30 GB"
        print("Initialising VM Storage...")
        return {"vm_storage": vm_storage}

    @worker.task(task_type="merge-config")
    def merge_config(json_data: dict, vm_ram: str, vm_vcpu: str, vm_storage: str):
        print("Merging configuration from parallel tasks...")
        updated_data = dict(json_data)
        updated_data.update({
            "VM Ram": vm_ram,
            "VM vCPU": vm_vcpu,
            "VM Storage": vm_storage
        })
        return {"json_data": updated_data}

    @worker.task(task_type="send-result")
    def send_result():
        print("VM Initialisation complete! Sending result...")
        return {}

    @worker.task(task_type="receive-result")
    def receive_result(json_data: dict):
        print(f"\nInitialisation process completed. VM called {json_data['VM Name']} has been initialised with \n"
              f"{json_data['VM Ram']} of RAM,\na vCPU with {json_data['VM vCPU']} \n"
              f"and {json_data['VM Storage']} of storage.")
        return {}
    
    @worker.task(task_type="request-is-invalid")
    def request_is_invalid(VMRequestID: int):
        print(f"Request with ID {VMRequestID} is invalid. Make sure you give your VM a name, choose a size, and choose an image. Please try again.")
        return {}

    @worker.task(task_type="save-config-mongodb")
    def save_config_mongodb():
        print("is this being called")
        client.admin.command('ping')
        print("succeess")
        return {}
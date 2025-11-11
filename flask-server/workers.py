import random
import os
import csv
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from flask import jsonify



def register_tasks(worker):
    # register all zeebe workers
    load_dotenv()

    client = MongoClient(os.getenv("MONGO_URI"), tlsAllowInvalidCertificates=True)
    db = client[os.getenv("MONGO_DB")]



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
        # cast data type of VMRequestID to string
        return {"VMRequestID": str(VMRequestID)}

    @worker.task(task_type="validate-request")
    def validate_request(json_data: dict, VMRequestID: str):
        try:
            if json_data.get("VM Size") and json_data.get("VM Image") and json_data.get("VM Name"):
                print(f"VM Request with ID: {VMRequestID} is valid")
                return {"requestIsValid": 1}
        except Exception as e:
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
    def receive_vm_config(json_data: dict, VMRequestID:str):
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
    def request_is_invalid(VMRequestID: str):
        print(f"Request with ID {VMRequestID} is invalid. Make sure you give your VM a name, choose a size, and choose an image. Please try again.")
        return {}

    @worker.task(task_type="save-config-mongodb")
    def save_config_mongodb(json_data: dict):
        print("is this being called")
        client.admin.command('ping')
        print("succeess")
        vms_collection = db['vms']
        result = vms_collection.insert_one(json_data)

        return {
                'dbVMId': str(result.inserted_id),
                'dbSaveSuccess': True,
                'dbSaveTimestamp': datetime.utcnow().isoformat()
            }
    
    @worker.task(task_type="save-config-csv")
    def save_config_csv(json_data: dict):
        with open('saved_config.csv', 'w', newline='') as csvfile:
            config_writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            config_writer.writerow(json_data)

    @worker.task(task_type="get-data-centre-availability")
    def get_data_centre_availability():
        try:
            # send request to node server 
            node_url = os.getenv('NODE_SERVER_URL', 'http://node-server:3000')
            response = requests.get(f'{node_url}/availability', timeout=10)
            response.raise_for_status()
        
            # parse data sent by node server
            data = response.json()
        
            return {
                'DataCentreAvailability': data  # This will be the dict with bestCentre, availability, allCentres
            }
        except requests.exceptions.RequestException as e:
            return {
                'Error': str(e),
                'DataCentreAvailability': None
            }

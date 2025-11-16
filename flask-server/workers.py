import random
import os
import requests
from dotenv import load_dotenv
from pyzeebe import Job
from pyzeebe.errors import BusinessError




def register_tasks(worker):
    load_dotenv()



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


    @worker.task(task_type="validate-request")
    def validate_request(job: Job):
        json_data = job.variables.get("json_data", {})
        VMRequestID = job.variables.get("VMRequestID")

        vm_name = json_data.get("VM Name", "")
    
        if not vm_name or len(vm_name) < 1:
            print(f"VM Request {VMRequestID} failed validation - missing VM Name")
            raise BusinessError("INVALID_REQUEST")

        print(f"VM Request {VMRequestID} is valid")
        return {"ValidationStatus": "VALID"}

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

    @worker.task(task_type="approve-request-to-int")
    def approve_request_to_int(approveRequest:str):
        return {"approveRequest": int(approveRequest)}
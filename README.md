# Description

## This repository contains code intended to serve as external tasks for a process modelled in Camunda.

## Install instructions
Instructions to setup project:

Disclaimer: depending on python install, you might have to use python instead of python3, or pip instead of pip3

Navigate to directory where you want to clone repo

    git clone <repo>

    # Create virtual environment
    python3 -m venv venv

    # Activate it
    source venv/bin/activate

    # Install required packages
    pip3 install -r requirements.txt

Afterwards, create a .env in the root directory and initialise these environment variables:
- ZEEBE_ADDRESS = This should be the address of your cluster
- ZEEBE_CLIENT_ID = Client ID
- ZEEBEE_CLIENT_SECRET 
- CAMUNDA_CLOUD_REGION
- MONGO_URI = mongodb+srv://bpmsvmproject_db_user:<db_password>@bpmsproject.6fzayhk.mongodb.net/?appName=BPMSProject
- MONGO_DB = BPMS_Project

Change <db_password> to your actual one

To be able to execute workers.py/get_data_centre_availability(), make sure you run the node server at port 3000 that it requires.

Code for the node server can be found here: https://github.com/Lord-of-Waffles/BPMS_Node

## Files

### main.py

This file runs the flask server, connects to Zeebe and calls workers.py

### workers.py

This file contains all the different functions for when tasks are executed by Zeebe

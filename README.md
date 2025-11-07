# Description

## This repository contains code intended to serve as external tasks for a process modelled in Camunda.

It consists of 2 dockerised servers, 1 written with Flask and the other with Node. To be able to run the project, please make sure the docker daemon is running on your computer.

## Install instructions
Instructions to setup project:

Navigate to directory where you want to clone repo

    git clone <repo>

Afterwards, create a .env in the flask-server directory and initialise these environment variables:
- ZEEBE_ADDRESS = This should be the address of your cluster
- ZEEBE_CLIENT_ID = Client ID
- ZEEBEE_CLIENT_SECRET 
- CAMUNDA_CLOUD_REGION
- MONGO_URI = mongodb+srv://bpmsvmproject_db_user:<db_password>@bpmsproject.6fzayhk.mongodb.net/?appName=BPMSProject
- MONGO_DB = BPMS_Project

Change <db_password> to your actual one

Finally, when you're ready to launch to project, navigate to the project's root diretory and run this command in your terminal:

    docker compose up --build

## Files

### main.py

This file runs the flask server, connects to Zeebe and calls workers.py

### workers.py

This file contains all the different functions for when tasks are executed by Zeebe

### server.js

This file runs the node server, which will be called by the flask server for a specific task in the BPMS process.

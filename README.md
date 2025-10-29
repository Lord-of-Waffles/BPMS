# Description

## This repository contains code intended to serveer as external tasks for a process modelled in Camunda.

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
- ZEEBE_ADDRESS | This should be the address of your cluster
- ZEEBE_CLIENT_ID | Client ID
- ZEEBEE_CLIENT_SECRET |
- CAMUNDA_CLOUD_REGION

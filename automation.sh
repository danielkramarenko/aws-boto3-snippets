#!/bin/bash

# Set variables (customize these)
REPO_URL="https://github.com/danielkramarenko/aws-boto3-snippets.git"
REPO_DIR="/home/ec2-user/aws-boto3-snippets"
SCRIPT_PATH="$REPO_DIR/src/ec2_s3_computing_automation.py"

# Clone the Git repository
echo "Cloning repository..."
git clone "$REPO_URL" "$REPO_DIR" || { echo "Error: Failed to clone repository."; exit 1; }

# Install Python 3 pip (if not already installed)
echo "Installing Python 3 pip..."
sudo dnf install python3-pip -y || { echo "Error: Failed to install python3-pip."; exit 1; }

# Install requirements
echo "Installing requirements..."
pip3 install -r "$REPO_DIR/requirements.txt" || { echo "Error: Failed to install requirements."; exit 1; }


# Run the Python script
echo "Running Python script..."
python3 "$SCRIPT_PATH" || { echo "Error: Failed to run Python script."; exit 1; }

echo "Script execution complete."

exit 0 # Exit with success code
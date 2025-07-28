import subprocess
import logging
import sys
import os

logging.basicConfig(
    filename='setup.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)

def run_command(command):
    try:
        logging.info(f"Running command: {command}")
        result = subprocess.run(command, check=True, shell=True)
        logging.info(f"Command succeeded: {result}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        sys.exit(1)

def install_dependencies():
    logging.info("Installing Python dependencies...")
    run_command(r'C:/Python310/python.exe -m pip install -r requirements.txt')

def main():
    install_dependencies()
    print("Setup complete. Run the agent with run.bat (Windows) or run.sh (Linux/Mac).")

if __name__ == "__main__":
    main()
import os
import platform
import argparse

os.system("clear" if platform.system() == "Linux" else "cls")
print("Before Starting, Auto-installing Python dependencies")

if platform.system() == "Linux":
    os.system(f"python3 -m pip install --upgrade -r requirements.txt")
else:
    os.system(f"python -m pip install --upgrade -r requirements.txt")
os.system("clear" if platform.system() == "Linux" else "cls")

parser = argparse.ArgumentParser()
parser.add_argument('--port', help='Specify the port on which to run the server. (Default is 8000)')
parser.add_argument('--dev', help='Auto Reload', default=0, type=bool)
args = parser.parse_args()

os.system(f"uvicorn main:app {'--reload' if args.dev else ''} --port={8000 if args.port == None else args.port}")
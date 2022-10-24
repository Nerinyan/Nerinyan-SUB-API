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
parser.add_argument('--port', help='Specify the port on which to run the server. (Default is 8000)', default="8000", type=str)
parser.add_argument('--host', help='Specify the host address on which to run the server. (Default is 127.0.0.1)', default="127.0.0.1", type=str)
parser.add_argument('--dev', help='Auto Reload', default=0, type=bool)
args = parser.parse_args()

os.system(f"uvicorn main:app {'--reload' if args.dev else ''} --port={args.port} --host={args.host}")
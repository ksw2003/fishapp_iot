import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

SERVER = os.getenv("SERVER_URL")
SERVER_WS = os.getenv("SERVER_WS")
DEVICE_ID = os.getenv("DEVICE_ID")

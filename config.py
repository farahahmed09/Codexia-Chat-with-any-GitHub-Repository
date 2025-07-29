# config.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the Hugging Face API token
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Hugging Face API token not found. Please set it in your .env file.")
# check_models.py

import os
from huggingface_hub import list_models
from dotenv import load_dotenv

def find_available_models():
    """
    Connects to the Hugging Face Hub and lists popular text-generation models.
    """
    # Load the API token from your .env file
    load_dotenv()
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    if not api_token:
        print("Hugging Face API token not found in .env file.")
        return

    print("Fetching top 15 text-generation models from Hugging Face Hub...\n")

    # Use list_models to fetch models, filtering by task and sorting by downloads
    model_iterator = list_models(
        task="text-generation",
        sort="downloads",
        direction=-1,  # -1 for descending order
        token=api_token,
        limit=15
    )

    for model in model_iterator:
        print(f"- {model.id}")

if __name__ == "__main__":
    find_available_models()
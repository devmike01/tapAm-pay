import os
from dotenv import load_dotenv

load_dotenv()

monify_header = {
    "Authorization": f"Basic {os.environ.get('MONIFY_API_KEY')}",  # If authentication is required
    "Content-Type": "application/json",
    "Accept": "application/json"
}

import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import asset_documents_return

res = asset_documents_return(14753)
pass

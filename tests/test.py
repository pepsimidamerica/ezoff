from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

from ezoff.ezoff import get_teams

res = get_teams()
print(res)
pass

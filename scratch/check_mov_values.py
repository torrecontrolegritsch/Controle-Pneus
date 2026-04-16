import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

project_id = "dpvdjldocvdsdgvmnsvu"
supa_url = f"https://{project_id}.supabase.co"
supa_key = os.getenv("SUPABASE_KEY")

api_url = f"{supa_url}/rest/v1/gp_movimentacoes"
headers = {
    "apikey": supa_key,
    "Authorization": f"Bearer {supa_key}",
    "Range": "0-5"
}

response = requests.get(api_url, headers=headers)
if response.status_code == 200:
    data = response.json()
    for row in data:
        print(f"ID: {row['id']} - data_hora: {row.get('data_hora')}")
else:
    print("Error:", response.status_code, response.text)

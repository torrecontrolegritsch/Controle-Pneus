import os
from dotenv import load_dotenv

load_dotenv()

print(f"SQLSERVER_HOST: [{os.getenv('SQLSERVER_HOST')}]")
print(f"SQLSERVER_PORT: [{os.getenv('SQLSERVER_PORT')}]")
print(f"SQLSERVER_USER: [{os.getenv('SQLSERVER_USER')}]")
print(f"SQLSERVER_DB: [{os.getenv('SQLSERVER_DB')}]")

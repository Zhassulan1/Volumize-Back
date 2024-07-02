import os
from dotenv import load_dotenv

load_dotenv()

key = "AWS_SECRET_ACCESS_KEY"
value = os.environ.get(key) 

print(value)
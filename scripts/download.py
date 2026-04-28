import requests
import zipfile
import io
import os
from datetime import datetime

URLS = [
    "http://feed.getrix.it/xml/12C22AD2-7740-46E9-9676-C051C9C6D674.zip",
    "http://feed.getrix.it/xml/4C65360F-1CB5-43C6-BA1B-6448DEEF2529.zip",
    "http://feed.getrix.it/xml/45AD2DB4-A85B-4238-A537-35259EFAB356.zip",
]

OUTPUT_DIR = "output/xml"
os.makedirs(OUTPUT_DIR, exist_ok=True)

for url in URLS:
    print(f"Scarico {url}...")
    r = requests.get(url, timeout=60)
    r.raise_for_status()  # fallisce subito se HTTP error

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(OUTPUT_DIR)
    print(f"  estratti: {z.namelist()}")

print(f"\nFatto! File in {OUTPUT_DIR}:")
for f in os.listdir(OUTPUT_DIR):
    print(f"  {f}")

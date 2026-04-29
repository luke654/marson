import requests
import zipfile
import io
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

URLS = [
    "http://feed.getrix.it/xml/12C22AD2-7740-46E9-9676-C051C9C6D674.zip",
    "http://feed.getrix.it/xml/4C65360F-1CB5-43C6-BA1B-6448DEEF2529.zip",
    "http://feed.getrix.it/xml/45AD2DB4-A85B-4238-A537-35259EFAB356.zip",
]

OUTPUT_DIR = "output"
XML_DIR = os.path.join(OUTPUT_DIR, "xml")
os.makedirs(XML_DIR, exist_ok=True)


def xml_to_dict(element):
    """Converte ricorsivamente un elemento XML in dict."""
    result = {}
    # Attributi
    if element.attrib:
        result["@attributes"] = element.attrib
    # Figli
    children = list(element)
    if children:
        child_dict = {}
        for child in children:
            child_data = xml_to_dict(child)
            if child.tag in child_dict:
                # Se il tag esiste già, trasforma in lista
                if not isinstance(child_dict[child.tag], list):
                    child_dict[child.tag] = [child_dict[child.tag]]
                child_dict[child.tag].append(child_data)
            else:
                child_dict[child.tag] = child_data
        result.update(child_dict)
    # Testo
    text = (element.text or "").strip()
    if text:
        result["#text"] = text
    return result


all_data = {}
errors = []

for url in URLS:
    print(f"Scarico {url}...")
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(XML_DIR)
        print(f"  estratti: {z.namelist()}")

        for filename in z.namelist():
            if not filename.lower().endswith(".xml"):
                continue
            xml_path = os.path.join(XML_DIR, filename)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            all_data[filename] = {
                "source_url": url,
                "root_tag": root.tag,
                "data": xml_to_dict(root),
            }

    except Exception as e:
        print(f"  ERRORE su {url}: {e}")
        errors.append({"url": url, "error": str(e)})

output = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "feeds": all_data,
    "errors": errors,
}

json_path = os.path.join(OUTPUT_DIR, "feed.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nFatto! JSON salvato in {json_path}")
if errors:
    print(f"  {len(errors)} URL falliti (non bloccanti): {[e['url'] for e in errors]}")

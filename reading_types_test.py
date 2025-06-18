import os
import requests

# URL in token iz okolja
API_URL = "https://api.informatika.si/mojelektro/v1"
API_TOKEN = os.environ.get("MOJELEKTRO_TOKEN")

if not API_TOKEN:
    print("⚠️ Napaka: Manjka okoljska spremenljivka MOJELEKTRO_TOKEN")
    exit(1)

# Header z API ključem
headers = {
    "X-API-TOKEN": API_TOKEN,
    "Accept": "application/json"
}

# Endpoint
url = f"{API_URL}/reading-type"

# Pošlji zahtevo
print("🔄 Pošiljam zahtevo na:", url)
response = requests.get(url, headers=headers)

# Obravnava odgovora
if response.status_code == 200:
    data = response.json()
    print(f"✅ Najdenih {len(data)} ReadingType zapisov:\n")
    for item in data:
        print(f"- {item.get('naziv')} ({item.get('oznaka')}): {item.get('readingType')}")
else:
    print(f"❌ Napaka {response.status_code}")
    print("Odziv:", response.text)

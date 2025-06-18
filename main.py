import os
import requests
from datetime import date, timedelta
from twilio.rest import Client

# 🔐 Secrets iz okolja
API_TOKEN = os.environ['MOJELEKTRO_TOKEN']
GSRN = os.environ['MOJELEKTRO_GSRN']
TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']
TWILIO_FROM = os.environ['TWILIO_FROM']
TWILIO_TO = os.environ['TWILIO_TO']

# 📅 Včerajšnji datum
vceraj = date.today() - timedelta(days=1)
datum = vceraj.isoformat()

# 🌐 API podatki
url = "https://api.informatika.si/mojelektro/v1/meter-readings"
headers = {
    "X-API-TOKEN": API_TOKEN,
    "Accept": "application/json"
}
params = {
    "usagePoint": GSRN,
    "startTime": datum,
    "endTime": datum
}

# 📥 Klic API in obdelava
try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print("⚠️ Napaka pri pridobivanju ali razčlenjevanju podatkov!")
    print("Status:", response.status_code if 'response' in locals() else "Ni odgovora")
    print("Odziv:", response.text[:500] if 'response' in locals() else "Ni vsebine")
    raise e

# ⚙️ Seštej vse vrednosti v podatkih
oddana_energija = 0.0

for block in data.get("intervalBlocks", []):
    for reading in block.get("intervalReadings", []):
        try:
            oddana_energija += float(reading.get("value", 0))
        except ValueError:
            continue  # preskoči, če ni številka

# 📤 Pripravi in pošlji SMS
if oddana_energija > 0:
    body = (
        f"ELEKTRARNA DELUJE! Dnevno poročilo o delovanju sončne elektrarne Gmajnica 255. "
        f"Včeraj je bilo proizvedene {oddana_energija:.2f} kWh električne energije."
    )
else:
    body = "ELEKTRARNA NE DELUJE! Včeraj elektrarna ni delovala."

# Twilio SMS
client = Client(TWILIO_SID, TWILIO_TOKEN)
client.messages.create(
    body=body,
    from_=TWILIO_FROM,
    to=TWILIO_TO
)

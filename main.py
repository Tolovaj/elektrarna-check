import os

print("DEBUG: Razpoložljive spremenljivke:")
print(list(os.environ.keys()))

if 'MOJELEKTRO_GSRN' not in os.environ:
    raise RuntimeError("MOJELEKTRO_GSRN ni bil naložen! Secret manjka.")

import requests
from datetime import date, timedelta
from twilio.rest import Client

# Nastavitve iz okolja (GitHub Secrets)
API_TOKEN = os.environ['MOJELEKTRO_TOKEN']
GSRN = os.environ['MOJELEKTRO_GSRN']
tw_sid = os.environ['TWILIO_SID']
tw_token = os.environ['TWILIO_TOKEN']
tw_from = os.environ['TWILIO_FROM']
tw_to = os.environ['TWILIO_TO']

# Določimo včerajšnji datum
vceraj = date.today() - timedelta(days=1)
datum = vceraj.isoformat()

# Klic na Moj Elektro testni API
url = f"https://mojelektro.informatika.si/api/v1/meter-readings?gsrn={GSRN}&datum={datum}"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# Pošlji zahtevek
r = requests.get(url, headers=headers)

try:
    data = r.json()
except Exception as e:
    print("⚠️ Napaka pri branju JSON odgovora:")
    print("Status:", r.status_code)
    print("Odziv:", r.text[:500])
    raise e

# Privzeta vrednost
oddana_energija = 0

# Poskušaj najti energijo v podatkih
if "intervalBlocks" in data:
    for block in data["intervalBlocks"]:
        for reading in block.get("intervalReadings", []):
            oddana_energija += reading.get("value", 0)

# Pripravi sporočilo
if oddana_energija > 0:
    msg = (
        "ELEKTRARNA DELUJE! "
        "Dnevno poročilo o delovanju sončne elektrarne Gmajnica 255. "
        f"Včeraj je bilo proizvedene {oddana_energija:.2f} kWh električne energije."
    )
else:
    msg = (
        "ELEKTRARNA NE DELUJE! "
        "Včeraj elektrarna ni delovala."
    )

# Pošlji SMS
client = Client(tw_sid, tw_token)
client.messages.create(
    body=msg,
    from_=tw_from,
    to=tw_to
)

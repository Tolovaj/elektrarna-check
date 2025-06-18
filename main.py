import os
import requests
from datetime import date, timedelta
from twilio.rest import Client

# Okoljske spremenljivke iz GitHub Secrets
API_TOKEN = os.environ['MOJELEKTRO_TOKEN']
MESTO_ID = os.environ['MOJELEKTRO_METRIC_ID']
tw_sid = os.environ['TWILIO_SID']
tw_token = os.environ['TWILIO_TOKEN']
tw_from = os.environ['TWILIO_FROM']
tw_to = os.environ['TWILIO_TO']

# Določimo včerajšnji datum
vceraj = date.today() - timedelta(days=1)
datum = vceraj.isoformat()

# API klic
url = f"https://mojelektro.si/api/merilno-mesto/{MESTO_ID}/dnevni-podatki"
params = {'datum': datum}
headers = {'Authorization': f'Bearer {API_TOKEN}'}

r = requests.get(url, params=params, headers=headers)
r.raise_for_status()
try:
    data = r.json()
except Exception as e:
    print("Napaka pri pretvorbi v JSON – morda napačen API_TOKEN, merilno mesto ali ni podatkov.")
    print("HTTP status:", r.status_code)
    print("Odzivna vsebina:", r.text)
    raise e  # prekinemo skripto, da vidimo točno napako

# Preverimo oddano energijo
oddana_energija = data.get('oddana_energija_kwh', 0)

# Priprava sporočila glede na stanje
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

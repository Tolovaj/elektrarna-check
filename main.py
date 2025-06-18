import requests
from datetime import date, timedelta
from twilio.rest import Client
import os

# Konstante
MERILNO_MESTO = "3-8005031"
API_TOKEN = os.environ["MOJELEKTRO_TOKEN"]
TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]
READING_TYPE = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"  # Oddana delovna energija ET (24h)

# Datum včeraj in dan pred tem
dan2 = date.today() - timedelta(days=1)
dan1 = dan2 - timedelta(days=1)

def pridobi_energijo(datum):
    url = "https://api.informatika.si/mojelektro/v1/meter-readings"
    headers = {"X-API-TOKEN": API_TOKEN}
    params = {
        "usagePoint": MERILNO_MESTO,
        "startTime": datum.isoformat(),
        "endTime": datum.isoformat(),
        "option": f"ReadingType={READING_TYPE}"
    }
    print(f"➡️ Pošiljam zahtevo za {datum}...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    vrednost = float(data["intervalBlocks"][0]["intervalReadings"][0]["value"])
    return vrednost

try:
    energija1 = pridobi_energijo(dan1)
    energija2 = pridobi_energijo(dan2)
    razlika = round(energija2 - energija1, 2)

    if razlika > 0:
        body = f"ELEKTRARNA DELUJE! Včeraj ({dan2}) je bilo proizvedene {razlika} kWh električne energije."
    else:
        body = f"ELEKTRARNA NE DELUJE! Včeraj ({dan2}) elektrarna ni delovala."

    print(f"➡️ Pošiljam SMS: {body}")
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        body=body,
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )
    print("✅ SMS poslan.")

except Exception as e:
    print("⚠️ Napaka:")
    print(e)

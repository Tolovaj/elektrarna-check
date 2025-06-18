import os
import requests
from datetime import date, timedelta
from twilio.rest import Client

# Okoljske spremenljivke iz GitHub/GitLab Secrets
API_TOKEN = os.getenv("MOJELEKTRO_API_TOKEN")
USAGE_POINT = os.getenv("MOJELEKTRO_USAGE_POINT")
READING_TYPE = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

def fetch_energy(datum: str) -> float:
    url = "https://api.informatika.si/mojelektro/v1/meter-readings"
    headers = { "X-API-TOKEN": API_TOKEN }
    params = {
        "usagePoint": USAGE_POINT,
        "startTime": datum,
        "endTime": datum,
        "option": f"ReadingType={READING_TYPE}"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    value = float(data["intervalBlocks"][0]["intervalReadings"][0]["value"])
    return value

def send_sms(message: str):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )

if __name__ == "__main__":
    try:
        today = date.today()
        day1 = (today - timedelta(days=2)).isoformat()
        day2 = (today - timedelta(days=1)).isoformat()

        energy1 = fetch_energy(day1)
        energy2 = fetch_energy(day2)
        delta = round(energy2 - energy1, 3)

        msg = f"⚡ Oddana energija za {day2}: {delta} kWh"

        print(msg)
        send_sms(msg)

    except Exception as e:
        print("⚠️ Napaka:")
        print(e)

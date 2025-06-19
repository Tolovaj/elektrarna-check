import requests
import datetime
import os
import smtplib
from email.message import EmailMessage

# 💾 Branje iz okolja
TOKEN = os.getenv("MOJELEKTRO_TOKEN")
USAGE_POINT = os.getenv("MOJELEKTRO_METRIC_ID")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

READING_TYPE = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"

# 📆 Datumi
dan1 = (datetime.datetime.now() - datetime.timedelta(days=2)).date()
dan2 = (datetime.datetime.now() - datetime.timedelta(days=1)).date()

def pridobi_energijo(datum):
    url = "https://api.informatika.si/mojelektro/v1/meter-readings"
    headers = {
        "X-API-TOKEN": TOKEN
    }
    params = {
        "usagePoint": USAGE_POINT,
        "startTime": str(datum),
        "endTime": str(datum),
        "option": f"ReadingType={READING_TYPE}"
    }

    print(f"➡️ Pošiljam zahtevo za datum {datum}...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    interval_blocks = data.get("intervalBlocks", [])
    if interval_blocks and "intervalReadings" in interval_blocks[0]:
        vrednost = float(interval_blocks[0]["intervalReadings"][0]["value"])
        return vrednost
    else:
        return None

try:
    energija_dan1 = pridobi_energijo(dan1)
    energija_dan2 = pridobi_energijo(dan2)

    if energija_dan1 is None or energija_dan2 is None:
        sporocilo = f"⚠️ Ni podatkov za {dan1} ali {dan2}."
    else:
        razlika = energija_dan2 - energija_dan1
        if razlika > 0:
            sporocilo = (f"ELEKTRARNA DELUJE!\n\n"
                         f"Dnevno poročilo o delovanju sončne elektrarne.\n"
                         f"Datum: {dan2}\n"
                         f"Proizvedeno: {razlika:.2f} kWh")
        else:
            sporocilo = (f"ELEKTRARNA NE DELUJE!\n\n"
                         f"Datum: {dan2}\n"
                         f"Proizvodnja: 0.00 kWh")

    # 📧 Pošlji e-mail
    msg = EmailMessage()
    msg["Subject"] = "Poročilo sončne elektrarne"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(sporocilo)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ E-mail poslan!")
except Exception as e:
    print(f"⚠️ Napaka pri pošiljanju ali pridobivanju podatkov: {e}")

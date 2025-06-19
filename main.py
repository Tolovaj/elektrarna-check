import requests
from datetime import date, timedelta
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Konstante
MERILNO_MESTO = "3-8005031"
API_TOKEN = os.environ["MOJELEKTRO_TOKEN"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
MAIL_TO = os.environ["MAIL_TO"]
READING_TYPE = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"

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

    for poskus in range(10):
        print(f"➡️ Pošiljam zahtevo ({poskus + 1}/10) za datum {datum}...")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            vrednost = float(data["intervalBlocks"][0]["intervalReadings"][0]["value"])
            return vrednost
        except Exception as e:
            print(f"⚠️ Poskus {poskus + 1} ni uspel: {e}")
            time.sleep(15)
    raise Exception("❌ Neuspešno pridobivanje podatkov po 10 poskusih.")

def poslji_mail(zadeva, telo):
    msg = MIMEMultipart()
    msg["From"] = formataddr(("Elektrarna Gmajnica", GMAIL_USER))
    msg["To"] = MAIL_TO
    msg["Subject"] = zadeva
    msg.attach(MIMEText(telo, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("✅ E-pošta uspešno poslana.")
    except Exception as e:
        print(f"❌ Napaka pri pošiljanju maila: {e}")

# Glavna logika
try:
    energija1 = pridobi_energijo(dan1)
    energija2 = pridobi_energijo(dan2)
    razlika = round(energija2 - energija1, 2)

    if razlika > 0:
        telo = f"ELEKTRARNA DELUJE! Včeraj ({dan2}) je bilo proizvedene {razlika} kWh električne energije."
    else:
        telo = f"ELEKTRARNA NE DELUJE! Včeraj ({dan2}) elektrarna ni delovala."

    print(f"➡️ Pošiljam e-pošto: {telo}")
    poslji_mail("Status elektrarne", telo)

except Exception as e:
    print("⚠️ Napaka pri izvajanju:")
    print(e)

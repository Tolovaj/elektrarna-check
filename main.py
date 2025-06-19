import requests
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os

# --- KONFIGURACIJA ---
usage_point = os.getenv("MOJELEKTRO_METRIC_ID") or "3-8005031"
token = os.getenv("MOJELEKTRO_TOKEN")
recipient = os.getenv("MAIL_TO")
gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_PASS")

# --- DATUMI ---
dan1 = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
dan2 = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

reading_type = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"  # Oddana delovna energija ET
url_base = "https://api.informatika.si/mojelektro/v1/meter-readings"

def pridobi_podatke(datum):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "usagePoint": usage_point,
        "startTime": datum,
        "endTime": datum,
        "option": f"ReadingType={reading_type}"
    }

    for poskus in range(1, 11):
        print(f"➡️ Pošiljam zahtevo ({poskus}/10) za datum {datum}...")
        try:
            r = requests.get(url_base, headers=headers, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            vrednost = float(data['intervalBlocks'][0]['intervalReadings'][0]['value'])
            print(f"✅ {datum}: {vrednost} kWh")
            return vrednost
        except Exception as e:
            print(f"⚠️ Poskus {poskus} ni uspel: {e}")
            if poskus < 10:
                time.sleep(15)
            else:
                raise Exception(f"Napaka po 10 poskusih za datum {datum}")

def poslji_mail(zadeva, vsebina):
    msg = EmailMessage()
    msg.set_content(vsebina)
    msg['Subject'] = zadeva
    msg['From'] = gmail_user
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)
            print("📧 Mail uspešno poslan.")
    except Exception as e:
        print(f"❌ Napaka pri pošiljanju maila: {e}")

# --- GLAVNI DEL ---
try:
    energija1 = pridobi_podatke(dan1)
    energija2 = pridobi_podatke(dan2)
    razlika = round(energija2 - energija1, 2)

    subject = f"Oddana energija za {dan2}"
    body = f"Med {dan1} in {dan2} si oddal {razlika} kWh v omrežje."

    poslji_mail(subject, body)

except Exception as e:
    error_subject = f"Napaka pri preverjanju elektrarne ({datetime.now().strftime('%Y-%m-%d')})"
    error_body = f"Prišlo je do napake:\n\n{e}"
    poslji_mail(error_subject, error_body)

import requests
from datetime import date, timedelta
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Slovenska imena mesecev
slovenski_meseci = [
    "", "januar", "februar", "marec", "april", "maj", "junij",
    "julij", "avgust", "september", "oktober", "november", "december"
]

# Konstante
MERILNO_MESTO = "3-8005031"
API_TOKEN = os.environ["MOJELEKTRO_TOKEN"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
MAIL_TO = os.environ["MAIL_TO"]
READING_TYPE = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"

# Datumi
danes = date.today()
vceraj = danes - timedelta(days=1)
zacetek_meseca = danes.replace(day=1)
zacetek_leta = danes.replace(month=1, day=1)

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
    energija_danes = pridobi_energijo(danes)
    energija_vceraj = pridobi_energijo(vceraj)
    energija_zacetek_meseca = pridobi_energijo(zacetek_meseca)
    energija_zacetek_leta = pridobi_energijo(zacetek_leta)

    dnevna_razlika = round(energija_danes - energija_vceraj, 2)
    mesecna_razlika = round(energija_danes - energija_zacetek_meseca, 2)
    letna_razlika = round(energija_danes - energija_zacetek_leta, 2)

    mesec_slo = slovenski_meseci[danes.month]

    if dnevna_razlika > 0:
        telo = (
            f"ELEKTRARNA DELUJE!\n"
            f"Danes ({danes}) je bilo oddane v omrežje {dnevna_razlika} kWh električne energije.\n"
            f"V mesecu {mesec_slo} {danes.year} je bilo oddanih {mesecna_razlika} kWh.\n"
            f"V letu {danes.year} je bilo skupaj oddanih {letna_razlika} kWh."
        )
    else:
        telo = f"ELEKTRARNA NE DELUJE!\nDanes ({danes}) elektrarna ni delovala."

    print(f"➡️ Pošiljam e-pošto:\n{telo}")
    poslji_mail("Status elektrarne", telo)

except Exception as e:
    print("⚠️ Napaka pri izvajanju:")
    print(e)

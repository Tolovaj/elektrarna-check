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

# ReadingType kode
RT_ODDANA = "32.0.4.1.19.2.12.0.0.0.0.0.0.0.0.3.72.0"  # Oddana delovna energija ET
RT_PREJETA = "32.0.4.1.1.2.12.0.0.0.0.0.0.0.0.3.72.0"   # Prejeta delovna energija ET

# Datumi
danes = date.today()
vceraj = danes - timedelta(days=1)
zacetek_meseca = danes.replace(day=1)
zacetek_leta = danes.replace(month=1, day=1)

def pridobi_energijo(datum, reading_type):
    url = "https://api.informatika.si/mojelektro/v1/meter-readings"
    headers = {"X-API-TOKEN": API_TOKEN}
    params = {
        "usagePoint": MERILNO_MESTO,
        "startTime": datum.isoformat(),
        "endTime": datum.isoformat(),
        "option": f"ReadingType={reading_type}"
    }

    for poskus in range(10):
        print(f"➡️ Pošiljam zahtevo ({poskus + 1}/10) za datum {datum} - tip: {reading_type}")
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
    # Oddana energija
    oddana_danes = pridobi_energijo(danes, RT_ODDANA)
    oddana_vceraj = pridobi_energijo(vceraj, RT_ODDANA)
    oddana_mesec_zacetek = pridobi_energijo(zacetek_meseca, RT_ODDANA)
    oddana_leto_zacetek = pridobi_energijo(zacetek_leta, RT_ODDANA)

    oddana_dnevna = round(oddana_danes - oddana_vceraj, 2)
    oddana_mesecna = round(oddana_danes - oddana_mesec_zacetek, 2)
    oddana_letna = round(oddana_danes - oddana_leto_zacetek, 2)

    # Prejeta energija
    prejeta_danes = pridobi_energijo(danes, RT_PREJETA)
    prejeta_vceraj = pridobi_energijo(vceraj, RT_PREJETA)
    prejeta_mesec_zacetek = pridobi_energijo(zacetek_meseca, RT_PREJETA)
    prejeta_leto_zacetek = pridobi_energijo(zacetek_leta, RT_PREJETA)

    prejeta_dnevna = round(prejeta_danes - prejeta_vceraj, 2)
    prejeta_mesecna = round(prejeta_danes - prejeta_mesec_zacetek, 2)
    prejeta_letna = round(prejeta_danes - prejeta_leto_zacetek, 2)

    mesec_slo = slovenski_meseci[danes.month]

    # Sestavi poročilo
    telo = (
        f"ELEKTRARNA DELUJE!\n"
        f"ODDANO V OMREŽJE:\n"
        f"Danes: ({danes}): {oddana_dnevna} kWh\n"
        f"{mesec_slo}: {oddana_mesecna} kWh\n"
        f"{danes.year}: {oddana_letna} kWh\n\n"
        f"PORABA IZ OMREŽJA:\n"
        f"Danes: {prejeta_dnevna} kWh\n"
        f"V mesecu {mesec_slo} {danes.year}: {prejeta_mesecna} kWh\n"
        f"V letu {danes.year}: {prejeta_letna} kWh"
    )

    print(f"➡️ Pošiljam e-pošto:\n{telo}")
    poslji_mail("Status elektrarne", telo)

except Exception as e:
    print("⚠️ Napaka pri izvajanju:")
    print(e)

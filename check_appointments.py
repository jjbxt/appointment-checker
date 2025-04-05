# import os
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup



WEBHOOK_URL = "https://discord.com/api/webhooks/1357845564770750585/UcDO_Ivzeo1E4CnBhtfQfIH8S9ZYOISQW8Di-hzOH5lIeE0Dt1vYkQOHX3xV6SsLZi-b"

def send_notification(message):
    data = {
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("✅ Message sent to Discord.")
    else:
        print("❌ Error:", response.text)


# BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# def send_telegram(message):
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     payload = {"chat_id": CHAT_ID, "text": message}
#     requests.post(url, data=payload)


# MTM1Nzg0MDIzODA0MjY4MTQ0NA.G0R3kJ.225Yzh-YszwATPwJOaoOmWTlIvNK4QMkme7WcI

# moj discord token od bota

# webhook url

# https://discord.com/api/webhooks/1357845564770750585/UcDO_Ivzeo1E4CnBhtfQfIH8S9ZYOISQW8Di-hzOH5lIeE0Dt1vYkQOHX3xV6SsLZi-b

url = "https://e-uprava.gov.si/si/javne-evidence/prosti-termini/content/singleton.html"
params = {
    "lang": "si",
    "type": "1",
    "cat": "6",
    "izpitniCenter": "18",
    "lokacija": "223",
    "offset": "0",
    "sentinel_type": "ok",
    "sentinel_status": "ok",
    "is_ajax": "1",
    "complete": "true",
    "page": "10"
}
headers = {
    "User-Agent": "Mozilla/5.0"
}


seen_path = Path(".cache/seen.json")
seen_path.parent.mkdir(exist_ok=True)

seen = set()
if seen_path.exists():
    with open(seen_path, "r") as f:
        seen_list = json.load(f)
        seen = set(tuple(item) for item in seen_list)


def fetch_data():
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    new_appointments = []
    seen_this_time = set()
 
    for box in soup.select(".js_dogodekBox.dogodek"):
        # Get the date from span.js_dateDiff
        date_elem = box.select_one("span.js_dateDiff")
        date = date_elem["data-value"] if date_elem else "N/A"

        # Get the time
        time = "N/A"
        for div in box.find_all("div"):
            if div.text.strip().startswith("Začetek ob"):
                bold = div.find("span", class_="bold")
                if bold:
                    time = bold.get_text(strip=True)
                break

        entry = (date, time)
        # print(entry)
        if entry not in seen:
            seen_this_time.add(entry)
            new_appointments.append(entry)

    seen.update(seen_this_time)
    return new_appointments


def main():
    # print("Starting appointment checker...")
    # while True:
    new = fetch_data()
    if new:
        # print("\n🆕 New appointments found:")
        # for date, time_val in new:
        #     print(f"📅 {date} ob 🕒 {time_val}")
        send_notification("New appointments found:\n\n```" + "\n".join([f"{date} at {time_val}" for (date, time_val) in new]) + "```")
    else:
        send_notification("No new appointments found.")
        pass
    with open(seen_path, "w") as f:
        json.dump(list(seen), f)

if __name__ == "__main__":
    main()

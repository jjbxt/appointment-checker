import time
import requests
from bs4 import BeautifulSoup

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

seen = set()

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
        if entry not in seen:
            seen.add(entry)
            new_appointments.append(entry)

    return new_appointments


def main():
    print("Starting appointment checker...")
    while True:
        new = fetch_data()
        if new:
            print("\n🆕 New appointments found:")
            for date, time_val in new:
                print(f"📅 {date} ob 🕒 {time_val}")
        else:
            print("No new appointments.")

        time.sleep(10)  # Wait for 5 minutes

if __name__ == "__main__":
    main()
import subprocess
import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PARKING_CSV = os.path.join(DATA_DIR, "parking.csv")
TRAFFIC_CSV = os.path.join(DATA_DIR, "traffic.csv")

PARKING_URL = "https://www.chadstone.com.au/api/parking"
TRAFFIC_URL = "https://www.chadstone.com.au/api/traffic"

CAR_PARK_MAP = {
    "616a72f7-85b0-439e-8f65-628a9807ab16": "A",
    "552a29ab-8cd0-4f88-a21d-25cda056538b": "B",
    "fa6fdfcc-ba17-4f56-949b-2d9be220b283": "C",
    "3998a27d-eaeb-4498-87ea-54b7060930e4": "E",
    "80ed54e9-8f85-44f2-adc9-94659820b6d9": "F",
}

CURL_HEADERS = [
    "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "-H", "Accept: application/json",
    "-H", "Referer: https://www.chadstone.com.au/directions/parking",
]


def now_str():
    return datetime.now(timezone(timedelta(hours=10))).strftime("%Y-%m-%d %H:%M:%S")


def curl_json(url):
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15"] + CURL_HEADERS + [url],
        capture_output=True, text=True, timeout=20
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed with code {result.returncode}: {result.stderr}")
    data = json.loads(result.stdout)
    return data


def scrape_parking(timestamp):
    data = curl_json(PARKING_URL)
    total_occ = data["totalOccupied"]
    total_vac = data["totalVacant"]
    rows = []
    for cp in data["occupancy"]:
        letter = CAR_PARK_MAP.get(cp["id"], "?")
        rows.append([timestamp, letter, cp["occupied"], cp["vacant"], total_occ, total_vac])
    return rows


def scrape_traffic(timestamp):
    today = datetime.now(timezone(timedelta(hours=10))).strftime("%Y-%m-%d")
    data = curl_json(f"{TRAFFIC_URL}?startDate={today}")
    rows = []
    for day in data["traffic"]["days"]:
        datestamp = day["datestamp"]
        for h in day["hours"]:
            hour = int(h["timestamp"][:13].split("T")[1]) if "T" in h["timestamp"] else 0
            occ = round(h["occupancy"], 6)
            alert = h["alertLevel"]
            rows.append([timestamp, datestamp, hour, occ, alert])
    return rows


def append_csv(filepath, rows, headers):
    is_new = not os.path.exists(filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(headers)
        writer.writerows(rows)


def main():
    timestamp = now_str()
    print(f"[{timestamp}] Starting scrape...")

    try:
        parking_rows = scrape_parking(timestamp)
        append_csv(PARKING_CSV, parking_rows, [
            "retrieved_at", "car_park", "occupied", "vacant",
            "total_occupied", "total_vacant"
        ])
        print(f"  Parking: {len(parking_rows)} car parks appended")
    except Exception as e:
        print(f"  Parking FAILED: {e}", file=sys.stderr)

    try:
        traffic_rows = scrape_traffic(timestamp)
        append_csv(TRAFFIC_CSV, traffic_rows, [
            "retrieved_at", "datestamp", "hour", "occupancy", "alert_level"
        ])
        print(f"  Traffic: {len(traffic_rows)} hour-rows appended")
    except Exception as e:
        print(f"  Traffic FAILED: {e}", file=sys.stderr)

    print(f"[{now_str()}] Done.")


if __name__ == "__main__":
    main()

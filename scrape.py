#!/usr/bin/env python3
import undetected_chromedriver as uc
import json
import time
import pygeohash as pgh

def fetch_tesla_data():
    """Fetch raw station data from Tesla API."""
    print("Launching browser...")
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Auto-detect Chrome version instead of hardcoding
    driver = uc.Chrome(options=options, headless=False)

    try:
        print("Visiting Tesla homepage...")
        driver.get("https://www.tesla.com")
        time.sleep(3)

        print("Fetching stations API...")
        driver.get("https://www.tesla.com/api/findus/get-locations?country=US&view=map")
        time.sleep(3)

        pre = driver.find_elements("tag name", "pre")
        content = pre[0].text if pre else driver.page_source

        if "Access Denied" in content or content.strip().startswith("<"):
            print("Error: Access denied")
            return None

        return json.loads(content)

    finally:
        driver.quit()

def filter_and_convert(data):
    """Filter for US non-Tesla-compatible stations and convert to geohashes."""
    stations = data.get("data", {}).get("data", [])

    nacs_geohashes = set()
    ccs_geohashes = set()

    for s in stations:
        lat = s.get("latitude")
        lon = s.get("longitude")

        if lat is None or lon is None:
            continue

        # Filter to US by longitude
        if not (-130 < lon < -60):
            continue

        sf = s.get("supercharger_function", {})
        accessibility = sf.get("charging_accessibility", "")

        geohash = pgh.encode(lat, lon, precision=6)

        if accessibility == "NACS Partner Enabled (Production)":
            nacs_geohashes.add(geohash)
        elif accessibility == "All Vehicles (Production)":
            ccs_geohashes.add(geohash)

    return {
        "nacs": sorted(list(nacs_geohashes)),
        "ccs": sorted(list(ccs_geohashes))
    }

def main():
    data = fetch_tesla_data()
    if not data:
        return False

    result = filter_and_convert(data)

    with open("compatible-stations.json", "w") as f:
        json.dump(result, f)

    print(f"Saved {len(result['nacs'])} NACS + {len(result['ccs'])} CCS geohashes to compatible-stations.json")

    # Also save raw data for debugging
    with open("stations.json", "w") as f:
        json.dump(data, f, indent=2)

    return True

if __name__ == "__main__":
    main()

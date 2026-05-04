import subprocess
from bs4 import BeautifulSoup
import time
from collections import defaultdict
import os
from datetime import datetime
import concurrent.futures
import random

def fetch_and_parse_page(url, proxy):
    """Fetches and parses a single page of election results."""
    page_party_results = defaultdict(lambda: defaultdict(int))
    try:
        # Note: ECI WAF blocks standard Python requests and browser user-agents.
        # Using plain curl works around this.
        cmd = ['curl', '-s', url]
        if proxy:
            cmd.extend(['--socks5-hostname', proxy.replace("socks5h://", "").replace("socks5://", "")])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        html = result.stdout
        
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table-striped')
        if not table:
            return page_party_results
            
        tbody = table.find('tbody')
        if not tbody:
            return page_party_results
            
        for row in tbody.find_all('tr', recursive=False):
            cols = row.find_all('td', recursive=False)
            if len(cols) >= 4:
                round_info = cols[2].text.strip()
                # The leading party is in the 4th column, inside a nested table
                party_cell = cols[3]
                nested_td = party_cell.find('td')
                if nested_td:
                    party_name = nested_td.text.strip()
                    if party_name:
                        status = 'Leading'  # Default to Leading
                        try:
                            if 'declared' in round_info.lower():
                                status = 'Won'
                            else:
                                parts = round_info.split('/')
                                if len(parts) == 2:
                                    rounds_checked, total_rounds = map(int, parts)
                                    if rounds_checked > 0 and rounds_checked == total_rounds:
                                        status = 'Won'
                        except (ValueError, IndexError):
                            pass  # If parsing fails, default to Leading
                        page_party_results[party_name][status] += 1
    except Exception as e:
        print(f"Error fetching or parsing page {url}: {e}")
    return page_party_results

def fetch_results(base_url, max_pages=15, proxy=None):
    party_results = defaultdict(lambda: defaultdict(int))
    urls = [f"{base_url}{page}.htm" for page in range(1, max_pages + 1)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_pages) as executor:
        future_to_url = {executor.submit(fetch_and_parse_page, url, proxy): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            page_results = future.result()
            for party, statuses in page_results.items():
                for status, count in statuses.items():
                    party_results[party][status] += count
            
    return party_results

if __name__ == "__main__":
    base_url = "https://results.eci.gov.in/ResultAcGenMay2026/statewiseS25" # S25 is for West Bengal
    TOTAL_CONSTITUENCIES = 294 # Total number of assembly constituencies in West Bengal

    # We found that using default curl without a custom User-Agent works best.
    # The ECI Akamai WAF blocks Python requests and custom browser User-Agents from non-residential IPs.
    my_proxy = None

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"West Bengal Assembly Election Results - Live Updates")
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("======================================================")

        print("\nFetching results...")

        results = fetch_results(base_url, max_pages=15, proxy=my_proxy)
        total_declared = sum(sum(counts.values()) for counts in results.values())

        print("\nSeat Allocation:")
        print("-" * 60)

        sorted_parties = sorted(
            results.items(),
            key=lambda item: (
                -sum(item[1].values()),  # Sort by total seats (desc)
                -item[1].get('Won', 0),  # Then by won seats (desc)
                item[0]                  # Then by party name (asc)
            )
        )

        for party, counts in sorted_parties:
            won = counts.get('Won', 0)
            leading = counts.get('Leading', 0)
            total = won + leading
            print(f"{party}: {total} (Won: {won}, Leading: {leading})")
        print("-" * 60)
        print(f"AC Counted So Far: {total_declared}/{TOTAL_CONSTITUENCIES}")

        noisy_sleep = random.choice(range(280, 320, 1))
        print("\nPolling again in around 5 minutes ("+str(noisy_sleep)+" seconds to be precise)"+"... ")
        time.sleep(noisy_sleep)
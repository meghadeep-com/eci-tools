import subprocess
from bs4 import BeautifulSoup
import time
from collections import defaultdict
import os
from datetime import datetime
import random

def fetch_results(url, proxy=None):
    """Fetches and parses the summary page of election results."""
    party_results = defaultdict(lambda: defaultdict(int))
    try:
        # Note: ECI WAF blocks standard Python requests and browser user-agents.
        # Using plain curl works around this.
        cmd = ['curl', '-s', url]
        if proxy:
            cmd.extend(['--socks5-hostname', proxy.replace("socks5h://", "").replace("socks5://", "")])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        html = result.stdout

        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find('table', class_='table')
        if not table:
            table = soup.find('table', class_='table-striped')
        if not table:
            table = soup.find('table')
            
        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr') if tbody else table.find_all('tr')
            for row in rows:
                cols = [td.text.strip() for td in row.find_all(['td', 'th'])]
                if len(cols) >= 4 and cols[0] and cols[0].lower() != "party":
                    party_name = cols[0]
                    try:
                        won = int(cols[1])
                        leading = int(cols[2])
                        party_results[party_name]['Won'] += won
                        party_results[party_name]['Leading'] += leading
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error fetching or parsing page {url}: {e}")
        
    return party_results

if __name__ == "__main__":
    target_url = "https://results.eci.gov.in/ResultAcGenMay2026/partywiseresult-S25.htm" # S25 is for West Bengal
    TOTAL_CONSTITUENCIES = 294 # Total number of assembly constituencies in West Bengal
    MAJORITY_MARK = (TOTAL_CONSTITUENCIES // 2) + 1

    # We found that using default curl without a custom User-Agent works best.
    # The ECI Akamai WAF blocks Python requests and custom browser User-Agents from non-residential IPs.
    my_proxy = None

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"West Bengal Assembly Election Results - Live Updates")
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("======================================================")

        print("\nFetching results...")

        results = fetch_results(target_url, proxy=my_proxy)
        total_declared = sum(sum(counts.values()) for counts in results.values())

        # Determine the maximum party name length for alignment
        max_party_len = max((len(party) for party in results.keys()), default=0)

        sorted_parties = sorted(
            results.items(),
            key=lambda item: (
                -sum(item[1].values()), # Sort by total seats (desc)
                -item[1].get('Won', 0), # Then by won seats (desc)
                item[0]                 # Then by party name (asc)
            )
        )

        # Check if the leading party has reached a majority to adjust table width
        majority_achieved = False
        if sorted_parties:
            top_party_total = sum(sorted_parties[0][1].values())
            if top_party_total >= MAJORITY_MARK:
                majority_achieved = True

        print("\nSeat Allocation:")
        # Calculate dynamic line width, adding space for the majority marker if needed
        line_width = max(60, max_party_len + 31)
        if majority_achieved:
            line_width += 13 # for " <-- Majority"

        print("-" * line_width)

        for i, (party, counts) in enumerate(sorted_parties):
            won = counts.get('Won', 0)
            leading = counts.get('Leading', 0)
            total = won + leading
            output_line = f"{party:<{max_party_len}} : {total:>3} (Won: {won:>3}, Leading: {leading:>3})"
            # Add marker only for the first party if majority is achieved
            if i == 0 and majority_achieved:
                output_line += " <-- Majority"
            print(output_line)
        print("-" * line_width)
        print(f"AC Counted So Far: {total_declared}/{TOTAL_CONSTITUENCIES}")
        print(f"Majority Mark: {MAJORITY_MARK}")

        noisy_sleep = random.choice(range(100, 140, 1))
        print("\nPolling again in around 2 minutes ("+str(noisy_sleep)+" seconds to be precise)"+"... ")
        time.sleep(noisy_sleep)
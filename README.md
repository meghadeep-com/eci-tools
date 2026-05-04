# ECI West Bengal Election Results Scraper

A Python script to poll and display live results for the West Bengal Assembly elections directly from the Election Commission of India (ECI) website.

It provides a simple, command-line-based live view of the seat allocation, showing how many seats each party has won and is currently leading in.

## Features

- Fetches live election data for won and leading seats.
- Displays a continuously updated summary in the console.
- Uses `curl` to circumvent Web Application Firewall (WAF) restrictions on the ECI website that block standard Python HTTP clients.
- Employs concurrent requests for faster data retrieval across multiple result pages.
- Automatically refreshes data every 5 minutes.

## Prerequisites

Before you run the script, make sure you have the following installed:

- **Python 3.x**
- **`curl`**: This command-line tool is used to fetch the web page content.
  - On macOS and most Linux distributions, `curl` is pre-installed.
  - On Windows, you may need to install it or use Windows Subsystem for Linux (WSL).

## Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd eci-tools
    ```

2.  **Install Python dependencies:**
    Create a virtual environment (recommended) and install the packages from `requirements.txt`.
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Usage

Simply run the `wb_poll.py` script from your terminal:

```sh
python wb_poll.py
```

The script will clear the console, fetch the latest results, and display them. It will automatically poll for new data every 5 minutes. To stop the script, press `Ctrl+C`.

## Configuration

- **Election URL**: The `base_url` variable in `wb_poll.py` is set for a specific election (e.g., May 2026 West Bengal Assembly election, code `S25`). You will need to update this URL for different elections by inspecting the ECI results website.
- **Proxy**: If you need to route traffic through a SOCKS5 proxy, you can set the `my_proxy` variable in the script (e.g., `my_proxy = "socks5h://127.0.0.1:9050"`).

## Disclaimer

This tool is for informational purposes only. The structure of the ECI website or its security measures (like the Akamai WAF) may change at any time, which could break this scraper.
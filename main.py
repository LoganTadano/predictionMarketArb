import pandas as pd
import requests
import json
import csv

#Basic KALSHI API for Grabbing Market Data
API_URL = "https://api.elections.kalshi.com/trade-api/v2/markets"


def main():
    data = fetch_JSON(API_URL)
    print(data)

def fetch_JSON(url):
    try:
        querystring = {"limit":"1"}
        response = requests.get(url, params=querystring)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # The .json() method directly parses the JSON response into a Python dictionary
        data = response.json()
        print("Data success")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None



if __name__ == "__main__":
    main()
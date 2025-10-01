import requests

def fetch_data():
    # Get markets with filtering
    response = requests.get(
        'https://api.elections.kalshi.com/trade-api/v2/markets',
        params={
            'status': 'open',
            'limit': 5
        }
    )

    markets = response.json()['markets']

    # Extract only the fields you need
    filtered_data = [
        {
            'ticker': market['ticker'],
            'title': market['title'],
            'status': market['status'],
            'volume': market['volume'],
            'rules_primary': market['rules_primary']

        }
        for market in markets
    ]
    return filtered_data
    
if __name__ == "__main__":
    data = fetch_data()
    print(data)
import requests


if __name__ == '__main__':
    url = 'http://127.0.0.1:5000/api/positions'
    data = {
        'ticker': 'ETH',
        'name': 'Ethereum',
    }

    p = requests.post(url, json=data)
    g = requests.get(url)
    print(g.json())

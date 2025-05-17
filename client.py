import requests
import pandas as pd


def populate_rds():
    positions_url = 'http://127.0.0.1:5000/api/positions'
    position_url = 'http://127.0.0.1:5000/api/position'
    portfolio = pd.read_csv('data/portfolio.csv')
    post_data = portfolio.to_dict('records')

    g = requests.get(positions_url).json()

    patch_data = []
    existing_symbols = {existing_symbol['ticker']: existing_symbol['id'] for existing_symbol in g}

    for record in post_data:
        if record['ticker'] in existing_symbols:
            p = requests.patch(position_url + '/' + f'{existing_symbols[record['ticker']]}', json=record).json()
        else:
            p = requests.post(positions_url, json=record).json()
        print(p)
    g = requests.get(positions_url)
    print(g.json())


if __name__ == '__main__':
    populate_rds()

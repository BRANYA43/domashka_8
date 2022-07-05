from datetime import datetime, timedelta
from argparse import ArgumentParser
import csv
import json

import requests
from tabulate import tabulate


def load_symbols_json() -> dict:
    url = 'https://api.exchangerate.host/symbols'
    try:
        currencies = load_file_json('symbols.json')
    except FileNotFoundError:
        response_url_2 = get_response_json(url)
        currencies = {'symbols': []}
        for currency in response_url_2['symbols']:
            currencies['symbols'].append(currency)
        save_file_json('symbols.json', currencies)
    return currencies


def check_correct_currency(currency: str, currencies: dict, default_currency: str) -> str:
    currency = currency.upper()
    for curr in currencies['symbols']:
        if currency == curr:
            return currency
    return default_currency


def get_response_json(url: str, parameters=None | dict) -> json:
    return requests.get(url, params=parameters).json()


def is_valid_date(date: str) -> bool:
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        print(f'Неправилильний формат дати, має бути YYYY-MM-DD')
        return False


def comparison_dates(date_now: datetime, date_input: datetime) -> bool:
    if date_input < date_now:
        return True
    else:
        return False


def create_dates_list(date: str) -> list:
    ret = []
    date_now = datetime.now()
    if is_valid_date(date):
        date_input = datetime(*[int(elem) for elem in date.split('-')])
        if comparison_dates(date_now, date_input):
            while date_input <= date_now:
                ret.append(date_input.strftime("%Y-%m-%d"))
                date_input += timedelta(days=1)
        else:
            ret.append(date_now.strftime("%Y-%m-%d"))
    return ret


def get_create_row_tab(date: str, currency_from: str, currency_to: str, amount: float) -> list:
    url = 'https://api.exchangerate.host/convert'
    parameters: dict[str, str | float] = {'date': date, 'from': currency_from, 'to': currency_to, 'amount': amount}
    response = get_response_json(url, parameters)
    return [date, currency_from, currency_to, amount, response['info']['rate'], response['result']]


def get_create_tab(dates: list, currency_from: str, currency_to: str, amount: float) -> list:
    ret = [['date', 'from', 'to', 'amount', 'rate', 'result']]
    for date in dates:
        ret.append(get_create_row_tab(date, currency_from, currency_to, amount))
    return ret


def get_file_name(currency_from: str, currency_to: str, amount: float) -> str:
    return f'{datetime.now().strftime("%Y-%m-%d")}-{currency_from}-{currency_to}-{amount}.txt'


def save_file_cvs(file_name: str, table: list):
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in table:
            writer.writerow(row)


def save_file_json(file_name: str, some_dict: dict):
    with open(file_name, 'w') as f:
        json.dump(some_dict, f)


def load_file_json(file_name: str) -> dict:
    with open(file_name, 'r') as f:
        return json.load(f)


def get_args():
    parser = ArgumentParser(prog='Онлайн конвертер валют')
    parser.add_argument('-from', '--currency_from', default='USD',
                        help='Валюта яку конвертують. За замовчуванням USD.')
    parser.add_argument('-to', '--currency_to', default='UAH',
                        help='Валюта в яку конвертують. За замовчуванням UAH.')
    parser.add_argument('-a', '--amount', type=float, default=100.00,
                        help='Кількість грошей якую треба конвертувати. За замовчуванням 100.00')
    parser.add_argument('--start_date', default=datetime.now().strftime('%Y-%m-%d'),
                        help=f'Дата у форматі YYYY-MM-DD. За замовчуванням {datetime.now().strftime("%Y-%m-%d")}.')

    parser.add_argument('--save_file', action='store_true',
                        help='Зберігти відповідь у файл.За замовчуванням видає у консоль.')
    return parser.parse_args()


def main():
    currencies_list = load_symbols_json()

    args = get_args()
    args.currency_from = check_correct_currency(args.currency_from, currencies_list, 'USD')
    args.currency_to = check_correct_currency(args.currency_to, currencies_list, 'UAH')
    dates = create_dates_list(args.start_date)

    tab = get_create_tab(dates, args.currency_from, args.currency_to, args.amount)

    if args.save_file:
        file_name = get_file_name(args.currency_from, args.curryncy_to, args.amount)
        save_file_cvs(file_name, tab)
    else:
        print(tabulate(tab))


if __name__ == '__main__':
    main()

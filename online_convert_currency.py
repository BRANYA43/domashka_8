from pprint import pp
from datetime import datetime, timedelta
from argparse import ArgumentParser


import requests
from requests import Response
from tabulate import tabulate


def get_response_json( date: str, currency_from: str, currency_to: str, amount: float) -> Response:
    params = {'date': date, 'from': currency_from, 'to': currency_to, 'amount': amount}
    return requests.get('https://api.exchangerate.host/convert', params=params).json()


def get_create_row_tab(date: str, currency_from: str, currency_to: str, amount: float) -> list:
    response = get_response_json(date, currency_from, currency_to, amount)
    return [date, currency_from, currency_to, amount, response['info']['rate'], response['result']]


def get_create_tab(dates: list, currency_from: str, currency_to: str, amount: float) -> list:
    ret = [['date', 'from', 'to', 'amount', 'rate', 'result']]
    for date in dates:
        ret.append(get_create_row_tab(date, currency_from, currency_to, amount))
    return ret


def validate(date: str) -> bool:
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        print('Неправилильний формат дати, має бути YYYY-MM-DD')
        return False


def is_date(date_now: datetime, date_input: datetime) -> bool:
    if date_input < date_now:
        return True
    else:
        return False


def iter_date(date: str) -> list:
    ret = []
    date_now = datetime.now()

    if validate(date):
        date_input = datetime(*[int(elem) for elem in date.split('-')])
        print(date_input)

        if is_date(date_now, date_input):
            while date_input <= date_now:
                ret.append(date_input.strftime("%Y-%m-%d"))
                date_input += timedelta(days=1)

            return ret

    return [date_now.strftime("%Y-%m-%d")]


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-from', '--currency_from', default='USD',
                        help='Валюта яку конвертують.')
    parser.add_argument('-to', '--currency_to', default='UAH',
                        help='Валюта в яку конвертують.')
    parser.add_argument('--amount', type=float, default=100.00,
                        help='Кількість грошей якую треба конвертувати.')
    parser.add_argument('--start_date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='')
    return parser.parse_args()


args = get_args()
dates = iter_date(args.start_date)
currency_from = args.currency_from
currency_to = args.currency_to
amount = args.amount

print()

tab = get_create_tab(dates, currency_from, currency_to, amount)
print(tabulate(tab))


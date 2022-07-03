from datetime import datetime, timedelta
from argparse import ArgumentParser
import csv


import requests
from requests import Response
from tabulate import tabulate


def get_file_name(currency_from: str, currency_to: str, amount: float) -> str:
    return f'{datetime.now().strftime("%Y-%m-%d")}-{currency_from}-{currency_to}-{amount}.txt'


def save_file(file_name: str, table: list):
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in table:
            writer.writerow(row)


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


def valid_date(date: str) -> bool:
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
    if valid_date(date):
        date_input = datetime(*[int(elem) for elem in date.split('-')])

        if comparison_dates(date_now, date_input):
            while date_input <= date_now:
                ret.append(date_input.strftime("%Y-%m-%d"))
                date_input += timedelta(days=1)
        else:
            ret.append(date_now.strftime("%Y-%m-%d"))

    return ret


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-from', '--currency_from', default='USD',
                        help='Валюта яку конвертують.')
    parser.add_argument('-to', '--currency_to', default='UAH',
                        help='Валюта в яку конвертують.')
    parser.add_argument('--amount', type=float, default=100.00,
                        help='Кількість грошей якую треба конвертувати.')
    parser.add_argument('--start_date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='Дата у форматі YYYY-MM-DD')

    parser.add_argument('--save_file', action='store_true')
    return parser.parse_args()


def main():
    args = get_args()
    dates = create_dates_list(args.start_date)
    tab = get_create_tab(dates, args.currency_from, args.currency_to, args.amount)

    if args.save_file:
        file_name = get_file_name(args.currency_from, args.curryncy_to, args.amount)
        save_file(file_name, tab)
    else:
        print(tabulate(tab))


if __name__ == '__main__':
    main()

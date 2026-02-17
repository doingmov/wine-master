from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from collections import defaultdict
import argparse
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas


def get_year_word(age):
    if 11 <= age % 100 <= 14:
        return "лет"
    last_digit = age % 10
    if last_digit == 1:
        return "год"
    elif 2 <= last_digit <= 4:
        return "года"
    else:
        return "лет"


def main():
    parser = argparse.ArgumentParser(description="Запуск винодельного сайта")
    parser.add_argument(
        "--wines-file",
        default=os.getenv("WINES_FILE", "wines.xlsx"),
        help="Путь к Excel файлу с данными о винах"
    )
    args = parser.parse_args()
    wines_path = args.wines_file

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    foundation_year = 1920
    current_year = datetime.now().year
    winery_age = current_year - foundation_year
    year_word = get_year_word(winery_age)

    wines_df = pandas.read_excel(
        wines_path,
        na_values=['', 'nan'],
        keep_default_na=False,
        engine='openpyxl'
    )

    products = defaultdict(list)

    for _, row in wines_df.iterrows():
        category = row.get('Категория', 'Без категории')
        grape = row.get('Сорт', '') or ""
        price = row.get('Цена', '')
        promo = row.get('Акция', '') == "Выгодное предложение"

        wine_data = {
            "name": row.get('Название', ''),
            "grape": grape,
            "price": price,
            "img": f"images/{row['Картинка']}" if row.get('Картинка') else "",
            "promo": promo
        }
        products[category].append(wine_data)

        if isinstance(price, (int, float)):
            min_price = min(
                item['price'] for item in products[category] 
                if isinstance(item['price'], (int, float))
            )
            for item in products[category]:
                if isinstance(item['price'], (int, float)):
                    item['promo'] = item['price'] == min_price or item['promo']

    rendered_page = template.render(
        winery_age=winery_age,
        year_word=year_word,
        products=products
    )

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()

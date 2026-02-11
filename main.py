from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from collections import defaultdict
from pprint import pprint

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


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

foundation_year = 1920
current_year = datetime.now().year
winery_age = current_year - foundation_year
year_word = get_year_word(winery_age)

wines_df = pandas.read_excel('wines.xlsx', na_values=['', 'nan'], keep_default_na=False)

products = defaultdict(list)
for _, row in wines_df.iterrows():
    category = row.get('Категория', 'Без категории')
    grape = row ['Сорт'] if pandas.notna(row['Сорт']) else ""

    wine_data = {
        "name": row.get('Название', ''),
        "grape": grape,
        "price": row.get('Цена', ''),
        "img": f"images/{row['Картинка']}" if row.get('Картинка') else "",
        "promo": row.get('Акция', '') == "Выгодное предложение"
    }
    products[category].append(wine_data)


for category, items in products.items():
    if not items:
        continue
    min_price = min(item['price'] for item in items)
    for item in items:
        if item['price'] == min_price:
            item['promo'] = True


rendered_page = template.render(
    winery_age=winery_age,
    year_word=year_word,
    products=products
)

with open('index.html', 'w', encoding='utf8') as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()

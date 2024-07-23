import requests
import json 
import csv
import os
import re

from xlsxwriter import Workbook
from typing import List, Dict
from bs4 import BeautifulSoup
from itertools import chain

from consts import headers, IMAGES_PATH, ORDERED_LIST

def get_soup_from_url(url) -> BeautifulSoup:
    src = requests.get(url, headers=headers).text
    soup = BeautifulSoup(src, 'lxml')
    return soup

def get_product_info(soup: BeautifulSoup, url) -> Dict[str, str]:
    try:
        name = soup.find(class_="product-detail-name").text.strip()
    except Exception:
        name = "No name"

    try:
        price = soup.find(class_="product-detail-price").text.strip()
    except Exception:
        price = "No price"

    try:
        article = soup.find(class_="product-detail-ordernumber").text.strip()
    except Exception:
        article = "No article"

    try:
        ean_and_article = soup.find_all(class_="product-detail-ordernumber")
        if len(ean_and_article) == 2:
            ean = ean_and_article[1].text.strip()
        else:
            raise Exception
    except Exception:
        ean = "0"

    try:
        categories = soup.find_all(class_="breadcrumb-title")
        categories = [cat.text for cat in categories]
        if len(categories) < 2:
            categories.append('')
    except Exception:
        categories = ['', '']

    try:
        description = soup.find(class_="product-detail-description-text").text.strip()
    except Exception:
        description = "No description"

    try:
        package_size = soup.find(class_="product-detail-paketgroesse").text.strip()
    except Exception:
        package_size = "No size"

    try:
        weight = soup.find(class_="side top").text.strip()
    except Exception:
        weight = "No weight"

    try:
        d = soup.find_all(class_="side-text")
        demensions = f"{d[0].text}*{d[1].text}*{d[2].text}"
    except Exception:
        demensions = "No demensions"

    try:
        avaliable = soup.find(class_="delivery-information delivery-available").text.strip()
    except Exception:
        avaliable = "Not avaliable"

    result_row = {
        "url": url,
        "article": article,
        "EAN": ean,
        "name": name,
        "weight": weight,
        "price": price,
        "avaliable": avaliable,
        "description": description,
        "package_size": package_size,
        "demensions": demensions,
        "category_1": categories[0],
        "category_2": categories[1],
    }

    return result_row

def get_picture_urls(soup: BeautifulSoup) -> List[str]:
    try:
        urls = soup.find_all("img", class_="gallery-slider-thumbnails-image")
        urls = [el['src'] for el in urls[0:int(len(urls)/2)]]
        if urls == []:
            raise Exception
    except Exception:
        try: 
            urls = [soup.find(class_="cms-element-image-gallery").find("img")["src"]]
        except Exception:
            urls = []
    
    return urls

def get_info_and_pictures(url: str) -> Dict:
    soup = get_soup_from_url(url)
    product_info = get_product_info(soup, url)
    picture_urls = get_picture_urls(soup)

    cat_1 = re.sub(r'[^\w_. -]', '_', product_info["category_1"])
    cat_2 = re.sub(r'[^\w_. -]', '_', product_info["category_2"])
    dir_path = os.path.join(IMAGES_PATH, cat_1, cat_2, product_info["article"]) 

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for i, url in enumerate(picture_urls, 1):
        image = requests.get(url).content
        image_name = f"{product_info['article']}_{i}.jpg"
        product_info[f"image_{i}"] = image_name
        with open(os.path.join(dir_path, image_name), "wb") as file:
            file.write(image)

    return product_info

def write_to_excel(ws, product: Dict) -> None:
    global row
    for _key,_value in product.items():
        col=ORDERED_LIST.index(_key)
        ws.write(row,col,_value)
    row += 1

def main():
    with open('category_to_products.json', 'r') as file:
        categories_and_products_urls = dict(json.load(file))

    urls = sorted(set(chain.from_iterable(categories_and_products_urls.values())))

    wb=Workbook("result.xlsx")
    ws=wb.add_worksheet("Data from RDX-DE")

    for header in ORDERED_LIST:
        col=ORDERED_LIST.index(header)
        ws.write(0, col, header)

        with open('data/products_sync.csv', 'w', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')

            writer.writerow(ORDERED_LIST)

    for i, url in enumerate(list(urls), 1):
        print(f"Processing with page {i}/{len(urls)}")
        product_info = get_info_and_pictures(url)

        with open('data/products_sync.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(product_info.values())

        write_to_excel(ws, product_info)

    wb.close()
        

if __name__ == '__main__':
    main()

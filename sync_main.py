import requests
import json

from typing import List, Dict
from bs4 import BeautifulSoup
from xlsxwriter import Workbook

from consts import ORDERED_LIST, headers, MAIN_URL

row = 1
products_data = []

def _write_to_excel(ws, product: Dict) -> None:
    global row
    for _key,_value in product.items():
        col=ORDERED_LIST.index(_key)
        ws.write(row,col,_value)
    row += 1

def _get_soup_from_url(url: str) -> BeautifulSoup:
    src = requests.get(url, headers=headers).text
    soup = BeautifulSoup(src, 'lxml')
    return soup

def _get_count_pictures(soup: BeautifulSoup) -> int:
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
    
    return len(urls)

def get_product_info(soup: BeautifulSoup) -> Dict:
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
        "article": article,
        "EAN": ean,
        "name": name,
        "weight": weight,
        "price": price,
        "avaliable": avaliable,
        "description": description,
        "package_size": package_size,
        "demensions": demensions,
    }

    return result_row

def get_cards_urls(url_2: str):
    soup = _get_soup_from_url(url_2)
    cards = soup.find_all(class_="product-info")
    urls = [el.find("a")["href"] for el in cards]

    return urls

def get_categories_2(url_1: str) -> Dict[str, List[str]]:
    soup = _get_soup_from_url(url_1)

    cat_group = soup.find(class_="category-navigation level-1").find_all(class_="category-navigation-link")
    categories_2_urls = [el['href'] for el in cat_group]
    categories_2 = [el.text.strip() for el in cat_group]

    return {
        "names": categories_2,
        "urls": categories_2_urls
    }

def get_categories_1() -> Dict[str, List[str]]:
    soup = _get_soup_from_url(MAIN_URL)
    links = soup.find_all(class_="category-navigation-link")[:41]

    categories_1_urls = [el['href'] for el in links]
    categories_1 = [el.text.strip() for el in links]

    return {
        "names": categories_1,
        "urls": categories_1_urls
    }

def main():
    wb=Workbook("data/products.xlsx")
    ws=wb.add_worksheet("Data from RDX-DE")

    for header in ORDERED_LIST:
        col=ORDERED_LIST.index(header)
        ws.write(0, col, header)

    cat_1 = get_categories_1()

    for cat_name_1, url_1 in zip(cat_1["names"], cat_1["urls"]):
        print(f"{cat_name_1}: {url_1}")

        cat_2 = get_categories_2(url_1)

        for cat_name_2, url_2 in zip(cat_2["names"], cat_2["urls"]):
            print(f"    - {cat_name_2}: {url_2}")
            for product_url in get_cards_urls(url_2):
                print(f"        * {product_url}")
                soup = _get_soup_from_url(product_url)
                product_info = get_product_info(soup)
                product_info["category_1"] = cat_name_1
                product_info["category_2"] = cat_name_2
                product_info["url"] = product_url

                for i in range(1, _get_count_pictures(soup) + 1):
                    product_info[f"image_{i}"] = f"{product_info['article']}_{i}"

                _write_to_excel(ws, product_info)
                products_data.append(product_info)

    with open('data/products.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    wb.close()

if __name__ == "__main__":
    main()

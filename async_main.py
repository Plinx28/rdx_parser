import aiohttp
import asyncio
import aiofiles
import csv
import json
import os
import re
import time

from bs4 import BeautifulSoup
from itertools import chain
from consts import ORDERED_LIST


start_time = time.time()

products_data = []

IMAGES_PATH = "images_async/"

with open('data/products.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')

    writer.writerow(ORDERED_LIST)

max_retries = 10


async def get_page_data(session: aiohttp.ClientSession, url: str, semaphor: asyncio.Semaphore, counter: int):
    async with semaphor:
        async with session.get(url) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, 'lxml')

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

            product_info = {
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

            cat_1 = re.sub(r'[^\w_. -]', '_', product_info["category_1"])
            cat_2 = re.sub(r'[^\w_. -]', '_', product_info["category_2"])
            dir_path = os.path.join(IMAGES_PATH, cat_1, cat_2, product_info["article"])

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            try:
                picture_urls = soup.find_all("img", class_="gallery-slider-thumbnails-image")
                picture_urls = [el['src'] for el in picture_urls[0:int(len(picture_urls) / 2)]]
                if picture_urls == []:
                    raise Exception
            except Exception:
                try:
                    picture_urls = [soup.find(class_="cms-element-image-gallery").find("img")["src"]]
                except Exception:
                    picture_urls = []

            for i, pic_url in enumerate(picture_urls, 1):
                retries = 0
                while retries < max_retries:
                    try:
                        async with session.get(pic_url) as image_response:
                            if image_response.status == 200:
                                image = await image_response.read()
                                image_name = f"{product_info['article']}_{i}.jpg"
                                product_info[f"image_{i}"] = image_name
                                f = await aiofiles.open(os.path.join(dir_path, image_name), "wb")
                                await f.write(image)
                                await f.close()
                                break
                    except (aiohttp.client_exceptions.ServerDisconnectedError,
                            aiohttp.client_exceptions.ClientOSError) as e:
                        print(f"Ошибка при загрузке изображения {pic_url}: {e}. Попытка {retries + 1}/{max_retries}")
                        retries += 1
                        await asyncio.sleep(1)

            products_data.append(product_info)

            with open('data/products.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(product_info.values())

            print(f"{counter}'s product {url} downloaded")


async def gather_data():
    timeout = aiohttp.ClientTimeout(total=660)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        with open('category_to_products.json', 'r') as file:
            categories_and_products_urls = dict(json.load(file))
        urls = set(chain.from_iterable(categories_and_products_urls.values()))
        urls = sorted(urls)

        semaphore = asyncio.Semaphore(3)
        tasks = []
        print(f'{len(urls)} - count of all products')
        for i, url in enumerate(urls, 1):
            task = asyncio.create_task(get_page_data(session, url, semaphore, i))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())

    with open('data/products.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    finish_time = round(time.time() - start_time)
    print(f'Total time: {finish_time} second')


if __name__ == "__main__":
    main()

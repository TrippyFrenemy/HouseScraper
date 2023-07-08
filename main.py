import datetime
import os
import re
import json
from bs4 import BeautifulSoup
import time
import asyncio
import aiohttp


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
url_global = "https://rieltor.ua/flats-sale/#10.5/50.4333/30.5167"
house_data = []

start_time = time.time()


async def get_all_pages(session, page, pages_count):
    url = f"https://rieltor.ua/flats-sale/?page={page}#10.5/50.4333/30.5167"

    async with session.get(url=url, headers=headers) as req:
        soup = BeautifulSoup(await req.text(), "lxml")
        house_items = soup.find_all("div", class_="catalog-card")

        for hi in house_items:
            h_url = hi.find("a", class_="catalog-card-media")["href"]
            h_price = hi.find("strong", class_="catalog-card-price-title").text

            try:
                h_price_by_square = hi.find("div", class_="catalog-card-price-details").text.strip()
            except:
                h_price_by_square = "-"

            try:
                h_address = hi.find("div", class_="catalog-card-address").text
            except:
                h_address = "-"

            try:
                h_city = hi.find("a", {"data-analytics-event": "card-click-region"}).text
            except:
                h_city = "-"

            try:
                h_district = hi.find("a", {"data-analytics-event": "card-click-region"}).next_sibling.next_sibling.text.strip()
            except:
                h_district = "-"

            try:
                h_subway = hi.find("a", class_="-subway").text.strip()
            except:
                h_subway = "-"

            try:
                h_temp = hi.find_all("a", class_="catalog-card-chip -orient")
                if len(h_temp) == 2:
                    h_microdistrict = h_temp[0].text.strip()
                    h_zk = h_temp[1].text.strip()
                elif h_temp[0].text.startswith("ЖК"):
                    h_zk = h_temp[0].text.strip()
                    h_microdistrict = "-"
                else:
                    h_microdistrict = h_temp[0].text.strip()
                    h_zk = "-"
            except:
                h_microdistrict = "-"
                h_zk = "-"

            h_num_of_rooms = hi.find("div", class_="catalog-card-details-row").text.strip()
            h_square = hi.find("div", class_="catalog-card-details-row").next_sibling.next_sibling.text.strip().replace(" ", "")
            h_floors = hi.find("div", class_="catalog-card-details-row").next_sibling.next_sibling.next_sibling.next_sibling.text.strip()

            h_publication = hi.find("div", class_="catalog-card-update").text.strip()
            h_publication = re.sub(r".*\nДод: ", "", h_publication)

            house_data.append(
            {
                "cost": h_price,
                "cost_by_square": h_price_by_square,
                "address": h_address,
                "district": h_district,
                "microdistrict": h_microdistrict,
                "zk": h_zk,
                "city": h_city,
                "subway": h_subway,
                "description": "опис обєкта, бла-бла-бла",
                "floor": h_floors,
                "number_rooms": h_num_of_rooms,
                "square_meters": h_square,
                "publication_date": h_publication,
                "contacts": "ім’я, телефон",
                "link": h_url
            })
        print(f"[INFO] {page} page downloaded as html file / {pages_count}")


async def gather_data():
    async with aiohttp.ClientSession() as session:
        request = await session.get(url=url_global, headers=headers)
        soup = BeautifulSoup(await request.text(), "lxml")
        pages_count = int(soup.find("div", class_="pagin_offers_wr").find_all("a")[-1].text)

        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_all_pages(session, page, pages_count))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    if not os.path.exists("data"):
        os.mkdir("data")
    asyncio.run(gather_data())

    cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
    with open(f"data/house_scaper_{cur_time}_async.json", "w", encoding="utf-8") as file:
        json.dump(house_data, file, indent=4, ensure_ascii=False)

    finish_time = time.time() - start_time
    print(f"[INFO] Time spent {finish_time}")


if __name__ == '__main__':
    main()

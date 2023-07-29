import os
import asyncio
import csv
import datetime
import json
import re
import time
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

headers = {
    "User-Agent": str(UserAgent().random)
}

url_global = "https://rieltor.ua/flats-sale/#10.5/50.4333/30.5167"

house_data = []

start_time = time.time()


async def get_description(session, h_url):
    async with session.get(url=h_url, headers=headers) as request_post:
        soup = BeautifulSoup(await request_post.text(), "lxml")
        try:
            return soup.find("div", class_="offer-view-section-text").text.strip().replace("\n", "  ")
        except:
            return "-"


async def get_all_pages(session, page, pages_count):
    url = f"https://rieltor.ua/flats-sale/?page={page}#10.5/50.4333/30.5167"
    try:
        async with session.get(url=url, headers=headers) as req:
            soup = BeautifulSoup(await req.text(), "lxml")
            house_items = soup.find_all("div", class_="catalog-card")

            for hi in house_items:
                h_url = hi.find("a", class_="catalog-card-media")["href"]
                try:
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

                    try:
                        h_author = hi.find("span", class_="catalog-card-author-title").text.strip()
                    except:
                        h_author = hi.find("a", class_="catalog-card-author-title").text.strip()
                    h_telephone = hi.find("div", {"data-jss": "ovContacts"}).text.strip().replace("\n", ", ")

                    h_description = await get_description(session, h_url)

                    house_data.append({
                        "cost": h_price,
                        "cost_by_square": h_price_by_square,
                        "address": h_address,
                        "district": h_district,
                        "microdistrict": h_microdistrict,
                        "zk": h_zk,
                        "city": h_city,
                        "subway": h_subway,
                        "description": h_description,
                        "floor": h_floors,
                        "number_rooms": h_num_of_rooms,
                        "square_meters": h_square,
                        "publication_date": h_publication,
                        "contacts": f"{h_author}, {h_telephone}",
                        "link": h_url
                    })
                except:
                    print(f"{h_url} have problems with parsing")
            print(f"[INFO] {page} page downloaded / {pages_count}")
    except:
        print(f"{url} {page} page have problems with parsing")


async def gather_data():
    async with aiohttp.ClientSession(trust_env=True) as session:
        request = await session.get(url=url_global, headers=headers)
        soup = BeautifulSoup(await request.text(), "lxml")

        pages_count = int(soup.find("div", class_="pagin_offers_wr").find_all("a")[-1].text)

        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_all_pages(session, page, pages_count))
            tasks.append(task)

        await asyncio.gather(*tasks)


def delete_repeats():
    data = house_data.copy()

    seen = {}
    unique_data = []

    for obj in data:
        key1 = obj['cost']
        key2 = obj['cost_by_square']
        key3 = obj['city']
        key4 = obj['address']
        key5 = obj['district']
        key6 = obj['microdistrict']
        key7 = obj['zk']
        key8 = obj['subway']
        key9 = obj['floor']
        key10 = obj['number_rooms']
        key11 = obj['square_meters']

        key_tuple = (key1, key2, key3, key4, key5, key6, key7, key8, key9, key10, key11)

        if key_tuple in seen:
            continue

        seen[key_tuple] = True
        unique_data.append(obj)

    return unique_data


def main():
    if not os.path.exists("data"):
        os.mkdir("data")
    asyncio.run(gather_data())

    cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")

    house_data = delete_repeats()

    with open(f"data/house_scaper_{cur_time}.json", "w", encoding="utf-8") as file:
        json.dump(house_data, file, indent=4, ensure_ascii=False)

    for house in house_data:
        with open(f"data/house_scaper_{cur_time}.csv", "a", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=',')

            writer.writerow(
                [
                    house["cost"],
                    house["cost_by_square"],
                    house["city"],
                    house["address"],
                    house["district"],
                    house["microdistrict"],
                    house["zk"],
                    house["subway"],
                    house["floor"],
                    house["number_rooms"],
                    house["square_meters"],
                    house["publication_date"],
                    house["contacts"],
                    house["link"],
                    house["description"]
                ]
            )

    finish_time = time.time() - start_time
    print(f"[INFO] Time spent {finish_time}")


if __name__ == '__main__':
    main()

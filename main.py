import os
import requests
from bs4 import BeautifulSoup
import time
import asyncio
import aiohttp


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
url_global = "https://rieltor.ua/flats-sale/#10.5/50.4333/30.5167"

start_time = time.time()

async def get_all_pages(session, page, pages_count):
    url = f"https://rieltor.ua/flats-sale/?page={page}#10.5/50.4333/30.5167"

    async with session.get(url=url, headers=headers) as req:

        with open(f"data/page_{page}.html", "w", encoding="utf-8") as file:
            file.write(await req.text())

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

    finish_time = time.time() - start_time
    print(f"[INFO] Time spent {finish_time}")

if __name__ == '__main__':
    main()

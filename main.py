import os
import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
url = "https://rieltor.ua/flats-sale/#10.5/50.4333/30.5167"


def get_all_pages():
    req = requests.get(url=url, headers=headers)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/page_1.html", "w", encoding="utf-8") as file:
        file.write(req.text)

    with open("data/page_1.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    pages_count = soup.find("div", class_="pagin_offers_wr").find_all("a")[-1].text
    print(pages_count)


def main():
    get_all_pages()


if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import notion_client

URL = "https://doctor2017.jumedicine.com/fourth-year/internal-medicine/"
PARENT_PAGE_ID = "<YOUR PAGE ID>"
NOTION_AUTH_KEY = "<YOUR AUTH TOKEN>"

response = requests.get(URL)

soup = BeautifulSoup(response.content, "lxml")

data = []

headers = soup.find_all('a', class_='header')

for header in headers:
    header_text = header.text
    daughter_list = header.find_next('ol').find_all('li')

    daughter_list_items = []
    for item in daughter_list:
        name = item.text
        link = item.find('a')['href']
        daughter_list_items.append({'name': name, 'link': link})

    data.append({'header': header_text, 'items': daughter_list_items})

output = []

for parent_item in data[4:-3]:
    for daughter_item in parent_item["items"]:
        daughter_item["category"] = parent_item["header"]
        output.append(daughter_item)

notion = notion_client.Client(auth=NOTION_AUTH_KEY)

database = notion.databases.create(
    parent={"type": "page_id", "page_id": PARENT_PAGE_ID},
    title=[{"type": "text", "text": {"content": "My Database 4"}}],
    properties={
        "No.": {"number": {}},
        "Name": {"title": {}},
        "Link": {"url": {}},
        "Category": {"select": {}},
        "Done": {"checkbox": {}}
    }
)

for number, item in enumerate(output):
    notion.pages.create(
        parent={
            "database_id": database["id"],
        },
        properties={
            "No.": {
                "number": number + 1,
            },
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": item["name"],
                        },
                    },
                ],
            },
            "Link": {
                "url": item["link"]
            },
            "Category": {
                "select": {
                    "name": item["category"]
                }
            },
        },
    )

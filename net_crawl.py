from db_api import dbAPI
from ytube import get_youtube_by_link as y_link


def update_links():
    db = dbAPI()
    lst = db.get_links_to_read()
    records = []
    for item in lst:
        data = y_link(item[0])
        records.append((data['id'], data['title'], item[0], data['author'], data['date'], data['duration'], data['tags']))
    db.insert_net(records)


if __name__ == '__main__':
    update_links()
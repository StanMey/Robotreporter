import csv
from datetime import datetime
from articles_app.models import Stocks, Articles

# from articles_app.models import Stocks
# from articles_app import data_helper_functions as dhf
# dhf.from_csv_to_Stocks(r"articles_app/data/AMX_prices.csv")

def from_csv_to_Stocks(data_path):

    with open(data_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                stock = Stocks()
                stock.indexx = row[7]
                stock.component = row[0]
                stock.volume = row[1]
                stock.s_open = row[2]
                stock.s_high = row[3]
                stock.s_low = row[4]
                stock.s_close = row[5]
                stock.date = datetime.strptime(row[6], '%d-%m-%Y %H:%M')

                stock.save()

                line_count += 1
        print(f'Processed {line_count} lines.')


# from articles_app.models import Articles
# from articles_app import data_helper_functions as dhf
# dhf.import_dummy_articles()

def import_dummy_articles():
    art_content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam feugiat justo eu luctus tempus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Mauris elementum a purus id vestibulum. Suspendisse potenti. Nam egestas, nisi quis faucibus venenatis, purus dui malesuada lacus, eget maximus tellus tellus nec libero. Phasellus at ipsum metus. Sed pharetra mollis luctus. Donec finibus ac dui at commodo. Ut in lorem at felis sollicitudin condimentum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."
    data = [
    {
        "title": "title of article 1",
        "content": art_content,
        "date": "2020-09-10 19:27:50",
        "author": "newsbot",
        "AI_version": 1.1
    },
    {
        "title": "title of article 2",
        "content": art_content,
        "date": "2020-09-11 19:27:50",
        "author": "newsbot",
        "AI_version": 1.1
    },
    {
        "title": "title of article 3",
        "content": art_content,
        "date": "2020-09-12 19:27:50",
        "author": "newsbot",
        "AI_version": 1.1
    },
    {
        "title": "title of article 4",
        "content": art_content,
        "date": "2020-09-13 19:27:50",
        "author": "newsbot",
        "AI_version": 1.1
    },
    {
        "title": "title of article 5",
        "content": art_content,
        "date": "2020-09-14 19:27:50",
        "author": "newsbot",
        "AI_version": 1.1
    },
    {
        "title": "title of article 6",
        "content": art_content,
        "date": "2020-09-15 19:27:50",
        "author": "newsbot",
        "AI_version": 1.2
    },
    {
        "title": "title of article 7",
        "content": art_content,
        "date": "2020-09-16 19:27:50",
        "author": "newsbot",
        "AI_version": 1.2
    }]
    
    line_count = 0
    for art in data:
        article = Articles()
        article.title = art["title"]
        article.content = art["content"]
        article.date = art["date"]
        article.author = art["author"]
        article.AI_version = art["AI_version"]

        article.save()
        line_count += 1

    print(f'Processed {line_count} lines.')
        
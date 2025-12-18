# !pip install pymongo
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.environ.get("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client["az_articles"]
collection = db["articles"]

try:
    with open('parsed_articles_complete.json', 'r', encoding='utf-8') as file:
        articles_data = json.load(file)
        print(f"загружено {len(articles_data)} статей")
except FileNotFoundError:
    print("ошибка, не тот файл загружен")

if articles_data:
    result = collection.insert_many(articles_data)
    print(f"добавлено {len(result.inserted_ids)} документов в коллекцию articles")

    print(f"документов в коллекции articles: {collection.count_documents({})}")
else:
    print("ошибка, в файле нет данных")

client.close()
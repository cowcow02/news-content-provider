import os
from datetime import datetime, time

from pymongo import MongoClient
from pymongo.collection import Collection


def get_collection() -> Collection:
    client = MongoClient(os.getenv('MONGO_URI'))
    database = client[os.getenv('MONGO_DATABASE_NAME')]
    return database.articles


def serialize_objects(cursor):
    return [serialize(article) for article in cursor]


def serialize(article):
    article.pop('_id')
    article['date'] = article['date'].strftime('%Y-%m-%d')
    if article.get('highlights'):
        article['highlights'] = serialize_highlights(article['highlights'])
    return article


def serialize_highlights(highlights):
    path_types = set([v.get('path') for v in highlights])
    return {path: max([v for v in highlights if v.get('path') == path], key=lambda x: x['score']) for path in path_types}


def get_article(article_id):
    return serialize(get_collection().find_one({
        'id': article_id
    }))


def list_articles_by_date(date, limit=20):
    cursor = get_collection().find({
        'date': {
            '$gte': datetime.combine(date, time.min),
            '$lt': datetime.combine(date, time.max),
        }
    }).limit(limit)
    return serialize_objects(cursor)


def search_articles_by_keyword(keyword, limit=20, offset=0, sort=None):
    post_search_pipelines = [
        {'$skip': offset, },
        {'$limit': limit}
    ]
    if sort:
        post_search_pipelines.insert(0, {'$sort': {'date': sort}})
    pipelines = [
        {
            '$search': {
                'index': 'default',
                'text': {
                    'query': keyword,
                    'path': ["headline", "body"],
                },
                "highlight": {
                    "path": ["headline", "body"]
                }
            },
        },
        {
            "$addFields": {
                "highlights": {"$meta": "searchHighlights"}
            }
        },
    ] + post_search_pipelines

    result = get_collection().aggregate(pipelines)
    results = serialize_objects(result)
    return results


def create_articles(records):
    return get_collection().insert_many(records, ordered=False)

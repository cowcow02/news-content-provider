from datetime import datetime

import pymongo
from flask import Flask, request, jsonify

import mongo
from exception_classes import BadRequest

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route("/articles", methods=['GET'])
def list_articles():
    limit = request.args.get('limit', 20)
    date = request.args.get('date')
    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        parsed_date = None
    if not parsed_date:
        raise BadRequest('Invalid date format, please use YYYY-mm-dd.')
    articles = mongo.list_articles_by_date(parsed_date)
    next_cursor = str(articles[-1]['_id']) if len(articles) == limit else None
    return jsonify({
        'pagination': {'next_cursor': next_cursor},
        'results': articles,
    })


@app.route("/articles/<article_id>", methods=['GET'])
def get_article(article_id):
    return jsonify(mongo.get_article(article_id))


@app.route("/articles/search", methods=['GET'])
def search():
    args = request.args
    keyword = args.get('q')
    limit = int(args.get('limit', 20))
    offset = int(args.get('offset', 0))
    sort = args.get('sort')
    if sort == 'latest':
        sort = pymongo.DESCENDING
    elif sort == 'oldest':
        sort = pymongo.ASCENDING
    else:
        sort = None
    articles = mongo.search_articles_by_keyword(keyword, limit, offset, sort)
    return jsonify({
        'metadata': {
            'q': keyword,
        },
        'pagination': {
            'limit': limit,
            'offset': offset,
        },
        'results': articles,
    })


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

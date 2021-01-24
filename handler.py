import json
import os
from datetime import date, timedelta
import calendar

from notion.block import TextBlock
from notion.client import NotionClient
from notion.collection import NotionDate

from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ.get('NOTION_TOKEN', "")
SECRET = os.environ.get('API_SECRET')
MONTH_PAGE = os.environ.get('MONTH_PAGE')
YEAR_PAGE = os.environ.get('YEAR_PAGE')
DAY_PAGE = os.environ.get('DAY_PAGE')
WEEK_PAGE = os.environ.get('WEEK_PAGE')

class Notion:
    def __init__(self, page_id):
        self.client = NotionClient(token_v2=NOTION_TOKEN)
        self.page = self.client.get_block(page_id)

    def add_row(self, title, content=None):
        collection = self.page.collection
        print(collection.parent.views)
        row = collection.add_row()
        row.name = title
        print(row)
        if content:
            row_content = row.children.add_new(
                TextBlock, title=content
            )
        return row

def in_between(start, end, d):
    return d >= start and d <= end

def find_in_between(page_id, d):
    n = Notion(page_id)
    rows = n.page.collection.get_rows()
    return (next(p for p in rows if in_between(p.dates.start, p.dates.end, d)))

def find_month(d):
    return find_in_between(MONTH_PAGE, d)

def find_year(d):
    return find_in_between(YEAR_PAGE, d)

def find_day(d):
    n = Notion(DAY_PAGE)
    rows = n.page.collection.get_rows()
    return next(p for p in rows if ( p.automatic_day and p.automatic_day.date() == d) or (p.manual_date and p.manual_date.start == d))

def first_and_last_days_of_month(d):
    year = d.year
    month = d.month
    days = calendar.monthrange(year, month)[1]
    first = date(year, month, 1)
    return first, (first + timedelta(days=days-1))


def notion_create(event, context):
    data = json.loads(event['body'])
    secret = data["secret"]
    if secret == SECRET:
        page_type = data["type"] or "add_row"
        page_id = data["page_id"]
        title = data["title"]
        content = data["content"]
        n = Notion(page_id)
        method_to_call = getattr(n, page_type)
        result = method_to_call(title, content)
        body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            "input": "Content created"
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    else:

        response = {
            "statusCode": 402,
            "body": "Not allowed"
        }

    return response

def create_day(event, context):
    page_id = DAY_PAGE
    today = date.today()
    title = F"{today:%d.%m.%Y}"
    print(title)
    n = Notion(page_id)
    result = n.add_row(title)
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": "Content created"
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

"""
needs to run on monday
"""
def create_week(event, context):
    page_id = WEEK_PAGE
    today = date.today()
    friday = today + timedelta(days=5)
    title = F"{today:%d.%m.} - {friday:%d.%m.%Y}"
    this_week = NotionDate(today, friday)
    month = find_month(today)
    print(title)
    n = Notion(page_id)
    result = n.add_row(title)
    result.dates = this_week
    result.month = month

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": "Content created"
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def create_month(event, context):
    page_id = MONTH_PAGE
    today = date.today()
    title = F"{today:%B}"
    first, last = first_and_last_days_of_month(today)
    this_week = NotionDate(first, last)
    year = find_year(today)
    print(title)
    n = Notion(page_id)
    result = n.add_row(title)
    result.dates = this_week
    result.year = year

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": "Content created"
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }


def create(data):
    secret = data.get("secret")
    if secret == SECRET:
        page_type = "add_row"
        page_id = data.get("page_id")
        title = data.get("title")
        content = data.get("content", "")
        n = Notion(page_id)
        result = n.add_row(title, content)
        return result

def notion_create_today(event, context):
    data = json.loads(event['body'])
    result = create(data)
    if result:
        day = find_day(date.today())
        if day:
            result.day = day

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": "Content created"
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def notion_create_with_props(event, context):
    data = json.loads(event['body'])
    result = create(data)
    if result:
        props = data.get('props', {})
        for key, value in props.items():
            result.set_property(key, value)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": "Content created"
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }


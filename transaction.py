import datetime


def create(content):
    return {
        'content': content,
        'date': int(datetime.datetime.now().timestamp() * 1000)
    }
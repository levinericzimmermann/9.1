import datetime

from mutwo import zimmermann_generators

DATE_TIME = datetime.datetime(2022, 10, 8)
TITLE = zimmermann_generators.get_title(DATE_TIME)

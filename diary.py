import sqlite3
import sys
from datetime import datetime
from datetime import date


DEFAULT_LOCATION = "Brno"

conn = sqlite3.connect('diary_entries.db',
                       detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()


class Page:

    def __init__(self, timestamp, location, letter):
        self.timestamp = timestamp
        if not location:
            self.location = location
        else:
            self.location = DEFAULT_LOCATION


class Diary:

    def __init__(self):

        create_page_table = '''CREATE TABLE IF NOT EXISTS PAGE (
            DATE      TIMESTAMP PRIMARY KEY NOT NULL,
            LOCATION  TEXT NOT NULL,
            LETTER    TEXT );'''

        cursor.execute(create_page_table)

        if not cursor.connection.total_changes:
            print("Diary found")
        else:
            print("Diary created successfully, changes: {}"
                  .format(cursor.connection.total_changes)
                  )

    def write_page(self, letter, timestamp=datetime.now(), location='Brno'):
        '''adds a page to the diary
        params:
            letter: the text body of the diary page
            timestamp: a timestamp, defaults to datetime.now()
            location: a city, text'''

        write_page = '''
            INSERT INTO PAGE (DATE,LOCATION,LETTER)
            VALUES (?, ?, ?)'''
        row = (timestamp, location, letter)
        cursor.execute(write_page, row)

        conn.commit()

    def read_all(self):
        '''reads all pages from a diary'''

        read_all_query = "SELECT DATE, LOCATION, LETTER FROM PAGE"
        cursor.execute(read_all_query)

        self.print_pages(cursor)

    def read_pages(self, date):
        '''reads all pages from a diary for a given day'''

        read_page_query = '''
            SELECT DATE, LOCATION, LETTER FROM PAGE
            WHERE ? < DATE AND DATE < ? '''

        day_start = datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=0, minute=0, second=0, microsecond=0
        )
        day_end = datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=23, minute=59, second=59, microsecond=999999
        )
        query_param = (day_start, day_end)
        try:
            cursor.execute(read_page_query, query_param)
        except sqlite3.ProgrammingError as err:
            print("reading error: {}".format(err), file=sys.stderr)
        except ValueError as err:
            print("date parsing error: {}".format(err), file=sys.stderr)
            print("date: {}".format(query_param))
            print("date type: {}".format(type(date)))
            print("query param type: {}".format(type(query_param)))

        results = cursor.fetchall()
        print("Found {} pages at date: {}".format(len(results), date))

        self.print_pages(results)

    def print_pages(self, cursor):
        '''prints diary pages to stdout
        params:
            cursor: the result of a query to the diary
        '''
        for row in cursor:
            print("*** date: {}".format(row[0])),
            print("\tplace: {}".format(row[1])),
            print("\tletter: {}".format(row[2])),


if __name__ == '__main__':
    print("Diary begins...")

    diary = Diary()

    diary.read_pages(date(2022, 4, 30))
    diary.read_all()
    conn.close()

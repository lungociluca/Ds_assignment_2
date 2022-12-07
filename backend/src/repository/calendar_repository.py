import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)


class CalendarRepository:
    db = None

    def __init__(self, db):
        self.db = db

    def get_days_of_month(self, year, month):
        print(f'In repository: { year }, {month}')
        query = "SELECT days_in_month FROM days where year = %d AND month = '%s'" % (year, month)
        db_result = self.db.engine.execute(query)
        for entry in db_result:
            print(entry)
            return entry[0]
        return None

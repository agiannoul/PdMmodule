import pickle
import sqlite3
import time
import codecs
import pandas

class SQLiteHandler:
    def __init__(self, db_name="NavarchosModels.db"):
        self.conn = sqlite3.connect(db_name)#,isolation_level = 'DEFERRED')
        self.cursor = self.conn.cursor()
        # self.cursor.execute('''PRAGMA synchronous = OFF''')
        # self.cursor.execute('''PRAGMA journal_mode = OFF''')
    def create_table(self):
        # Create a table with fields Date (datetime) and 3 text fields (target, modelpickle, Field3)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS my_table (
                Date INTEGER,
                source TEXT,
                modelpickle TEXT,
                PRIMARY KEY (source)
            )
        ''')
        self.conn.commit()
        self.create_index('source')

    def create_index(self, field_name):
        # Create an index on a specified field (e.g., target)
        self.cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{field_name} ON my_table({field_name})')
        self.conn.commit()

    def insert_record(self, date : pandas.Timestamp, target, modelpickle):
        unix_timestamp = int(time.mktime(date.timetuple()))
        tosave=self.create_pickle(modelpickle)
        self.cursor.execute('INSERT OR REPLACE INTO my_table (Date, source, modelpickle) VALUES (?, ?, ?)',
                                (unix_timestamp, str(target), tosave))
        self.conn.commit()


    def load_pickle(self,data_string):
        # Convert the string back to bytes
        dcccoded=codecs.decode(data_string.encode(), "base64")

        loaded_data = pickle.loads(dcccoded)

        return loaded_data

    def create_pickle(self,data):
        # Serialize the data to a bytes object
        data_bytes = codecs.encode(pickle.dumps(data), "base64").decode()

        # Convert the bytes to a string
        data_string = str(data_bytes)

        return data_string

    def get_record_source(self,value):
        # Retrieve records based on the indexed field (e.g., target)
        self.cursor.execute(f'SELECT * FROM my_table WHERE source = ?', (value,))
        records = self.cursor.fetchall()
        return records

    def get_model(self,source):
        # Retrieve records between the specified dates
        records = self.get_record_source(source)
        return_list = []
        for record in records:
            date, sourcei, model = record
            modeldict = self.load_pickle(model)
            return_list.append(modeldict)
        return return_list
    def close_connection(self):
        # Close the database connection
        self.conn.close()

# if __name__ == '__main__':
#     # Example usage
#     db_handler = SQLiteHandler('my_database.db')
#
#     # Create the table if it doesn't exist
#     db_handler.create_table()
#
#     # Create an index on a specified field (e.g., target)
#     db_handler.create_index('target')
#
#     # Insert a new record
#     db_handler.insert_record('2023-10-20', 'Value1', 'Value2', 'Value3')
#
#     # Retrieve records based on the indexed field (e.g., target)
#     records = db_handler.get_records_by_index('target', 'Value1')
#     for record in records:
#         print(record)
#
#     # Close the database connection when done
#     db_handler.close_connection()

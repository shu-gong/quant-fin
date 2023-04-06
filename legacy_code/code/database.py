#!/usr/local/bin/python3

# @Time    : 2021/1/22 14:00
# @Author  : Paul Ding
# @File    : database.py
# @Software: PyCharm

import pymysql

class mysql:
    def __init__(self, **kwargs):
        self.host = "localhost"
        self.port = 3306
        self.user = "root"
        self.password = "houjiacheng"
        self.charset = "UTF8MB4"
        self.database = "my_database"

        self.con = None
        self.cursor = None

        for key in kwargs:
            if key == 'host': self.host = kwargs[key]
            elif key == 'port': self.port = kwargs[key]
            elif key == 'user': self.user = kwargs[key]
            elif key == 'password': self.password = kwargs[key]
            elif key == 'charset': self.charset = kwargs[key]
            elif key == 'database': self.database = kwargs[key]
            else: print("Not used arguments: {} = {}".format(key, kwargs[key]))

        self.connect()

    def connect(self):
        host = self.host
        port = self.port
        user = self.user
        password = self.password
        charset = self.charset

        print("host = ", host)
        print("port = ", port)
        print("user = ", user)
        print("password = ", password)
        print("charset = ", charset)

        con = pymysql.connect(host = host, port = port,
                             user = user, password = password, charset = charset)
        cursor = con.cursor()

        self.con = con
        self.cursor = cursor

    def close(self):
        con = self.con
        if con : con.close()

    def create_database(self, database):
        con = self.con
        cursor = self.cursor

        if (con or cursor or database) is None: return
        try:
            sql = "CREATE DATABASE IF NOT EXISTS {}".format(database)
            cursor.execute(sql)
            return
        except pymysql.Error as err:
            print(err)


    def create_table(self, database, table, table_columns, primary_key):
        '''
        CREATE TABLE IF NOT EXISTS gold2102 (
            DateTime datetime,
            Open float(10,4),
            High float(10,4),
            Low float(10,4),
            Close float(10,4),
            TradeVolume BIGINT,
            HoldVolume BIGINT,
            Average float(10,4),
            PRIMARY KEY(DateTime)) ENGINE=innodb DEFAULT CHARSET=UTF8MB4;
        '''
        con = self.con
        cursor = self.cursor
        if (con or cursor or database or table) is None: return

        try:
            sql_statement = "use " + database
            cursor.execute(sql_statement)

            # OHLC: Open, High, Low, Close
            sql_statement = "CREATE TABLE IF NOT EXISTS {} (\n".format(table)
            for key, value in table_columns.items():
                sql_statement += "    {} {}, \n".format(key, value)
            sql_statement += "    PRIMARY KEY ({})) ENGINE=innodb DEFAULT CHARSET=UTF8MB4;".format(primary_key)
            print(sql_statement)
            cursor.execute(sql_statement)
        except pymysql.Error as err:
            print(err)

    def drop_database(self, database):
        con = self.con
        cursor = self.cursor
        if (con or cursor or database) is None: return

        sql = "DROP DATABASE IF EXISTS " + database
        cursor.execute(sql)

    def drop_table(self, database, table):
        con = self.con
        cursor = self.cursor
        if (con or cursor or database or table) is None: return

        sql = "use " + database
        cursor.execute(sql)
        sql = "DROP TABLE IF EXISTS " + table
        cursor.execute(sql)

    def insert_item(self, database, table, values):
        con = self.con
        cursor = self.cursor
        if (con or cursor or database or table or values) is None: return

        sql = "use " + database
        cursor.execute(sql)

        sql = """INSERT INTO {}
            VALUES{} """.format(table, values)
        try:
            print(sql)
            cursor.execute(sql)
            con.commit()
        except pymysql.Error as err:
            print(err)

    def insert_items(self, database, table, values_list):
        con = self.con
        cursor = self.cursor
        if (con or cursor or database or table or values_list) is None: return

        sql = "use " + database
        cursor.execute(sql)

        batch_rows = 10000
        inserted_rows = 0
        rest_rows = len(values_list)
        while rest_rows > 0:
            rows = batch_rows if rest_rows > batch_rows else rest_rows
            print("rows", rows)
            print("{} items will be inserted into table {}".format(rows, table))
            sql = """INSERT INTO {} VALUES """.format(table)
            idx = 0
            for values in values_list[inserted_rows : inserted_rows+rows]:
                if idx == 0:
                    comma = ''
                else:
                    comma = ','
                sql += "{} {}".format(comma, values)
                idx += 1
            # print(sql)
            try:
                pass
                cursor.execute(sql)
                con.commit()
            except pymysql.Error as err:
                print(err)
            inserted_rows += rows
            rest_rows -= rows

    def show_tables(self, database):
        con = self.con
        cursor = self.cursor
        if (con or cursor or database) is None: return

        sql = "use " + database
        cursor.execute(sql)
        sql = "show tables"
        cursor.execute(sql)
        tables = list(cursor.fetchall())
        print("%d table(s) found: %s" % (len(tables), tables))
        idx = 0
        for table in tables:
            print("Tables[%d] :" % idx, "%s" % table)
            idx += 1
        print()
        return tables

    def show_databases(self):
        con = self.con
        cursor = self.cursor
        if (con or cursor) is None: return

        sql = "show databases"
        cursor.execute(sql)
        databases = list(cursor.fetchall())
        print("%d databases found: %s" %(len(databases),databases))
        idx = 0
        for database in databases:
            print("Database[%d] :" % idx, "%s" % database)
            idx += 1
        print()

        return databases

    def date(self):
        con = self.con
        cursor = self.cursor
        if (con or cursor) is None: return

        sql = 'SET @dt = NOW()'
        cursor.execute(sql)
        sql = 'SELECT DATE(@dt)'
        cursor.execute(sql)

        return cursor.fetchone()

    def time(self):
        con = self.con
        cursor = self.cursor
        if (con or cursor) is None: return

        sql = 'SET @dt = NOW()'
        cursor.execute(sql)
        sql = 'SELECT TIME(@dt)'
        cursor.execute(sql)
        return cursor.fetchone()

    def version(self):
        con = self.con
        cursor = self.cursor
        if (con or cursor) is None: return

        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()

        return version

    def create_futures(self,database, table):
        if (database or table) is None: return

        values_list = [
            ("2020/12/23 02:27", 391.8600, 391.8600, 391.7000, 391.7000, 59.0000, 50041.0000, 391.8169),
            ("2020/12/23 02:28", 391.7000, 391.9200, 391.6800, 391.8400, 75.0000, 50000.0000, 391.8222),
        ]

        table_columns = {'DateTime': 'datetime',
                         'Open': 'DECIMAL(10,4)',
                         'High': 'DECIMAL(10,4)',
                         'Low': 'DECIMAL(10,4)',
                         'Close': 'DECIMAL(10,4)',
                         'TradeVolume': 'BIGINT',
                         'HoldVolume': 'BIGINT',
                         'Average': 'DECIMAL(10,4)',
                         'MA5': 'DECIMAL(10,4)',
                         }
        primary_key = 'DateTime'

        print("database: {}".format(database))
        print("table: {}".format(table))

        db.drop_database(database)
        db.create_database(database)
        db.show_databases()
        db.create_table(database, table, table_columns, primary_key)
        db.show_tables(database)

        # db.insert_items(database, table, values_list)
        db.close()

if __name__ == "__main__":
    db = mysql(host="localhost", user="root", password="houjiacheng")
    db.create_futures(database = "futures", table = "gold2021")

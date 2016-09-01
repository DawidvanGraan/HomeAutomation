#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import subprocess
import time
import json
import os
from datetime import datetime

class WhosHome:
    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.con = None
        self.getConnection(self.dbPath)

    def init(self, users):
        # Insert initial status (offline) into the database
        rows = self.query("SELECT * FROM whoshome limit 1")
        if rows is None or len(rows) == 0:
            cursor = self.con.cursor()
            for user in users:
                cursor.execute("""INSERT INTO whoshome(name, status, updated) VALUES(?, ?, ?)""", (user["name"], 0, 0))
            self.con.commit()

    def getConnection(self, dbPath):
        try:
            self.con = sqlite3.connect(dbPath)

            # Create the database
            cursor = self.con.cursor()
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS whoshome(
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                                name TEXT,
                                status INTEGER,
                                updated DATETIME)
                        """)
            self.con.commit()

            print "connection created"
        except sqlite3.Error, e:
            print "getConnection Error %s:" % e.args[0]
            # sys.exit(1)

    def query(self, sql):

        # print sql
        rows = []
        try:
            # with self.con:
            cur = self.con.cursor()
            cur.execute(sql)

            rows = [dict((cur.description[i][0], value) \
                         for i, value in enumerate(row)) for row in cur.fetchall()]
        except sqlite3.Error, e:
            print "Query Error %s:" % e.args[0]
            # sys.exit(1)
        return rows

    def find(self, name):
        return self.query("select name, status, updated from whoshome where name = '" + name + "'")

    def getUsers(self):
        return self.query("select name, status, updated from whoshome")

    def ping(self, ip):
        output = subprocess.Popen(["ping", "-c", "1", ip], stdout=subprocess.PIPE, shell=False)
        check = output.communicate()[0]
        check = output.returncode
        return check

    def checkIfHome(self, name, ip):
        check = self.ping(ip)
        today = datetime.today()
        now = today.strftime('%H:%M')

        status = 0  # OFFLINE
        if check == 0:
            status = 1  # ONLINE

        cursor = self.con.cursor()
        cursor.execute("""UPDATE whoshome SET status = ?, updated = ? WHERE name = ?;""", (status, now, name))
        self.con.commit()


def readConfig():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, 'config.json')) as json_data_file:
        return json.load(json_data_file)


def main():
    whoshome = None

    try:
        # Read the config
        config = readConfig()

        whoshome = WhosHome(config["database"]["file"])
        whoshome.init(config["users"])

        # Loop it
        while True:
            for user in config["users"]:
                whoshome.checkIfHome(user["name"], user["ip"])
            time.sleep(60)

    except KeyboardInterrupt:
        if whoshome is not None:
            whoshome.con.close()

        print "Exit"


if __name__ == "__main__":
    main()

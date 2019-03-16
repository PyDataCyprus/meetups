#-*- coding: utf-8 -*-
import argparse
import sys
import logging
import random
import time

import sqlite3

random.seed(time.time())

NAMES = ["Giorgos", "Ioannis", "Argyris", "Vassilis", "Minas", "Maria",
         "Eleni", "Konstantina", "Manolis", "Andri", "Mark", "Benn", "Hassan",
         "Katerina", "Jorge", "Petros", "Eliza", "Andreas", "Nestoras",
         "Iraklis", "Mihalis"]

TECHS = ["c", "sql", "golang", "python", "php", "c++", "rust", "swift",
        "linux", "ruby", "java"]

CITIES = ["Athens", "Patras", "Chania", "Thessaloniki", "Nicossia", "Paphos",
          "Larnaca", "Limassol", "Berlin", "San Fransisco"]


class Participant(object):

    __slots__ = ('pid', 'name', 'city', 'techs')

    def __init__(self, pid, name, city, techs):
        """
        :param int pid: The participant id
        :param string name: The participant's name
        :param string city: The participant's city
        :param list techs: The participants technology stack
        """
        self.pid = pid
        self.name = name
        self.city = city
        self.techs = techs[:]

    def __str__(self):
        return "{} {} {} {}".format(self.pid, self.name, self.city,
                ','.join(self.techs))

    @classmethod
    def get_random(cls):
        name = random.choice(NAMES)
        city = random.choice(CITIES)
        n = random.randint(0, len(TECHS))
        techs = []
        if n > 0:
            seen = set()
            while len(techs) < n:
                t = random.choice(TECHS)
                if t not in seen:
                    seen.add(t)
                    techs.append(t)
        return cls(-1, name, city, techs)


def create_tables(conn):
    cursor = conn.cursor()
    t1 = '''
    CREATE TABLE IF NOT EXISTS participants(id INTEGER PRIMARY KEY, name TEXT, city TEXT);
    '''
    t2 = '''
    CREATE TABLE IF NOT EXISTS part_techs
    (pid INTEGER, tech TEXT,
    CONSTRAINT fk_participants
    FOREIGN KEY (pid) REFERENCES participants(id)
    );'''
    cursor.execute(t1)
    cursor.execute(t2)
    conn.commit()


def insert_participant(cursor, participant):
    q1 = 'INSERT INTO participants(name, city) VALUES(?, ?)'
    cursor.execute(q1, (participant.name, participant.city))
    if len(participant.techs) > 0:
        cursor.execute('select last_insert_rowid()')
        row = cursor.fetchone()
        q2 = 'INSERT INTO part_techs(pid, tech) VALUES(?, ?)'
        params = [(row[0], t) for t in participant.techs]
        cursor.executemany(q2, params)


def create_random(num):
    participants = []
    for i in range(0, num):
        p = Participant.get_random()
        participants.append(p)
        print(p)
    return participants


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='participants.db')
    parser.add_argument('--num', type=int, default=10000)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    conn = sqlite3.connect(args.db)
    create_tables(conn)
    cursor = conn.cursor()
    for p in create_random(args.num):
        insert_participant(cursor, p)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()



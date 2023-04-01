
# Your name: Sam Gibson
# Your student id: 42836823
# Your email: samcg@umich.edu
# List who you have worked with on this project:

import unittest
import sqlite3
import json
import os

def read_data(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path)
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def make_positions_table(data, cur, conn):
    positions = []
    for player in data['squad']:
        position = player['position']
        if position not in positions:
            positions.append(position)
    cur.execute("CREATE TABLE IF NOT EXISTS Positions (id INTEGER PRIMARY KEY, position TEXT UNIQUE)")
    for i in range(len(positions)):
        cur.execute("INSERT OR IGNORE INTO Positions (id, position) VALUES (?,?)",(i, positions[i]))
    conn.commit()

def make_players_table(data, cur, conn):
    position_list = []
    cur.execute("CREATE TABLE IF NOT EXISTS Players (id INTEGER PRIMARY KEY, name TEXT, position_id INTEGER, birthyear INTEGER, nationality TEXT)")
    for player in data['squad']:
        position_list.append(player['position'])
    for i in range(len(position_list)):
        if position_list[i] == 'Goalkeeper':
            position_list[i] = 0
        elif position_list[i] == 'Defence':
            position_list[i] = 1
        elif position_list[i] == 'Midfield':
            position_list[i] = 2
        elif position_list[i] == 'Offence':
            position_list[i] = 3
        elif position_list[i] == 'Forward':
            position_list[i] = 4
    
    c = 0
    for player in data['squad']:
        cur.execute("INSERT OR IGNORE INTO Players (id, name, position_id, birthyear, nationality) VALUES (?,?,?,?,?)", (player['id'], player['name'], position_list[c], player['dateOfBirth'].split('-')[0], player['nationality']))
        c +=1
    conn.commit()

def nationality_search(countries, cur, conn):
    ptup_list = []
    for country in countries:
        cur.execute(f'SELECT * FROM Players WHERE nationality = "{country}"')
        for row in cur:
            ptup = (row[1], row[2], row[4])
            ptup_list.append(ptup)

    return ptup_list

def birthyear_nationality_search(age, country, cur, conn):
    ptup2_list = []
    cur.execute(f'SELECT * FROM Players WHERE nationality="{country}" AND birthyear<"{2023-age}"')
    for row in cur:
        ptup2 = (row[1], row[4], row[3])
        ptup2_list.append(ptup2)

    return ptup2_list

def position_birth_search(position, age, cur, conn):
    ptup3_list = []
    cur.execute(f"SELECT name, position, birthyear FROM Positions JOIN Players ON Positions.id = Players.position_id WHERE Positions.position = '{position}' AND birthyear>'{2023-age}'")
    for row in cur:
        ptup3_list.append(row)

    return ptup3_list

#EXTRA CREDIT
def make_winners_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Winners (id INTEGER PRIMARY KEY, name TEXT)")
    for season in data['seasons']:
        if season['winner'] != None:
            cur.execute("INSERT OR IGNORE INTO Winners (id, name) VALUES (?,?)", (season['id'], season['winner']['name']))
    conn.commit()

def make_seasons_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Seasons (id INTEGER PRIMARY KEY, winner_id TEXT, end_year INT)")
    for season in data['seasons']:
        if season['winner'] != None:
            cur.execute("INSERT OR IGNORE INTO Seasons (id, winner_id, end_year) VALUES (?,?,?)", (season['id'], season['winner']['id'], season['endDate'].split('-')[0]))

    conn.commit()

def winners_since_search(year, cur, conn):
    pass


class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'Football.db')
        self.cur = self.conn.cursor()
        self.conn2 = sqlite3.connect(path+'/'+'Football_seasons.db')
        self.cur2 = self.conn2.cursor()

    def test_players_table(self):
        self.cur.execute('SELECT * from Players')
        players_list = self.cur.fetchall()

        self.assertEqual(len(players_list), 30)
        self.assertEqual(len(players_list[0]),5)
        self.assertIs(type(players_list[0][0]), int)
        self.assertIs(type(players_list[0][1]), str)
        self.assertIs(type(players_list[0][2]), int)
        self.assertIs(type(players_list[0][3]), int)
        self.assertIs(type(players_list[0][4]), str)

    def test_nationality_search(self):
        x = sorted(nationality_search(['England'], self.cur, self.conn))
        self.assertEqual(len(x), 11)
        self.assertEqual(len(x[0]), 3)
        self.assertEqual(x[0][0], "Aaron Wan-Bissaka")

        y = sorted(nationality_search(['Brazil'], self.cur, self.conn))
        self.assertEqual(len(y), 3)
        self.assertEqual(y[2],('Fred', 2, 'Brazil'))
        self.assertEqual(y[0][1], 3)

    def test_birthyear_nationality_search(self):

        a = birthyear_nationality_search(24, 'England', self.cur, self.conn)
        self.assertEqual(len(a), 7)
        self.assertEqual(a[0][1], 'England')
        self.assertEqual(a[3][2], 1992)
        self.assertEqual(len(a[1]), 3)

    def test_type_speed_defense_search(self):
        b = sorted(position_birth_search('Goalkeeper', 35, self.cur, self.conn))
        self.assertEqual(len(b), 2)
        self.assertEqual(type(b[0][0]), str)
        self.assertEqual(type(b[1][1]), str)
        self.assertEqual(len(b[1]), 3) 
        self.assertEqual(b[1], ('Jack Butland', 'Goalkeeper', 1993)) 

        c = sorted(position_birth_search("Defence", 23, self.cur, self.conn))
        self.assertEqual(len(c), 1)
        self.assertEqual(c, [('Teden Mengi', 'Defence', 2002)])
    
    # # test extra credit
    def test_make_winners_table(self):
        self.cur2.execute('SELECT * from Winners')
        winners_list = self.cur2.fetchall()
        self.assertEqual(len(winners_list), 28)
        self.assertEqual(type(winners_list[0]), tuple)
        self.assertEqual(type(winners_list[0][0]), int)
        self.assertEqual(type(winners_list[0][1]), str)
        self.assertEqual(winners_list[1][1], 'Manchester City FC')
        self.assertEqual(winners_list[-1][0], 619)

    def test_make_seasons_table(self):
        self.cur2.execute('SELECT * from Seasons')
        seasons_list = self.cur2.fetchall()
        self.assertEqual(len(seasons_list), 28)
        self.assertEqual(type(seasons_list[0]), tuple)
        self.assertEqual(type(seasons_list[0][0]), int)
        self.assertEqual(type(seasons_list[0][1]), str)
        self.assertEqual(type(seasons_list[0][2]), int)
        self.assertEqual(seasons_list[1][1], '65')
        self.assertEqual(seasons_list[-1][0], 619)


    # def test_winners_since_search(self):

    #     pass


def main():

    #### FEEL FREE TO USE THIS SPACE TO TEST OUT YOUR FUNCTIONS

    json_data = read_data('football.json')
    cur, conn = open_database('Football.db')
    make_positions_table(json_data, cur, conn) 
    make_players_table(json_data, cur, conn)
    conn.close()


    seasons_json_data = read_data('football_PL.json')
    cur2, conn2 = open_database('Football_seasons.db')
    make_winners_table(seasons_json_data, cur2, conn2)
    make_seasons_table(seasons_json_data, cur2, conn2)
    conn2.close()


if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)

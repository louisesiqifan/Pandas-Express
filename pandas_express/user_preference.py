import sqlite3
import os
import re
import configparser
import manage_user

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']


def find(c, tbl, id, user):
    s = '''
    SELECT * FROM {}
    WHERE id = ? AND user = ?
    '''.format(tbl)
    c.execute(s, (id, user))
    result = c.fetchall()
    if len(result) > 0:
        return True
    return False


def save(tbl, id, user):
    '''
    Save result to table
    Input:
        tbl(str): user_fav or user_least_fav
        id(int): food id
        user(str): user name
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    user_exist = manage_user.find(c, user)
    if not user_exist:
        db.close()
        return 'User does not exist'
    exist = find(c, tbl, id, user)
    if exist:
        db.close()
        return 'Dish already Saved :)'
    s = '''
    INSERT INTO {} (id, user)
    VALUES (?, ?)
    '''.format(tbl)
    c.execute(s, (id, user))
    db.commit()
    db.close()
    return 'Save Success!'

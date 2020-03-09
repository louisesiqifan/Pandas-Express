import sqlite3
import os
import re
import configparser

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
SQL_CREATE_USER = config['USER']['SQL_CREATE_USER']
SQL_CREATE_FAV = config['USER']['SQL_CREATE_FAV']
SQL_CREATE_LEAST_FAV = config['USER']['SQL_CREATE_LEAST_FAV']
SQL_CREATE_CURRENT_USER = config['USER']['SQL_CREATE_CURRENT_USER']
SQL_CREATE_CURRENT_DISH = config['USER']['SQL_CREATE_CURRENT_DISH']


def create_table(sql_query):
    '''
    Create Table
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    c.execute(sql_query)
    db.commit()
    db.close()


def create_tables():
    create_table(SQL_CREATE_CURRENT_USER)
    create_table(SQL_CREATE_USER)
    create_table(SQL_CREATE_FAV)
    create_table(SQL_CREATE_LEAST_FAV)
    create_table(SQL_CREATE_CURRENT_DISH)


def find_user(user):
    s = '''
    SELECT * FROM user
    WHERE name = ?
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    c.execute(s, (user,))
    result = c.fetchall()
    db.close()
    if len(result) > 0:
        return True
    return False


def save_current_dish(id):
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    s = '''
    DELETE FROM current_dish;
    '''
    c.execute(s)
    db.commit()
    s = '''
    INSERT INTO current_dish (name)
    VALUES (?)
    '''
    c.execute(s, (id,))
    db.commit()
    db.close()


def save_current_user(name):
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    s = '''
    DELETE FROM current_user;
    '''
    c.execute(s)
    db.commit()
    s = '''
    INSERT INTO current_user (name)
    VALUES (?)
    '''
    c.execute(s, (name,))
    db.commit()
    db.close()


def create_new_user(name):
    '''
    Create new user if not already exists
    '''
    create_tables()
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    s = '''
    INSERT INTO user (name)
    VALUES (?)
    '''
    c.execute(s, (name,))
    db.commit()
    db.close()
    return 'User Created!'


def delete_user(name):
    '''
    Delete user from database
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    for tbl in ['user', 'user_fav', 'user_least_fav']:
        if tbl == 'user':
            col = 'name'
        else:
            col = 'user'
        s = '''
            DELETE from {} WHERE {} = ?;
            '''.format(tbl, col)
        c.execute(s, (name,))
        db.commit()
    db.close()
    return 'Successfully deleted user from database'

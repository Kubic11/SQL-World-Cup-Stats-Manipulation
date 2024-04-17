import logging
import sqlite3
import re

global DB, DB_FILE

# TODO change this to your database file
DB_FILE = 'projetobd.db'

DB = dict()

def connect():
  global DB, DB_FILE
  c = sqlite3.connect(DB_FILE, check_same_thread=False)
  print("connected", c)
  c.row_factory = sqlite3.Row
  DB['conn'] = c
  DB['cursor'] = c.cursor()
  logging.info('Connected to database')

def execute(sql,args=None):
  global DB
  sql = re.sub('\s+',' ', sql)
  logging.info('SQL: {} Args: {}'.format(sql,args))
  return DB['cursor'].execute(sql, args) \
      if args != None else DB['cursor'].execute(sql)

def close():
  global DB
  DB['conn'].close()
# from string import ascii_letters
#
# print(len(ascii_letters))

import psycopg2
from pswd import user, password

# import logging

# # Creating logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)
# foramtter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
# file_handler = logging.FileHandler('rest_service.log')
# file_handler.setFormatter(foramtter)
# logger.addHandler(file_handler)


# class MyError(Exception):
#     def __repr__(self):
#         raise MyError(" Postgis extension might already be installed")


# connection db
# def connection_db():
#     conn = psycopg2.connect(
#         database="rest_DB",
#         user=user,
#         password=password,
#         host="127.0.0.1",
#         port="5432"
#     )
#     return conn
#
#
# def table_crt(con):
#     cur = con.cursor()
#     sql_check = "select exists(select * from information_schema.tables where table_name=%s)"
#     cur.execute(sql_check, ('rest_users',))
#     if not cur.fetchone()[0]:
#         # sql_postgis = 'create extension postgis;'
#         # try:
#         # cur.execute(sql_postgis)
#         # except:
#         # MyError(Exception):
#         # logger.info(f'Postgis extension might be already installed {MyError}')
#
#         sql_table = '''create table rest_users (
#                                     id      	serial,
#                                     name    	varchar(10),
#                                     longitude 	real,
#                                     latitude 	real);'''
#         #sql_drop = 'drop table rest_users;'
#         cur.execute(sql_table)
#     # cur.execute(sql_drop)
#
#         conn.commit()
#     else:
#         print('hello')


# def table_ins(con):
#     cur = con.cursor()
#     test_ins = '''INSERT INTO rest_users (id ,name, longitude, latitude)
#                                         VALUES(default, %s, %s, %s)'''
#     cur.execute(test_ins, ('1', 10.1, 10.132))
#     cur.execute(test_ins, ('2', 10.1, 10.122))
#     cur.execute(test_ins, ('3', 10.1, 10.123))
#
#     sql_update = '''alter table rest_users add
#                         column geolocation geography(point);'''
#
#     sql_make_point = '''update rest_users set
#                             geolocation =ST_MakePoint(longitude, latitude); '''
#
#     sql_near = '''
#         select name, ST_Distance(ru.geolocation,
#                                                 first_user.geolocation) distance
#         from rest_users ru,lateral(
#                             select id, geolocation
#                             from rest_users
#                             where name = '1') as first_user
#         where ru.id != first_user.id
#         and ST_Distance(ru.geolocation, first_user.geolocation)<1500
#         order by distance;'''
#
#     cur.execute(sql_update)
#     cur.execute(sql_make_point)
#     cur.execute(sql_near)
#     print(cur.fetchall())
#     conn.commit()
#     return conn
#
#
# def get_all(con):
#     cur = conn.cursor()
#     sql = 'Select * from rest_users;'
#     cur.execute(sql)
#     print(cur.fetchall())
#     cur.close()
#
#
# def drop_table(conn):
#     cur = conn.cursor()
#     sql_drop = 'drop table rest_users'
#     cur.execute(sql_drop)
#     conn.commit()
#     conn.close()


# conn = connection_db()
# table_crt(conn)
# print(table_ins(conn))
# print(get_all(conn))
# drop_table(conn)


# cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('mytable',))
# cur.fetchone()[0]


# import collections
#
# defdict = collections.defaultdict(list)
# print(defdict)
# for i in range(5):
#     defdict[i] = [i]
# print(defdict)

import sys
a = [10, 120, 303030]

b = {}
m = b.fromkeys(a, 0)
with open('tests.txt', 'w') as test:
    sys.stdout

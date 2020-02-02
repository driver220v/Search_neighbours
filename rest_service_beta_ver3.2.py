# Напишите REST-сервис для поиска соседей. Основная функция - сервис должен позволить запросить
# K ближайших соседей пользователя N в радиусе M километров.
# Помимо этого сервис должен позволять выполнять простейшие CRUD-действия над пользователями
# - создавать пользователя с координатами (2D, на плоскости, сфере или геоиде - не суть),
# модифицировать информацию о нём
# (координаты, какое-нибудь описание, по желанию), удалять. У вас десять миллионов пользователей и один вечер.


# Напишите простой сервис для поиска соседей. У сервиса должно быть две ручки:

# Добавить человека (имя, координата x, координата y)
# По координатам (x, y) вывести имена ближайших N (N < 100) людей
# Имена и координаты могут повторяться. Интерфейс не обязателен, достаточно REST API.


# Notes(Nik)

import json
import psycopg2.extensions
import psycopg2.errors
from pswd import user, password, database  # file with confidential information
from flask import Flask
from flask import request

# file with confidential data

app = Flask(__name__)


# SQL METHODS

def connection_db():  # SQL
    conn = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host="127.0.0.1",
        port="5432")
    return conn


con = connection_db()


def del_all_sql():  # SQL
    cur = con.cursor()
    # check if the table exist
    sql_check = """select exists(select *
                                     from information_schema.tables 
                                      where table_name = 'rest_users');"""
    sql_drop = 'drop table rest_users;'
    cur.execute(sql_check)
    if cur.fetchone()[0]:
        cur.execute(sql_drop)
        con.commit()
        cur.execute(sql_check)
        return json.dumps(cur.fetchone()[0])
    else:
        cur.execute(sql_drop)
        con.commit()
        cur.execute(sql_check)
        return json.dumps(cur.fetchone()[0])


def del_one_sql(name_srch, long,
                lat):  # SQL #todo smt wrong when passing longitude, latitude deletion doesnt work correctly
    cur = con.cursor()
    sql_del = f"""delete from rest_users
                  where name=%s;"""  # and longitude=%s and latitude=%s;"""

    cur.execute(sql_del, (name_srch,))
    con.commit()
    return name_srch, long, lat


def insert_table_sql(name, long, lat):  # SQL
    cur = con.cursor()
    test_ins = '''INSERT INTO rest_users (id ,name, longitude, latitude)
                                            VALUES(default, %s, %s, %s)'''

    cur.execute(test_ins, (name, long, lat))
    con.commit()
    sql_repr = ('''select name 
                    from rest_users
                    where latitude=%s
                    and longitude=%s;''')
    cur.execute(sql_repr, (lat, long))

    sql_to_return = '''select name, longitude, latitude
                    from rest_users
                    where name=%s
                    and latitude=%s
                    and longitude=%s'''
    cur.execute(sql_to_return, (name, lat, long))
    return cur.fetchone()


def neighbours_sql(name_srch, radius):  # SQL
    cur = con.cursor()
    sql_make_point = '''update rest_users set 
                                        geolocation =ST_MakePoint(longitude, latitude); '''

    sql_search = f"""select name, ST_Distance(ru.geolocation, first_user.geolocation) distance
                                    from rest_users ru, lateral( 
                                                                select id, geolocation
                                                                from rest_users 
                                                                where name=%s) as first_user
                                    where ru.id != first_user.id
                                    and ST_Distance(ru.geolocation, first_user.geolocation)<%s
                                    order by distance;"""
    cur.execute(sql_make_point)
    con.commit()
    cur.execute(sql_search, (name_srch, radius))
    con.commit()
    return cur.fetchall()


def select_all_sql():  # SQL
    cur = con.cursor()
    # Check the existence users' table
    sql_select = '''select to_json(t)
                    from 
                        (select name, longitude, latitude 
                          from rest_users) t;'''

    sql_check = """select exists(select * 
                                    from information_schema.tables 
                                    where table_name=%s)"""

    cur.execute(sql_check, ('rest_users',))
    if not cur.fetchone()[0]:
        table_crt_sql()
        cur.execute(sql_select)
        return cur.fetchall()
    else:
        cur.execute(sql_select)
        return cur.fetchall()


def update_coords_sql(name_srch, long, lat):
    cur = con.cursor()
    sql_select = f'''select to_json(t)
                    from 
                        (select name, longitude, latitude 
                          from rest_users
                          where name=%s and longitude=%s and latitude=%s ) t;'''

    sql_update = f"""update rest_users
                     set longitude=%s,latitude=%s
                     where name=%s;"""

    cur.execute(sql_update, (long, lat, name_srch))
    con.commit()
    cur.execute(sql_select, (name_srch, long, lat))
    return cur.fetchall()


def table_crt_sql():  # SQL
    # check if postgis is installed, else install it
    cur = con.cursor()

    sql_postgis_check = """select * from pg_extension 
                    where extname=%s;"""

    cur.execute(sql_postgis_check, ('postgis',))

    sql_table = '''create table rest_users (
                                            id      	serial,
                                            name    	varchar(10),
                                            longitude 	real,
                                            latitude 	real,
                                            geolocation geography(point, 4326));'''
    if not cur.fetchone()[0]:
        pg_install = """create extension postgis; """
        cur.execute(pg_install)
        cur.execute(sql_table)
        con.commit()
    else:
        cur.execute(sql_table)
        con.commit()


# Hub-methods
@app.route('/person',
           methods=['PUT',
                    'POST',
                    'DELETE']
           )  # CRUD actions
def person_actions():
    person_name = str(request.args.get('name'))
    coord_long = float(request.args.get('longitude'))
    coord_lat = float(request.args.get('latitude'))

    if request.method == 'POST':  # Create
        person = insert_table_sql(person_name, coord_long, coord_lat)
        return json.dumps(person)
    elif request.method == 'PUT':  # Update
        new_position = update_coords_sql(person_name, coord_long, coord_lat)
        return json.dumps(new_position)
        pass
    elif request.method == 'DELETE':  # Delete
        del_one = del_one_sql(person_name, coord_long, coord_lat)
        return json.dumps(del_one)


@app.route('/persons', methods=['GET'])  # CRUD action (read)
def show_data():
    return json.dumps(select_all_sql())  # conversion, read


@app.route('/persons_near',
           methods=['GET'])
def search_near():
    name = (request.args.get('name'))
    distance = int(request.args.get('distance'))
    res = neighbours_sql(name, distance)
    return json.dumps(res)


@app.route('/persons', methods=['DELETE'])  # DELETE WHOLE TABLE
def delete_all():
    res = del_all_sql()
    return json.dumps(res)


if __name__ == '__main__':
    # app.debug = 1
    app.run()

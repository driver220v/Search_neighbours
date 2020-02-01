
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


pers_info = {}
con = connection_db()


# todo LOOK HERE DELETE NOT ONLY DB BUT DICT PERS_INFO
def del_all_sql():  # SQL
    cur = con.cursor()
    pers_info.clear()
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
        return json.dumps(cur.fetchone())
    else:
        cur.execute(sql_drop)
        con.commit()
        cur.execute(sql_check)
        return json.dumps(cur.fetchone())


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


def neighbours_sql(name_srch, distance):  # SQL
    every = []
    cur = con.cursor()
    # CHECK EXISTENCE OF GEOLOCATION COLUMN
    sql_check = """select exists(select *
                                 from information_schema.columns 
                                 where table_name = 'rest_users' and column_name = 'geolocation');"""

    sql_update = '''alter table rest_users add 
                                                    column geolocation geography(point);'''
    sql_make_point = '''update rest_users set 
                                        geolocation =ST_MakePoint(longitude, latitude); '''

    sql_search = f"""select name, ST_Distance(ru.geolocation, first_user.geolocation) distance
                                    from rest_users ru, lateral( 
                                                                select id, geolocation
                                                                from rest_users 
                                                                where name = '{name_srch}') as first_user
                                    where ru.id != first_user.id
                                    and ST_Distance(ru.geolocation, first_user.geolocation)<{distance}
                                    order by distance;"""
    cur.execute(sql_check)
    if not cur.fetchone()[0]:
        cur.execute(sql_update)
        cur.execute(sql_make_point)

        cur.execute(sql_search)
        every.append(cur.fetchall())
        con.commit()
    else:
        cur.execute(sql_search)
        every.append(cur.fetchall())
        con.commit()
    return every


def select_all_sql():  # SQL
    cur = con.cursor()
    # Check the existence users' table
    sql_select = 'Select * from rest_users;'
    sql_check = """select exists(select * from information_schema.tables 
                    where table_name=%s)"""

    cur.execute(sql_check, ('rest_users',))
    if not cur.fetchone()[0]:
        table_crt_sql()
        cur.execute(sql_select)
        fl = cur.fetchall()
        return fl
    else:
        cur.execute(sql_select)
        fl = cur.fetchall()
        return fl


def update_coords_sql(name_srch, long, lat):
    cur = con.cursor()
    sql_select = 'Select * from rest_users;'
    sql_update = f"""update rest_users
                     set longitude={long},latitude={lat}
                     where name='{name_srch}';"""
    cur.execute(sql_update)
    con.commit()
    cur.execute(sql_select)
    return cur.fetchall()


def table_crt_sql():  # SQL - todo done
    # check if postgis is installed, else install it
    cur = con.cursor()

    sql_postgis_check = """select * from pg_extension 
                    where extname=%s;"""

    cur.execute(sql_postgis_check, ('postgis',))

    sql_table = '''create table rest_users (
                                            id      	serial,
                                            name    	varchar(10),
                                            longitude 	real,
                                            latitude 	real);'''
    if not cur.fetchone()[0]:
        pg_install = """create extension postgis; """
        cur.execute(pg_install)
        cur.execute(sql_table)
    else:
        cur.execute(sql_table)

    con.commit()


def sql_del_one(name_srch, long, lat):  # SQL
    cur = con.cursor()
    sql_del = f"""delete from rest_users
                  where name='{name_srch}'
                  and longitude='{long}'
                  and latitude='{lat}';"""

    cur.execute(sql_del)
    con.commit()

    sql_check = """select * from rest_users;"""
    cur.execute(sql_check)
    return cur.fetchall()


# Ordinary methods(links to sql methods)

def neighbours(name_srch, distance):
    res = neighbours_sql(name_srch, distance)
    return res


def del_all_pers():
    res = del_all_sql()
    return res


def get_all():  # SQL # todo LOOK HERE RETURN INFO
    info = pers_info
    sel = select_all_sql()
    return dict(sel)


def person_gen(name, x, y):  # SQL - todo done
    pers_info[name] = {'coords': [x, y]}
    insert_table_sql(name, x, y)
    info = pers_info[name]
    return info


def update_coords(name_srch, long, lat):
    res = update_coords_sql(name_srch, long, lat)
    for name, coords in pers_info.items():
        if name_srch == name:
            coords['coords'][0] = long
            coords['coords'][1] = lat
            break
    return pers_info[name_srch]


def del_pers(name_srch, long, lat):
    res = sql_del_one(name_srch, long, lat)
    for name in list(pers_info):
        if name == name_srch:
            pers_info.pop(name)
    return res


# Hub-methods
@app.route('/person',
           methods=['PUT',
                    'POST',
                    'DELETE']
           )  # CRUD actions
def person_actions():
    person_name = request.args.get('name')
    coord_long = float(request.args.get('coord_x'))
    coord_lat = float(request.args.get('coord_y'))
    if request.method == 'POST':  # Create
        person = person_gen(person_name, coord_long, coord_lat)
        return json.dumps(person)
    elif request.method == 'PUT':  # Update
        new_position = update_coords(person_name, coord_long, coord_lat)
        return json.dumps(new_position)
        pass
    elif request.method == 'DELETE':  # Delete
        del_one = del_pers(person_name, coord_long, coord_lat)
        return json.dumps(del_one)


@app.route('/persons', methods=['GET'])  # CRUD action (read) todo done SQL
def show_data():
    return get_all()  # conversion, read


@app.route('/persons_near',
           methods=['GET'])
def search_near():
    name = (request.args.get('name'))
    distance = (request.args.get('distance'))
    res = neighbours(name, distance)
    return json.dumps(res)


@app.route('/persons', methods=['DELETE'])  # DELETE WHOLE TABLE
def delete_all():
    res = del_all_pers()
    return json.dumps(res)


if __name__ == '__main__':
    # app.debug = 1
    app.run()

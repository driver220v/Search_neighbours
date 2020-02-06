import requests
from time import time
from random import uniform, randint
from matplotlib import pyplot as plt


# decorator to measure functions' time execution
def time_dec(original_func):
    def wrapper(*args):
        start = time()
        res = original_func(*args)
        end = time()
        dif = end - start
        # function name, payload(10, 100, 1000...), time of execution
        # example: ('del_one_pers', 10): 0.029580116271972656
        exec_time[original_func.__name__, i] = dif
        return res

    return wrapper


# Service test functions (CRUD)

# Show all persons method
def get_pers():  # reference: select_all persons
    r = requests.get('http://localhost:5000/persons')
    return r.json()


def post_pers(user):  # reference: person_gen
    payload = {'name': f'{user}',
               'longitude': f'{uniform(10.000, 10.999)}',
               'latitude': f'{uniform(10.000, 10.999)}'}
    r = requests.post('http://localhost:5000/person', params=payload)


def put_upd(person):  # reference: update_coords
    payload = {'name': f"{person}",
               'longitude': f'{uniform(10.000, 10.999)}',
               'latitude': f'{uniform(10.000, 10.999)}'}
    r = requests.put('http://localhost:5000/person', params=payload)


def delete_all_mhd():  # reference: del_all_pers
    r = requests.delete('http://localhost:5000/persons')


def delete_one_mhd(person):  # reference: del_one_pers
    payload = {'name': f"{person}"}
    r = requests.delete('http://localhost:5000/person', params=payload)


def pers_near(person):  # reference: neighbours
    payload = {'name': f"{person}",
               'distance': f'{randint(100, 1000)}'}
    r = requests.get('http://localhost:5000/persons_near', params=payload)


@time_dec
def select_all():
    get_pers()


@time_dec
def person_gen(pers_range):
    for pers in range(0, pers_range):
        post_pers(pers)


@time_dec
def upd_coords(pers_range):
    for pers in range(0, pers_range):
        put_upd(pers)


@time_dec
def neighbour(pers_range):
    for pers in range(0, pers_range):
        pers_near(pers)


@time_dec
def del_one_pers(pers_range):
    # DELETE METHODS :
    # delete_all_mhd()     1) DELETE WHOLE TABLE
    # delete_one_mhd(0, pers_range) 2) DELETE USERS IN TABLE ONE BY ONE
    for pers in range(0, pers_range):
        delete_one_mhd(pers)


def build_graph():
    with open('tests_results.txt', 'w') as test_results:
        dots = {}
        dots_axis = dots.fromkeys(persons_range, 0)
        for key, value in exec_time.items():
            test_results.write(f'{key}: {value}')
            test_results.write('\n')
            if key[1] == 10:
                dots_axis[10] += value

            elif key[1] == 100:
                dots_axis[100] += value

            elif key[1] == 1000:
                dots_axis[1000] += value

            elif key[1] == 2000:
                dots_axis[2000] += value

            elif key[1] == 3000:
                dots_axis[3000] += value

            elif key[1] == 5000:
                dots_axis[5000] += value

            elif key[1] == 10000:
                dots_axis[10000] += value

    lists_persons = sorted(dots_axis.items())

    plt.xlabel('persons')
    plt.ylabel('seconds')
    plt.title(f'Payload table')

    axis_x, axis_y = zip(*lists_persons)
    plt.plot(axis_x, axis_y)
    plt.savefig('graph.png')


exec_time = {}
# check time of functions execution with payload of 10, 100, 1000... users
persons_range = [10, 100, 1000, 2000, 3000, 5000, 10000]
for i in persons_range:
    select_all()
    person_gen(i)
    select_all()
    upd_coords(i)
    neighbour(i)
    del_one_pers(i)
    select_all()

build_graph()

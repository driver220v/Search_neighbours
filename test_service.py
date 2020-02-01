import requests
import json
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
        # print(f'function {original_func.__name__} executed in {dif} second') # visualize process
        exec_time[original_func.__name__, i] = dif
        return res

    return wrapper


# Rest service test functions (CRUD)
@time_dec
# Show all persons method
def get_pers():  # reference: GET show_all persons
    r = requests.get('http://localhost:5000/persons')
    return r.json()


@time_dec
def post_mhd(user_range):  # reference:  Post person_gen
    for user in range(0, user_range):
        payload = {'name': f'{user}',
                   'coord_x': f'{uniform(10.000, 10.999)}',
                   'coord_y': f'{uniform(10.000, 10.999)}'}
        r = requests.post('http://localhost:5000/person', params=payload)
        to_return = r.text
        # print(json.dumps(to_return, indent=2)) -visualize process
        json.dumps(to_return, indent=2)


@time_dec
def put_mhd(ppl):  # reference:  PUT/ update_coords
    # example:  ppl.items() == {"K": {"coords": [-77,-4]}, "Z": {"coords": [12,14]
    for pers in ppl:
        payload = {'name': f'{pers}',
                   'coord_x': f'{uniform(10.000, 10.999)}',
                   'coord_y': f'{uniform(10.000, 10.999)}'}
        r = requests.put('http://localhost:5000/person', params=payload)
        to_return = r.json()
        # print(json.dumps(to_return, indent=2)) -visualize process
        json.dumps(to_return, indent=2)


#
@time_dec
def delete_all_mhd():  # reference: DELETE/ delete_pers
    r = requests.delete('http://localhost:5000/persons')
    to_return = r.json()
    # print(json.dumps(to_return, indent=2)) -visualize process
    json.dumps(to_return, indent=2)


@time_dec
def delete_one_mhd(ppl):  # reference: DELETE/ delete_pers
    del_pers = {}
    for pers, coords in ppl.items():
        payload = {'name': f'{pers}',
                   'coord_x': f'{coords["coords"][0]}',
                   'coord_y': f'{coords["coords"][1]}'}
        r = requests.delete('http://localhost:5000/person', params=payload)
        to_return = r.json()
        # print(json.dumps(to_return, indent=2)) -visualize process
        inf = json.dumps(to_return, indent=2)
        del_pers[pers] = inf
    return del_pers


@time_dec
def pers_near(ppl):  # reference GET/ person_near
    for pers in ppl:
        payload = {'name': f'{pers}',
                   'distance': f'{randint(100, 1000)}'}
        r = requests.get('http://localhost:5000/persons_near', params=payload)
        to_return = r.json()
        # print(json.dumps(to_return, indent=2)) -visualize process
        json.dumps(to_return, indent=2)


exec_time = {}
# check time of functions execution with payload of 10, 100, 1000... users
persons_range = [10, 100, 1000, 2000, 3000, 5000, 10000]
for i in persons_range:
    get_pers()
    post_mhd(i)
    get_pers()
    put_mhd(get_pers())
    pers_near(get_pers())

    # DELETE METHODS :
    # delete_all_mhd()  # 1) DELETE WHOLE TABLE
    # delete_one_mhd(get_pers())  # 2) DELETE USERS IN TABLE ONE BY ONE

with open('tests.txt', 'w') as tests:
    dots = {}
    dots_axis = dots.fromkeys(persons_range, 0)
    for key, value in exec_time.items():
        tests.write(f'{key}: {value}')
        tests.write('\n')
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

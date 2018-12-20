import pynput
from pynput import keyboard
import time
import math
import numpy as np
from statistics import variance
import sqlite3

conn = sqlite3.connect('model.db')
c = conn.cursor()

vector = []                                         # Dinamic dictionary - safety double click
time_on_press = {}                                  # Key hold time (list)
hold_time = []                                      # Time between clicks (dict)
between_time = []
last_time = 0
count = 0
count_stud = [1, 1, 3.07, 1.88, 1.63, 1.53, 1.47, 1.43, 1.41, 1.39,
             1.38, 1.37, 1.36, 1.36, 1.35, 1.35, 1.34, 1.34,
             1.33, 1.33, 1.33]
def on_press(key):
    try:
        global count
        if (key != keyboard.Key.enter):
            time_on_press[key] = time.clock()       # Check time here
            #print('key {0} pressed'.format(key.char))
        elif (count != 0) & (key == keyboard.Key.enter):    
            return False                            # Stop listener
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    global count, last_time
    if (key != keyboard.Key.enter):
        time_now = time.clock()
        hold_time.append(round((time_now - time_on_press[key]), 6)) # Hold time (little delay)
        # Calculate between_time (skip first click)
        if(count > 0):
            between_time.append(round((time_now - last_time - (hold_time[count-1] + hold_time[count])),6))
            #print('between time is', between_time[count - 1])
        #print('{0} released'.format(key))
        #print('hold time is', hold_time[count])
        last_time = time.clock()                    # last_time for calculate between_time
        count += 1
    elif (count != 0) & (key == keyboard.Key.enter):
        return False                                # Stop listener

def count_model(vector):
    hold = []
    between = []
    v_size = len(vector)
    for i in vector:
        hold.append(i[0])
    for i in vector:
        between.append(i[1])
    h_mean = np.mean(hold, axis = 0)
    b_mean = np.mean(between, axis = 0)
    h_var = np.var(hold, ddof = 0, axis = 0)
    b_var = np.var(between, ddof = 0, axis = 0)
    h_min = h_mean - count_stud[v_size]*np.sqrt(h_var)
    h_max = h_mean + count_stud[v_size]*np.sqrt(h_var)
    b_min = b_mean - count_stud[v_size]*np.sqrt(b_var)
    b_max = b_mean + count_stud[v_size]*np.sqrt(b_var)
    return [[h_min, h_max], [b_min, b_max]]

def val_reset():
    global count, last_time
    time_on_press.clear()
    hold_time.clear()
    between_time.clear()
    last_time = 0
    count = 0

def create_table_db():
    c.execute("CREATE TABLE IF NOT EXISTS model(name TEXT, password TEXT, type TEXT, '1' REAL, '2' REAL, '3' REAL, '4' REAL, '5' REAL, '6' REAL, '7' REAL, '8' REAL, '9' REAL, '10' REAL)")

def data_entry_db(name, password, v):
    types = ['h_min', 'h_max', 'b_min', 'b_max']
    arr = []
    for t in types:
        if (t == 'h_min'): 
            x = 0; y = 0
        elif(t == 'h_max'):
            x = 0; y = 1
        elif(t == 'b_min'):
            x = 1; y = 0
        elif(t == 'b_max'):
            x = 1; y = 1
        else:
            pass
        arr.append(name)
        arr.append(password)
        arr.append(t)
        arr.extend(v[x][y].tolist())
        while(len(arr) != 13):
            arr.append(None)
        c.execute("INSERT INTO model VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", arr)
        arr.clear()
    conn.commit()

def hemming_entry_db(name, password, v, E):
    arr = []
    arr.append(name)
    arr.append(password)
    arr.append('hemming')
    arr.append(E)
    while(len(arr) != 13):
        arr.append(None)
    c.execute("INSERT INTO model VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", arr)
    conn.commit()

def check_in():
    E = []
    print("Type your name: ")
    name = input()
    count = 0
    while (count != 3):
        features, password = create_vector()
        vector.append(features)
        count += 1
    model = count_model(vector)                     # Create model
    create_table_db()
    data_entry_db(name, password, model)               # Create record in DataBase
    count = 0
    while(count != 3):
        features, password = create_vector()
        E.append(hemming_distance(name, features, password))
        count += 1
    limit = np.mean(E, axis = 0) + count_stud[len(E)] * np.var(E, ddof=0, axis=0)
    hemming_entry_db(name, password, model, limit)
    
    '''
    1)  Добавить цикл из n эпох -> высчитывать вектор хэминга для каждого ввода
    2)  Посчитать тот средий вектор
    3)  Ошибки считать при авторизации, либо при цикле свыше 
        (сравнивая с вектором хемминга на прошлой интерации)
    '''

def create_vector():
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
            print("Type your keyword(<13 letters): ")
            password = input()
            listener.join()
    vector = [np.array(hold_time), np.array(between_time)]
    val_reset()
    return vector, password

def hemming_distance(username, vector_pass, password):
    E = [[],[]]                                     # Hamming vector
    distance = 0
    count = 3                                       # Third record in db
    c.execute('SELECT * FROM model WHERE name = ?', [username])
    rows = c.fetchall()
    if (len(rows) == 0):                            # Check name
        print("Wrong name!")
        return None
    if(rows[0][1] != password):                     # Check password
        print("Wrong password!")
        return None
    for i in vector_pass[0]:
        if (rows[0][2] == 'h_min') and (rows[1][2] == 'h_max'):
            if(i > rows[0][count]) and (i < rows[1][count]):
                E[0].append(0)
            else:
                E[0].append(1)
                distance+=1
            count+=1
    count = 3                                       # Third record in db
    for i in vector_pass[1]:
        if(rows[2][2] == 'b_min') and (rows[3][2] == 'b_max'):
            if(i > rows[2][count]) and (i < rows[3][count]):
                E[1].append(0)
            else:
                E[1].append(1)
                distance+=1
            count+=1
    return distance

def authentication(username, distance):
    c.execute('SELECT * FROM model WHERE name = ?', [username])
    rows = c.fetchall()
    if(rows[4][3]>distance):
        print("Access is allowed")
        return True
    else:
        print("Access is denied")
        return False
       

def errors(username):
    N = 5
    allow = 0
    count = 0
    while(count < N):
        print("Type password:")
        vector_pass, password = create_vector()
        distance = hemming_distance(username, vector_pass, password)
        if(distance != None):
            if(authentication(username, distance)):
                allow+=1
        count += 1
    print("1: ", 1 - allow/N, "2: ", allow/N)

def main():
    while True:
        print("Check in (press 1) | Authentication (press 2) | Errors (press 3) | Exit (press 4)")
        print("Press number:")
        tmp = input()
        if(tmp == '1'):
            check_in()
        elif (tmp == '2'):
            print("Type name:")
            username = input()
            print("Type password:")
            vector_pass, password = create_vector()
            distance = hemming_distance(username, vector_pass, password)
            if(distance != None):
                authentication(username, hemming_distance(username, vector_pass, password))
        elif (tmp == '3'):
            print("Type name:")
            username = input()
            errors(username)
        else:
            if(tmp == '4'):
                c.close()
                conn.close()
                break
if __name__ == "__main__":
    main()

import pynput
from pynput import keyboard
import time
import math
import numpy as np
from statistics import variance
import sqlite3

conn = sqlite3.connect('model.db')
c = conn.cursor()

vector = []             # Dinamic dictionary - safety double click
time_on_press = {}      # Key hold time (list)
hold_time = []          # Time between clicks (dict)
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
        # Hold time (little delay)
        hold_time.append(round((time_now - time_on_press[key]), 6))
        # Calculate between_time (skip first click)
        if(count > 0):
            between_time.append(round((time_now - last_time - (hold_time[count-1] + hold_time[count])),6))
            #print('between time is', between_time[count - 1])
        #print('{0} released'.format(key))
        #print('hold time is', hold_time[count])
        last_time = time.clock()        # last_time for calculate between_time
        count += 1
    elif (count != 0) & (key == keyboard.Key.enter):
        return False                # Stop listener

def count_model(vector):
    hold = []
    between = []
    v_size = len(vector)
    for i in vector:
        hold.append(i[0])
        print(i[0])
    for i in vector:
        between.append(i[1])
    h_mean = np.mean(hold, axis = 0)
    b_mean = np.mean(between, axis = 0)
    h_var = np.var(hold, ddof = 0, axis = 0)
    b_var = np.var(between, ddof = 0, axis = 0)
    print(h_mean)
    print(h_var)
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

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS model(name TEXT, password TEXT, type TEXT,'1' REAL, '2' REAL, '3' REAL, '4' REAL, '5' REAL, '6' REAL, '7' REAL, '8' REAL)")

def data_entry(name, password, v):
    c.execute("INSERT INTO model (name, password, type, '1', '2', '3', '4', '5', '6') VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (name, password, 'h_min', v[0][0][0], v[0][0][1], v[0][0][2], v[0][0][3], v[0][0][4], v[0][0][5], v[0][0][6], v[0][0][7]))
    c.execute("INSERT INTO model (name, password, type, '1', '2', '3','4', '5', '6') VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (name, password, 'h_max', v[0][1][0], v[0][1][1], v[0][1][2], v[0][1][3], v[0][1][4], v[0][1][5], v[0][1][6], v[0][1][7]))
    c.execute("INSERT INTO model (name, password, type, '1', '2', '3','4', '5') VALUES (?,?,?,?,?,?,?,?,?,?)",
                (name, password,'b_min', v[1][0][0], v[1][0][1], v[1][0][2], v[1][0][3], v[1][0][4], v[1][0][5], v[1][0][6]))
    c.execute("INSERT INTO model (name, password, type, '1', '2', '3','4', '5') VALUES (?,?,?,?,?,?,?,?,?,?)",
                (name, password, 'b_max', v[1][1][0], v[1][1][1], v[1][1][2], v[1][1][3], v[1][1][4], v[1][1][5], v[1][1][6]))
    conn.commit()

def check_in():
    print("Type your name: ")
    name = input()
    count = 0
    while (count != 3):
        features, password = create_vector()
        vector.append(features)
        count += 1
    model = count_model(vector)         # Create model
    print(model)
    create_table()
    data_entry(name, password, model)   # Create record in DataBase

def create_vector():
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
            print("Type your keyword(6 letters): ")
            password = input()
            listener.join()
    vector = [np.array(hold_time), np.array(between_time)]
    val_reset()
    return vector, password

def authentication(username, vector_pass, password):
    E = []
    count = 3
    c.execute('SELECT * FROM model WHERE name = ?', [username])
    rows = c.fetchall()
    for i in vector_pass[0]:
        if(i > rows[0][count]) and (i < rows[1][count]) and (rows[0][2] == 'h_min') and (rows[1][2] == 'h_max'):
            E[0].append(0)
        count+=1
    count = 3
    for i in vector_pass[1]:
        if(i > rows[3][count]) and (i < rows[4][count]) and (rows[3][2] == 'b_min') and (rows[4][2] == 'b_max'):
            E[1].append(0)
        count+=1

def main():
    while True:
        print("Check in (press 1) | Authentication (press 2) | Exit (press 3)")
        print("Press number:")
        tmp = input()
        if(tmp == '1'):
            check_in()
        elif (tmp == '2'):
            print("Type name:")
            name = input()
            print("Type password:")
            vector_pass, password = create_vector()
            authentication(name, vector_pass, password)
        else:
            if(tmp == '3'):
                c.close()
                conn.close()
                break
if __name__ == "__main__":
    main()

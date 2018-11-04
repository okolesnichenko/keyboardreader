import pynput
from pynput import keyboard
import time
import math
import numpy as np

vector = []
# Dinamic dictionary - safety double click
time_on_press = {}
# Key hold time (list)
hold_time = []
# Time between clicks (dict)
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
            # Check time here
            time_on_press[key] = time.clock()
            #print('key {0} pressed'.format(key.char))
        elif (count != 0) & (key == keyboard.Key.enter):
            # Stop listener
            return False
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    global count, last_time
    if (key != keyboard.Key.enter):
        time_now = time.clock()
        # Hold time (little delay)
        hold_time.append(time_now - time_on_press[key])
        # Calculate between_time (skip first click)
        if(count > 0):
            between_time.append(time_now - last_time - (hold_time[count-1] + hold_time[count]))
            #print('between time is', between_time[count - 1])
        #print('{0} released'.format(key))
        #print('hold time is', hold_time[count])
        # last_time for calculate between_time
        last_time = time.clock()
        count += 1
    elif (count != 0) & (key == keyboard.Key.enter):
        # Stop listener
        return False

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
    h_var = np.var(hold, ddof = 1, axis = 0)
    b_var = np.var(between, ddof = 1, axis = 0)
    print(h_mean)
    print(b_mean)
    h_min = h_mean - count_stud[v_size]*h_var
    h_max = h_mean + count_stud[v_size]*h_var
    b_min = b_mean - count_stud[v_size]*b_var
    b_max = b_mean + count_stud[v_size]*b_var
    return [[h_min, h_max], [b_min, b_max]]

def init():
    global count, last_time
    time_on_press.clear()
    hold_time.clear()
    between_time.clear()
    last_time = 0
    count = 0

def main():
    count = 0
    while (count != 3):
        with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
            print("Type your keyword: ")
            keyword = input()
            if(keyboard.Key ==keyboard.Key.esc):
                break
            listener.join()
        vector.append([np.array(hold_time), np.array(between_time)])
        #print("Hold time: ", hold_time)
        #print("Time between: ", between_time)
        #print(np.array(between_time))
        # Reset lists
        count += 1
        init()
    res = count_model(vector)
    print(res)
if __name__ == "__main__":
    main()

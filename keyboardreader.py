import pynput
from pynput import keyboard
import time

vector = []
# Dinamic dictionary - safety double click
time_on_press = {}
# Key hold time (list)
hold_time = []
# Time between clicks (dict)
between_time = []
last_time = 0
count = 0
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

def reset():
    global count, last_time
    time_on_press.clear()
    hold_time.clear()
    between_time.clear()
    last_time = 0
    count = 0

def main():
    while True:
        with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
            print("Type your keyword: ")
            keyword = input()
            listener.join()
        vector.append([hold_time, between_time])
        print("Hold time: ", hold_time)
        print("Time between: ", between_time)
        print("Vector size: ", len(vector))
        # Reset lists
        reset()
if __name__ == "__main__":
    main()

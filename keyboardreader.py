import pynput
from pynput import keyboard
import time

# Dinamic dictionary - save double click
time_on_press = {}
# Key hold time (list)
hold_time = []
# Time between clicks (dict)
between_time = []
last_time = 0
count = 0
def on_press(key):
    try:
        # Check time here
        # Global time_on_press
        time_on_press[key] = time.clock()
        print('key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    global count, last_time
    time_now = time.clock()
    # Hold time (little delay)
    hold_time.append(time_now - time_on_press[key])

    # Calculate between_time (skip first click)
    if(count > 0):
        between_time.append(time_now - last_time - (hold_time[count-1] + hold_time[count]))
        print('between time is', between_time[count - 1])

    # Print it
    print('{0} released'.format(key))
    print('hold time is', hold_time[count])
    print("---")

    # last_time for calculate between_time
    last_time = time.clock()
    count += 1
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def main():
    h = 0
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join()
    print(hold_time)
    print(between_time)
if __name__ == "__main__":
    main()

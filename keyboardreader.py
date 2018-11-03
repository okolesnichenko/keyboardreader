import pynput
from pynput import keyboard
import time

# Dinamic dictionary
time_on_press = {'': 0}
hold_time = []
count = 0
def on_press(key):
    try:
        # Check time here
        #global time_on_press
        time_on_press[key] = time.clock()
        print('key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    # Hold time
    global count
    hold_time.append(time.clock() - time_on_press[key])
    print('{0} released'.format(key))
    print('hold time is', hold_time[count])
    count += 1
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def main():
    h = 0
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    print(hold_time)
if __name__ == "__main__":
    main()

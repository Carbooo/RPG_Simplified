import time as time

automatic = False
log_level = 1
log_debug = False
current_char = None
actions = {}
action0 = []
action1 = []


def optional_input(txt):
    global automatic
    if not automatic:
        return input(txt)
    else:
        global current_char
        global actions
        action = actions[current_char.name].pop(0)
        return action


def optional_print(*argv, skip_line=False, level=1, debug=False):
    global log_level
    global log_debug
    if not debug or log_debug:
        if level >= log_level:
            if skip_line:
                print(*argv, end=' ')
            else:
                print(*argv)


def optional_sleep(duration):
    global automatic
    if not automatic:
        time.sleep(duration)

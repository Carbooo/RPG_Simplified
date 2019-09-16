automatic = False
log_level = 1
actions = []


def optional_input(txt):
    global automatic
    if not automatic:
        return input(txt)
    else:
        global actions
        return actions.pop(0)


def optional_print(*argv, end=None, level=1):
    global log_level
    if level >= log_level:
        if end:
            print(*argv, end=end)
        else:
            print(*argv)

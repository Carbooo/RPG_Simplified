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


def optional_print(*argv, skip_line=False, level=1):
    global log_level
    if level >= log_level:
        if skip_line:
            print(*argv, end=' ')
        else:
            print(*argv)

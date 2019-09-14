automatic = False
actions = []

def optional_input(txt):
    global automatic
    if not automatic:
        return input(txt)
    else:
        global actions
        return actions.pop(0)

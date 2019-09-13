import time as time


#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class Actions:
    """Super class for all actions"""

    def __init__(self, fight):
        self.fight = fight
        self.is_a_success = False

    @staticmethod
    def cancel_action(read):
        try:
            read = int(read)
            if read == 0 or read == '0':
                print("Action cancelled!")
                time.sleep(1)
                return True
            return False
        except:
            return False

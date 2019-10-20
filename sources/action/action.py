import time as time
import sources.miscellaneous.global_functions as func


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
                func.optional_print("Action cancelled!")
                func.optional_sleep(1)
                return True
            return False
        except:
            return False

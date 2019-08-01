

#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class Actions:
    'Super class for all fight actions'

    def __init__(self, fight):
        self.fight = fight
        self.is_a_success = False
        
    def start(self):
        return False
        
    
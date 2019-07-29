

#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class Actions:
    'Super class for all fight actions'
    
    time_ratio = 1.0 #Ratio when the action will occur

    def __init__(self, fight):
        self.fight = fight
        self.timeline = 0
        self.is_a_success = False
        
    def start(self):
        return False
        
    def result(self):
        self.fight.scheduler.remove(self)
        return False
        
    
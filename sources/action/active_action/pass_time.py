import time as time
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions


#############################################################
########################## PASS CLASS #######################
#############################################################
class PassTime(ActiveActions):
    """Class to let a character pass time"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Passing time"
        self.is_a_success = self.start()
        
    def start(self):
        print("How much time do you want to wait?")
        txt = "--> Number of 0.1 turn (0 = Cancel): "
        while 1:
            try:
                read = int(input(txt))
                if Actions.cancel_action(read):
                    return False
                else:
                    break
            except:
                print("The input is not a number")
                continue
            
        self.initiator.spend_absolute_time(read * 0.1)
        print("You have decided to wait", round(read * 0.1, 1), "turn(s)")
        time.sleep(3)
        return True

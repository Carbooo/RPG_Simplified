from sources.action.Actions import ActiveActions
from sources.character.Characters import Characters

#############################################################
########################## PASS CLASS #######################
#############################################################
class PassChar(ActiveActions):
    'Class to let a character pass time'
    
    def __init__(self, fight, initiator):
        super().__init__(self, fight, initiator)
        self.is_a_success = self.start()
        
    def start(self):
        print("How much time do you want to wait?")
        txt = "--> Number of " + str(Characters.Pass[2]) + " turns (0 = Cancel): "
        while 1:
            try:
                read = int(input(txt))
                if self.fight.cancel_action(read):
                    return False
                else:
                    break
            except:
                print("The input is not a number")
                continue
            
        self.initiator.spend_time(read * Characters.Pass[2])
        print("You have decided to wait", round(read*Characters.Pass[2],1), "turn(s)")
        time.sleep(3)
        return True

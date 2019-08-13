from sources.action.Actions import Actions
from sources.character.Characters import Characters

#############################################################
########################## PASS CLASS #######################
#############################################################
class PassChar:
    'Class to let a character pass time'
    
    def __init__(self, fight):
        Actions.__init__(self, fight)
        self.is_a_success = self.start()
        
    def start(self):
        Actions.start(self)
        
        print("How much time do you want to wait?")
        txt = "--> Number of " + str(Characters.Pass[2]) + " turns (0 = Cancel): "
        while 1:
            try:
                read = int(input(txt))
                if self.cancel_action(read):
                    return False
                else:
                    break
            except:
                print("The input is not a number")
                continue
            
        character.spend_time(read * Characters.Pass[2])
        character.spend_stamina(read * Characters.Pass[3])
        character.calculate_characteristic()
        print("You have decided to wait", round(read*Characters.Pass[2],1), "turn(s)")
        time.sleep(3)
        return True

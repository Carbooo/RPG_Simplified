import time as time
import math as math
from sources.action.Actions import ActiveActions


#############################################################
########################## REST CLASS #######################
#############################################################
class RestChar(ActiveActions):
    """Class to make a character rest"""

    min_turn = 1
    max_turn = 10
    resting_ratio = 1.0/3.0
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Resting"
        self.nb_of_turns = -1
        self.resting_ratio = 1
        self.is_a_success = self.start()

    def start(self):
        print("How much time do you want to rest? (Resting longer make it more efficient)")
        txt = "--> Number of turns (0 = Cancel): "
        while 1:
            try:
                self.nb_of_turns = int(input(txt))
                if self.fight.cancel_action(self.nb_of_turns):
                    return False
                elif self.nb_of_turns < RestChar.min_turn:
                    print("You cannot rest less than ", RestChar.min_turn, " turns")
                elif self.nb_of_turns > RestChar.max_turn:
                    print("You cannot rest more than ", RestChar.max_turn, " turns")
                else:
                    break
            except:
                print("The input is not an integer")

        print("You have decided to rest for ", self.nb_of_turns, " turn(s)")
        time.sleep(3)
        
        self.resting_ratio = math.pow(self.nb_of_turns, RestChar.resting_ratio)
        self.end_update([], 0, 1, True)
        return True

    def execute(self):
        self.initiator.body.global_rest(self.resting_ratio)
        self.nb_of_turns -= 1
        if self.nb_of_turns > 0:
            self.end_update([], 0, 1, True)
        return True

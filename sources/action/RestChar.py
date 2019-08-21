import time as time
from sources.action.Actions import ActiveActions


#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class RestChar(ActiveActions):
    'Class to make a character rest'

    rest_config = [
        "min_turn" : 1,
        "max_turn" : 5
    ]
    
    def __init__(self, fight, initiator):
        super().__init__(self, fight, initiator)
        self.nb_of_turn = -1
        self.is_a_success = self.start()

    def start(self):
        print("How much time do you want to rest?")
        txt = "--> Number of turns (0 = Cancel): "
        while 1:
            try:
                self.nb_of_turn = int(input(txt))
                if self.fight.cancel_action(self.nb_of_turn):
                    return False
                elif self.nb_of_turn < RestChar.rest_config["min_turn"]:
                    print("You cannot rest less than", RestChar.rest_config["min_turn"], "turns")
                elif self.nb_of_turn > RestChar.rest_config["max_turn"]:
                    print("You cannot rest more than", RestChar.rest_config["max_turn"], "turns")
                else:
                    break
            except:
                print("The input is not an integer")

        print("You have decided to rest", self.nb_of_turn, "turn(s)")
        time.sleep(3)
        self.end_update([], 0, 1, True)
        return True

    def execute(self):
        self.initiator.body.global_rest(1)
        self.nb_of_turn -= 1
        if self.nb_of_turn > 0:
            self.end_update([], 0, 1, True)
        return True

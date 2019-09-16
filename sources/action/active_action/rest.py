import time as time
import math as math
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
########################## REST CLASS #######################
#############################################################
class Rest(ActiveActions):
    """Class to make a character rest"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Resting"
        self.nb_of_turns = -1
        self.resting_ratio = 1
        self.is_a_success = self.start()

    def start(self):
        func.optional_print("How much time do you want to rest? (Resting longer make it more efficient)")
        txt = "--> Number of turns (0 = Cancel): "
        while 1:
            try:
                self.nb_of_turns = int(func.optional_input(txt))
                if Actions.cancel_action(self.nb_of_turns):
                    return False
                elif self.nb_of_turns < cfg.min_rest_turn:
                    func.optional_print("You cannot rest less than ", cfg.min_rest_turn, " turns")
                elif self.nb_of_turns > cfg.max_rest_turn:
                    func.optional_print("You cannot rest more than ", cfg.max_rest_turn, " turns")
                else:
                    break
            except:
                func.optional_print("The input is not an integer")

        func.optional_print("You have decided to rest for ", self.nb_of_turns, " turn(s)")
        time.sleep(3)
        
        self.resting_ratio = math.pow(self.nb_of_turns, cfg.resting_ratio)
        self.end_update(0, 1, True)
        return True

    def execute(self):
        self.initiator.body.global_rest(self.resting_ratio)
        self.nb_of_turns -= 1
        if self.nb_of_turns > 0:
            self.end_update(0, 1, True)
        return True

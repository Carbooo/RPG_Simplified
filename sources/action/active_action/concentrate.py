import time as time
import math as math
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
###################### CONCENTRATE CLASS ####################
#############################################################
class Concentrate(ActiveActions):
    """Class to make a character concentrate"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Concentrating"
        self.nb_of_turns = -1
        self.concentration_ratio = 1
        self.feeling = ""
        self.action = ""
        self.is_a_success = self.start()

    def start(self):
        func.optional_print("On which feeling do you want to concentrate?")
        for feeling in cfg.feelings_list:
            func.optional_print("- ", feeling)
        txt = "--> Feeling (0 = Cancel): "
        while 1:
            self.feeling = func.optional_input(txt)
            if Actions.cancel_action(self.feeling):
                return False
            elif self.feeling in cfg.feelings_list:
                break
            else:
                func.optional_print("The feeling is not recognized")

        func.optional_print("")
        func.optional_print("Do you want to increase (INC) or decrease (DEC) the feeling?")
        txt = "--> INC / DEC (0 = Cancel): "
        while 1:
            self.action = func.optional_input(txt)
            if Actions.cancel_action(self.action):
                return False
            elif self.action == "INC":
                self.action = "increase"
                break
            elif self.action == "DEC":
                self.action = "decrease"
                break
            else:
                func.optional_print("Command invalid. You must choose between increase (INC) and decrease (DEC).")

        func.optional_print("")
        func.optional_print("How much time do you want to concentrate? (Concentrating longer make it more efficient)")
        func.optional_print("Beware that each new concentration is less efficient than the previous ones!")
        txt = "--> Number of turns (0 = Cancel): "
        while 1:
            try:
                self.nb_of_turns = int(func.optional_input(txt))
                if Actions.cancel_action(self.nb_of_turns):
                    return False
                elif self.nb_of_turns < cfg.min_concentration_turn:
                    func.optional_print("You cannot rest less than", cfg.min_concentration_turn, "turns")
                elif self.nb_of_turns > cfg.max_concentration_turn:
                    func.optional_print("You cannot rest more than", cfg.max_concentration_turn, "turns")
                else:
                    break
            except:
                func.optional_print("The input is not an integer")

        func.optional_print("")
        func.optional_print("You have decided to", self.action, "your", self.feeling, "for", self.nb_of_turns, "turns")
        time.sleep(3)
        
        self.concentration_ratio = math.pow(self.nb_of_turns, cfg.concentration_rate)
        self.initiator.nb_of_concentrate += 1
        self.end_update(cfg.actions["concentrate"]["stamina"], 1.0, True)
        return True

    def execute(self):
        self.initiator.feelings[self.feeling].concentrate_energy_update(self.action, self.concentration_ratio *
                                                                        min(1.0,
                                                                            cfg.deconcentration_rate /
                                                                            self.initiator.nb_of_concentrate
                                                                            )
                                                                        )
        self.nb_of_turns -= 1
        if self.nb_of_turns > 0:
            self.end_update(cfg.actions["concentrate"]["stamina"], 1.0, True)
        return True

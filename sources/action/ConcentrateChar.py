import time as time
from sources.action.Actions import ActiveActions
import sources.miscellaneous.global_variables as global_variables

#############################################################
###################### CONCENTRATE CLASS ####################
#############################################################
class ConcentrateChar(ActiveActions):
    'Class to make a character concentrate'

    min_turn = 3,
    max_turn = 10,
    concentration_rate = 1.0/3.0
    deconcentration_rate = 1.5
    
    def __init__(self, fight, initiator):
        super().__init__(self, fight, initiator)
        self.name = "Concentrating"
        self.nb_of_turns = -1
        self.concentration_ratio = 1
        self.feeling = ""
        self.action = ""
        self.is_a_success = self.start()

    def start(self):
        print("On which feeling do you want to concentrate?")
        for feeling in global_variables.feelings_list:
            print(feeling)
        txt = "--> Feeling (0 = Cancel): "
        while 1:
            self.feeling = input(txt)
            if self.fight.cancel_action(self.feeling):
                return False
            elif self.feeling in global_variables.feelings_list:
                break
            else:
                print("The feeling is not recognized")

        print("Do you want to increase (INC) or decrease (DEC) the feeling?")
        txt = "--> INC / DEC (0 = Cancel): "
        while 1:
            self.action = input(txt)
            if self.fight.cancel_action(self.action):
                return False
            elif self.action == "INC":
                self.action = "increase"
                break
            elif self.action == "DEC":
                self.action = "decrease"
                break
            else:
                print("Command invalid. You must choose between increase (INC) and decrease (DEC).")
            
        print("How much time do you want to concentrate? (Concentrating longer make it more efficient)")
        print("Beware that each new concentration is less efficient than the previous ones!")
        txt = "--> Number of turns (0 = Cancel): "
        while 1:
            try:
                self.nb_of_turns = int(input(txt))
                if self.fight.cancel_action(self.nb_of_turns):
                    return False
                elif self.nb_of_turns < ConcentrateChar.min_turn:
                    print("You cannot rest less than ", ConcentrateChar.min_turn, " turns")
                elif self.nb_of_turns > ConcentrateChar.max_turn:
                    print("You cannot rest more than ", ConcentrateChar.max_turn, " turns")
                else:
                    break
            except:
                print("The input is not an integer")

        print("You have decided to ", self.action, " your ", self.feeling, " for ", self.nb_of_turns, " turn(s)")
        time.sleep(3)
        
        self.concentration_ratio = math.pow(self.nb_of_turns, ConcentrateChar.concentration_rate)
        self.initiator.nb_of_concentrate += 1
        self.end_update([], 0, 1, True)
        return True

    def execute(self):
        self.initiator.feelings[self.feeling].concentrate_energy_update(self.action, 
            self.concentration_ratio * min(1.0, ConcentrateChar.deconcentration_rate / self.initiator.nb_of_concentrate))
        self.nb_of_turns -= 1
        if self.nb_of_turns > 0:
            self.end_update([], 0, 1, True)
        return True

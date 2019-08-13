import time as time
from sources.action.Actions import Actions


#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class RestChar:
    'Class to make a character rest'

    rest_config = ["Normal rest", 1, 1, 5]  # [Type, Rest coef, min_turn, max_turn]

    def __init__(self, fight, character, nb_of_turn):
        Actions.__init__(self, fight)
        self.character = character
        self.nb_of_turn = nb_of_turn
        self.is_a_success = self.start(automatic)

    def start(self, automatic):
        Actions.start(self)
        if not automatic:
            print("How much time do you want to rest?")
            txt = "--> Number of turns (0 = Cancel): "
            while 1:
                try:
                    self.nb_of_turn = int(input(txt))
                    if self.fight.cancel_action(self.nb_of_turn):
                        return False
                    elif self.nb_of_turn < RestChar.rest_config[2]:
                        print("You cannot rest less than", RestChar.rest_config[2], "turns")
                    elif self.nb_of_turn > RestChar.rest_config[3]:
                        print("You cannot rest more than", RestChar.rest_config[3], "turns")
                    else:
                        break
                except:
                    print("The input is not an integer")

            print("You have decided to rest", self.nb_of_turn, "turn(s)")
            time.sleep(3)

        self.character.spend_absolute_time(self.nb_of_turn)
        self.character.body.global_rest(RestChar.rest_config[1] * self.nb_of_turn)
        self.character.calculate_characteristic()
        return True

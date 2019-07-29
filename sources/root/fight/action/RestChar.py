import time as time
from sources.root.fight.action.Actions import Actions
from sources.root.character.Characters import Characters


#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class RestChar:
    'Class to make a character rest'
    
    time_ratio = 0.5 #Ratio when the action will occur
    rest_type = [["Normal rest", 1, 1], ["Deep rest", 2.5, 5]] #[Type, Rest coef, min_turn]
    

    def __init__(self, fight, character, default_type="None", automatic=False, nb_of_turn=0):
        Actions.__init__(self, fight)
        self.character = character
        self.type = default_type
        self.nb_of_turn = nb_of_turn
        self.is_a_success = self.start(automatic)
        
        
    def start(self, automatic):
        Actions.start(self)
        
        if not automatic:
            print("")
            print("Do you want to normal rest (NO) or to deep rest (DE)? (NO/DE)")
            while 1:
                read = input('--> NO/DE (0 = Cancel): ')
                print("")
                if self.fight.cancel_action(read):
                    return False
                elif read == "NO":
                    self.type = RestChar.rest_type[0]
                    break
                elif read == "DE":
                    if not self.character.weapons_use:
                        self.type = RestChar.rest_type[1]
                        break
                    else:
                        print("Cannot deep rest if weapons are equipped")
                        print("")
                else:
                    print("Rest type:", read, "is not recognized")
            
            print("How much time do you want to rest? (min", self.type[2], ")")
            txt = "--> Number of " + str(Characters.Rest[2]) + " turns (0 = Cancel): "
            while 1:
                try:
                    self.nb_of_turn = int(input(txt))
                    if self.fight.cancel_action(self.nb_of_turn):
                        return False
                    elif self.nb_of_turn < self.type[2]:
                        print("You cannot rest less than", self.type[2] * Characters.Rest[2], "turns")
                    else:
                        break
                except:
                    print("The input is not an integer")
            
            print("You have decided to rest", round(self.nb_of_turn * Characters.Rest[2], 1), "turn(s)")
            time.sleep(3)
        
        self.character.action_in_progress = self
        self.fight.scheduler.append(self)
        self.timeline = self.character.timeline + Characters.Rest[2] * RestChar.time_ratio
        self.character.spend_absolute_time(self.nb_of_turn * Characters.Rest[2])
        return True
    
        
    def result(self):
        Actions.result(self)
        
        self.character.body.global_rest(self.type[1] * Characters.Rest[2])
        self.character.calculate_characteristic()
        
        self.nb_of_turn -= 1
        if self.nb_of_turn > 0:
            self.fight.scheduler.append(self)
            self.timeline += Characters.Rest[2]
        return True
        
    
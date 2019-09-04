import random as random
import time as time
import sources.miscellaneous.configuration as cfg


#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class Actions:
    """Super class for all actions"""

    def __init__(self, fight):
        self.fight = fight
        self.is_a_success = False

    @staticmethod
    def cancel_action(read):
        try:
            read = int(read)
            if read == 0 or read == '0':
                print("Action cancelled!")
                time.sleep(1)
                return True
            return False
        except:
            return False


#############################################################
##################### ACTIVE ACTIONS CLASS ##################
#############################################################
class ActiveActions(Actions):
    """
    Super class for all real actions.
    For all new action, stop_action and get_ranged_action_ratio must be updated
    """

    def __init__(self, fight, initiator):
        super().__init__(fight)
        self.name = "Generic active actions"
        self.initiator = initiator
        self.timeline = self.initiator.timeline
        
    def end_update(self, chars_in_previous_attacks, stamina, time, absolute_time=False):
        for char in chars_in_previous_attacks:
            if (self.timeline, self) not in char.previous_attacks:  # In case already added by stop action
                char.previous_attacks.append((self.timeline, self))
                
        self.initiator.spend_stamina(stamina)
        if absolute_time:
            self.initiator.spend_absolute_time(time)
        else:
            self.initiator.spend_time(time)

    def get_attack_coef(self, char):
        return random.gauss(1, cfg.high_variance) \
             * char.get_fighting_availability(self.initiator.timeline)



#############################################################
######################## ACTIONS CLASS ######################
#############################################################
class Actions:
    """Super class for all actions"""

    def __init__(self, fight):
        self.fight = fight
        self.is_a_success = False


#############################################################
##################### ACTIVE ACTIONS CLASS ##################
#############################################################
class ActiveActions(Actions):
    """Super class for all real actions"""

    def __init__(self, fight, initiator):
        super().__init__(self, fight)
        self.initiator = initiator
        self.timeline = initiator.timeline

    def end(self, chars_in_previous_attacks, stamina, time, absolute_time=False):
        for char in chars_in_previous_attacks:
            if (self.timeline, self) not in char.previous_attacks:  # In case already added by stop action
                char.previous_attacks.append((self.timeline, self))
                
        self.initiator.spend_stamina(stamina)
        if absolute_time:
            self.initiator.spend_absolute_time(time)
        else:
            self.initiator.spend_time(time)
            
        self.initiator.calculate_characteristic()

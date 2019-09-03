import sources.miscellaneous.global_variables as global_variables
import random as random

# A turn is around 6 seconds
# Between each case, there are approximatively 2 meters
actions = {
    "pass_time": {
        "description": "Wait a little",
        "command": "PAS",
        "duration": 0.1,  # Not used, duration choose by the user
        "stamina": 0.0
    },
    "rest": {
        "description": "Rest a little",
        "command": "RES",
        "duration": 1.0,  # Not used, duration choose by the user
        "stamina": 0.0
    },
    "concentrate": {
        "description": "Concentrate on your mind and feelings",
        "command": "CON",
        "duration": 1.0,  # Not used, duration choose by the user
        "stamina": 1.5
    },
    "melee_attack": {
        "description": "Melee attack an enemy character",
        "command": "MAT",
        "duration": 0.5,
        "stamina": 1.0
    },
    "ranged_attack": {
        "description": "Ranged attack an enemy character",
        "command": "RAT",
        "duration": 0.5,
        "stamina": 0.75
    },
    "reload": {
        "description": "Reload your ranged weapon",
        "command": "REL",
        "duration":  0.0,  # Not used, reload time is defined by the equipment
        "stamina": 0.1
    },
    "move": {
        "description": "Move to an adjacent case",
        "command": "MOV",
        "duration": 0.15,  # Normal run is around 2.7 meters --> around 1 case per second
        "stamina": 0.1
    },
    "modify_equip": {
        "description": "Equip / Unequip weapons",
        "command": "EQP",
        "duration": 0.5,
        "stamina": 0.1
    },
    "spell": {
        "description": "Cast a spell",
        "command": "SPL",
        "duration": 0.0,  # Not used, different for each spell
        "stamina": 0.0  # Not used, different for each spell
    },
    "information": {
        "description": "Information on a character state",
        "command": "INF",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    },
    "save": {
        "description": "Save the current game state",
        "command": "SAV",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    },
    "load": {
        "description": "Load a previous game state",
        "command": "LOA",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    }
}


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
        return random.gauss(1, global_variables.high_variance) \
             * char.get_fighting_availability(self.initiator.timeline)

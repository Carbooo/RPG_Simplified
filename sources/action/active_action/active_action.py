import random as random
from sources.action.action import Actions
from sources.miscellaneous import configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
##################### ACTIVE ACTIONS CLASS ##################
#############################################################
class ActiveActions(Actions):
    """
    Super class for all real actions.
    For all new action, stop_action, fighting_availability and get_ranged_action_ratio must be updated
    """

    def __init__(self, fight, initiator):
        super().__init__(fight)
        self.name = "Generic active actions"
        self.type = "Generic active actions"
        self.initiator = initiator
        self.timeline = self.initiator.timeline
        self.start_timeline = self.initiator.timeline  # To use the right timeline for get fight availability
    
    def start(self):
        return self.is_action_not_restricted()
    
    def end_update(self, stamina, time, absolute_time=False):
        self.initiator.spend_stamina(stamina)
        if absolute_time:
            self.initiator.spend_absolute_time(time)
        else:
            self.initiator.spend_time(time)

    def get_attack_coef(self, char, end_timeline):
        return random.gauss(cfg.mean, cfg.high_variance) * \
               char.get_fighting_availability(self.start_timeline, end_timeline, self)

    def is_action_not_restricted(self):
        if self.initiator.charged_spell:
            if self.type not in ["Waiting", "Move"]:
                func.optional_print("With a charged spell, you can only wait, move or cast the spell!", level=2)
                func.optional_sleep(2)
                return False

        elif self.initiator.equipments.get_loaded_bow():
            if self.type not in ["Waiting", "Move", "RangedAttack"]:
                func.optional_print("With a loaded bow, you can only wait, move or shoot your arrow!", level=2)
                func.optional_sleep(2)
                return False

        return True

    def stop_action(self, char, timeline):
        # Set stop action chances
        if self.type == "MeleeAttack":
            cancel_probability = cfg.melee_attack_fighting_availability
        elif self.type == "RangedAttack":
            cancel_probability = cfg.ranged_attack_fighting_availability
        elif self.type == "Spell":
            cancel_probability = cfg.magic_attack_fighting_availability
        else:
            func.optional_print("Error: Type not found for stop action function")
            return False
        
        # Cancel stuff that has been prepared
        cancelled = random.random() < cancel_probability
        if cancelled:
            char.equipments.loose_reloaded_bow_ammo()
            if char.charged_spell:
                func.optional_print("The attack makes you loose the spell you have previously charged!", level=3)
                func.optional_sleep(2)
                char.charged_spell = None

        # Cancel current actions
        if not char.last_action or char.last_action.type == "MeleeAttack":
            # Cannot stop these actions
            pass
        elif char.last_action.type == "Waiting":
            # This action is always stopped and has no penalty
            func.optional_print("You stop passing time because of the attack", level=2)
            func.optional_sleep(2)
            char.last_action = None
            char.timeline = timeline
        else:
            # Potentially cancel other actions
            cancel_probability *= (char.timeline - timeline) / (char.timeline - char.last_action.start_timeline)
            cancelled = random.random() < cancel_probability
        
            if char.last_action.type != "Move":
                # Penalty for standard actions (excepting move)
                func.optional_print("The attack surprises you and your defense is diminished!", level=2)
                func.optional_sleep(2)
                
            if cancelled:
                func.optional_print("Your current action (", char.last_action.name, ") is canceled by the attack!",
                                    level=3)
                func.optional_sleep(2)
                
                if char.last_action.type == "Reload":
                        func.optional_print("Furthermore, you loose the ammo being used for reloading!", level=3)
                        func.optional_sleep(2)
                        char.equipments.ammo.remove(char.last_action.ammo_to_load)
                
                char.last_action = None
                char.timeline = timeline
                char.spend_time(cfg.surprise_delay)

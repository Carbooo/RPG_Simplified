import math as math
import time as time
from sources.action.active_action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
######################## JOY SPELL CLASS ####################
#############################################################
class JoySpells(Spells):
    """Class to cast joy spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Joy", spell_code)
        self.name = "Casting a Joy spell"
        self.spell_stamina = cfg.joy_spells_stamina[self.spell_code]
        self.spell_time = cfg.joy_spells_time[self.spell_code]
        self.spell_energy = cfg.joy_spells_energy[self.spell_code]
        self.spell_hands = cfg.joy_spells_hands[self.spell_code]
        self.spell_knowledge = cfg.joy_spells_knowledge[self.spell_code]
        self.spell_power = cfg.joy_spells_power[self.spell_code]
        self.is_a_success = self.start()
        
    def start(self):
        super().start()
        if self.spell_code == "EGY":
            return self.start_energize()
        elif self.spell_code == "LGT":
            return self.start_light()
        else:
            return False
    
    def execute(self):
        super().execute()
        if self.spell_code == "EGY":
            return self.energize()
        elif self.spell_code == "LGT":
            return self.throw_light()
        else:
            return False
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "EGY":
            return self.end_energize(is_canceled)
        else:
            return False
    
    def start_energize(self):
        if not self.is_able_to_cast():
            return False
        
        func.optional_print("You have decided to energize yourselves, improving your overall stats and restoring stamina.")
        func.optional_print("The effect will start soon!")
        time.sleep(3)
            
        self.target = self.initiator
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def energize(self):
        self.print_spell("has improve all their attributes", "executing", True)
        self.remove_identical_active_spell()

        self.magical_coef *= self.initiator.magic_power_ratio
        self.target.body.udpate(self.spell_power["stamina_restored"] * self.magical_coef)
        self.target.update_morale(
            (math.pow(self.spell_power["moral_increase"], self.magical_coef) - 1)
            * self.target.original_morale
        )
        self.target.calculate_characteristic()

        self.add_lasting_spell("All attributes slightly increased",
                              self.spell_power["duration"] * math.sqrt(self.magical_coef))
        return True
    
    def end_energize(self, is_canceled):
        if not is_canceled:
            self.print_spell("has no longer improved attributes", "ending", True)

        self.target.update_morale(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_morale
        )
        self.target.calculate_characteristic()
        
        self.end_lasting_spell()
        return True
        
    def start_light(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(True, False, False):
            return False
        
        func.optional_print("You have decided to send a burning light")
        func.optional_print("The light is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_light(self):
        if not self.rechoose_target_if_necessary(True, False, False):
            return False

        self.print_spell("is sending a burning light to", "executing", False)

        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
        result = self.magical_attack_received(
            attack_value,
            False,  # is_localized
            True,  # can_use_shield
            self.spell_power["resis_dim_rate"], 
            self.spell_power["pen_rate"]
        )
        
        if self.target.body.is_alive() and result >= self.spell_power["min_damage_for_delay"]:
            func.optional_print("This light attack blinds you and delay your next step!")
            time.sleep(2)
            self.target.spend_time(self.spell_power["delay"])

        return True

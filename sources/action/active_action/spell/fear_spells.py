import math as math
import time as time
from sources.action.active_action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
######################## JOY SPELL CLASS ####################
#############################################################
class FearSpells(Spells):
    """Class to cast fear spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, spell_code)
        self.name = "Casting a Fear spell"
        self.feeling_type = "Fear"
        self.spell_stamina = cfg.joy_spells_stamina[self.spell_code]
        self.spell_time = cfg.joy_spells_time[self.spell_code]
        self.spell_energy = cfg.joy_spells_energy[self.spell_code]
        self.spell_hands = cfg.joy_spells_hands[self.spell_code]
        self.spell_knowledge = cfg.joy_spells_knowledge[self.spell_code]
        self.spell_power = cfg.joy_spells_power[self.spell_code]
        self.shield = None
        self.is_a_success = self.start()
        
    def start(self):
        super().start()
        if self.spell_code == "OWI":
            return self.start_opposing_winds()
        elif self.spell_code == "MFI":
            return self.start_gigantic_fist()
        else:
            return False
    
    def execute(self):
        super().execute()
        if self.spell_code == "OWI":
            return self.opposing_winds()
        elif self.spell_code == "MFI":
            return self.gigantic_fist()
        else:
            return False
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "OWI":
            return self.end_opposing_winds(is_canceled)
        else:
            return False
    
    def start_opposing_winds(self):
        if not self.is_able_to_cast():
            return False
        
        func.optional_print("You have decided to generate strong winds around you, making you harder to reach.")
        func.optional_print("The effect will start soon!")
        time.sleep(3)
            
        self.target = self.initiator
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def opposing_winds(self):
        self.print_spell("has generating strong winds around themselves", "executing", True)
        self.remove_identical_active_spell()

        self.magical_coef *= self.initiator.magic_power_ratio
        self.initiator.equipments.set_magical_shield("Opposing winds shield", 
                                                     self.spell_power["defense"], 0.0, 
                                                     self.spell_power["melee_def_ratio"], 
                                                     1.0, 0.0)

        self.add_lasting_spell("Opposing winds",
                              self.spell_power["duration"] * math.sqrt(self.magical_coef))
        return True
    
    def end_opposing_winds(self, is_canceled):
        if not is_canceled:
            self.print_spell("has no longer strong winds protecting them against attacks", "ending", True)

        self.initiator.equipments.remove_weapon(self.shield, definitive=True)
        
        self.end_lasting_spell()
        return True
        
    def start_gigantic_fist(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(True, False, False):
            return False
        
        func.optional_print("You have decided to throw a gigantic magic fist")
        func.optional_print("The fist is forming...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def gigantic_fist(self):
        if not self.rechoose_target_if_necessary(True, False, False):
            return False

        self.print_spell("is sending a gigantic magic fist to", "executing", False)

        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
        result = self.magical_attack_received(
            attack_value,
            False,  # is_localized
            False,  # can_use_shield
            self.spell_power["resis_dim_rate"], 
            self.spell_power["pen_rate"]
        )
        
        if self.spell_power["min_damage_for_moving"]:
            func.optional_print("The powerful impact with the magic fist moves you few cases back!")
            time.sleep(2)
            # to be done
            
        return True

import math as math
import time as time
from sources.action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg

#############################################################
####################### WRATH SPELL CLASS ###################
#############################################################

class WrathSpells(Spells):
    """Class to cast wrath spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Wrath", spell_code)
        self.name = "Casting a Wrath spell"
        self.spell_stamina = cfg.wrath_spells_stamina[self.spell_code]
        self.spell_time = cfg.wrath_spells_time[self.spell_code]
        self.spell_energy = cfg.wrath_spells_energy[self.spell_code]
        self.spell_hands = cfg.wrath_spells_hands[self.spell_code]
        self.spell_power = cfg.wrath_spells_power[self.spell_code]
        self.is_a_success = self.start()
        
    def start(self):
        if self.spell_code == "STR":
            return self.start_improve_strength()
        elif self.spell_code == "FBL":
            return self.start_fireball()
        else:
            return False
    
    def execute(self):
        if self.spell_code == "STR":
            return self.improve_strength()
        elif self.spell_code == "FBL":
            return self.throw_fireball()
        else:
            return False
    
    def end(self, is_canceled=False):
        if self.spell_code == "STR":
            return self.end_improve_strength(is_canceled)
        else:
            return False
    
    def start_improve_strength(self):
        if not self.is_able_to_cast():
            return False
        
        print("You have decided to improve your strength.")
        print("The effect will start soon!")
        time.sleep(3)
            
        self.target = self.initiator
        self.set_magical_coef() 
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def improve_strength(self):
        self.print_spell("has greatly improve their strength", "executing", True)

        self.remove_identical_active_spell()
        self.magical_coef *= self.initiator.magic_power_ratio
        
        self.target.update_force(
            (math.pow(self.spell_power["force"], self.magical_coef) - 1)
            * self.target.original_force
        )
        self.target.update_reflex(
            (math.pow(self.spell_power["reflex"], self.magical_coef) - 1)
            * self.target.original_reflex
        )
        self.target.update_dexterity(
            (math.pow(self.spell_power["dexterity"], self.magical_coef) - 1)
            * self.target.original_dexterity
        )
        self.target.calculate_characteristic()

        self.add_lasting_spell("Strength greatly increased", 
                              self.spell_power["duration"] * math.sqrt(self.magical_coef))
        return True
    
    def end_improve_strength(self, is_canceled):
        if not is_canceled:
            self.print_spell("has no longer an improved strength", "ending", True)
        
        self.target.update_force(
            (1 - math.pow(self.spell_power["force"], self.magical_coef))
            * self.target.original_force
        )
        self.target.update_reflex(
            (1 - math.pow(self.spell_power["reflex"], self.magical_coef))
            * self.target.original_reflex
        )
        self.target.update_dexterity(
            (1 - math.pow(self.spell_power["dexterity"], self.magical_coef))
            * self.target.original_dexterity
        )
        self.target.calculate_characteristic()
        
        self.end_lasting_spell()
        return True
        
    def start_fireball(self):
        if not self.is_able_to_cast():
            return False
        
        print("You have decided to throw a fireball")
        print("The fireball is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_fireball(self):
        self.print_spell("has a fireball ready and needs to choose a target", "choosing", True)
        target = self.choose_pos_target()
        if not target:
            print("Spell cancelled, the magic and stamina spent is lost")
            return False

        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
        for char, distance_ratio in self.get_all_spread_targets(
                self.spell_power["spread_distance"] * self.magical_coef,
                target["abscissa"], target["ordinate"]
        ):
            self.target = char
            self.print_spell("is sending a fireball to", "executing", False)
            self.magical_attack_received(
                attack_value * distance_ratio,
                False,  # is_localized
                True,  # can_use_shield
                self.spell_power["resis_dim_rate"], 
                self.spell_power["pen_rate"]
            )
            
        return True

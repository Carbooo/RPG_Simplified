import math as math
import time as time
from sources.action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg

#############################################################
####################### SADNESS SPELL CLASS ###################
#############################################################

class SadnessSpells(Spells):
    """Class to cast sadness spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Sadness", spell_code)
        self.name = "Casting a Sadness spell"
        self.spell_stamina = cfg.sadness_spells_stamina[self.spell_code]
        self.spell_time = cfg.sadness_spells_time[self.spell_code]
        self.spell_energy = cfg.sadness_spells_energy[self.spell_code]
        self.spell_hands = cfg.sadness_spells_hands[self.spell_code]
        self.spell_power = cfg.sadness_spells_power[self.spell_code]
        self.is_a_success = self.start()
        
    def start(self):
        super().start()
        if self.spell_code == "IPK":
            return self.start_ice_pick()
        elif self.spell_code == "DST":
            return self.start_despair_storm()
        else:
            return False
    
    def execute(self):
        super().execute()
        if self.spell_code == "IPK":
            return self.throw_ice_pick()
        elif self.spell_code == "DST":
            return self.throw_despair_storm()
        else:
            return False
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "DST":
            return self.end_despair_storm(is_canceled)
        else:
            return False
    
    def start_ice_pick(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(True, False, False):
            return False
        
        print("You have decided to send a ice pick")
        print("The ice is forming...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_ice_pick(self):
        if not self.rechoose_target_if_necessary(True, False, False):
            return False

        self.print_spell("is sending an ice pick to", "executing", False)

        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
        result = self.magical_attack_received(
            attack_value,
            True,  # is_localized
            True,  # can_use_shield
            self.spell_power["resis_dim_rate"], 
            self.spell_power["pen_rate"]
        )
        
        return True
    
    def start_despair_storm(self):
        if not self.is_able_to_cast():
            return False
        
        print("You have decided to throw a fireball")
        print("The fireball is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_despair_storm(self):
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
        
    def end_despair_storm(self, is_canceled):
        if is_canceled:
            self.target.equipments.remove_armor(self.spell_power["armor"])
            self.end_lasting_spell()
            return True
        
        if self.spell_power["armor"].is_broken():
            # Armor is already removed
            self.end_lasting_spell()
            return True
            
        is_depleted = self.target.equipments.decay_magical_armor(self.spell_power["armor"], self.spell_power["turn_decay"])
        if is_depleted:
            self.print_spell("has no longer a magic love shield", "ending", False)
            self.target.equipments.remove_armor(self.spell_power["armor"])
            self.end_lasting_spell()
        else:
            self.timeline += 1
        return True

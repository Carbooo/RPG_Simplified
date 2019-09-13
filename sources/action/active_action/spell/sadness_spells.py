import math as math
import time as time
from sources.action.active_action.spell.spells import Spells
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
        self.target_abs = -1
        self.target_ord = -1
        self.nb_of_turns = -1
        self.affected_targets = {}
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
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
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
        
        print("You have decided to cast a despair ice storm")
        print("The storm is forming...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_despair_storm(self):
        self.print_spell("has a despair storm ready and needs to choose a target", "choosing", True)
        target = self.choose_pos_target()
        if not target:
            print("Spell cancelled, the magic and stamina spent is lost")
            return False

        self.target_abs = target["abscissa"]
        self.target_ord = target["ordinate"]
        self.magical_coef *= self.initiator.magic_power_ratio
        self.nb_of_turns = int(round(self.spell_power["duration"] * self.magical_coef))
        self.apply_despair_storm()
        self.fight.field.active_spells.append(self)
        self.add_lasting_spell("Despair storm", cfg.recurrent_spell_frequency, False)
        return True
        
    def apply_despair_storm(self):
        current_targets = {}
        for char, distance_ratio in self.get_all_spread_targets(
                self.spell_power["spread_distance"] * self.magical_coef,
                self.target_abs, self.target_ord
        ):
            self.target = char
            self.print_spell("'s despair storm diminishes", "executing", False)
            coef = math.sqrt(distance_ratio) * self.magical_coef
            char.update_morale(- self.spell_power["moral_dim_rate"] * coef)
            char.spend_stamina(self.spell_power["stamina_dim_rate"] * coef)
            current_targets[char] = coef
            if char not in self.affected_targets:
                char.coef_speed_ratio -= self.spell_power["speed_dim_rate"] * coef
                self.affected_targets[char] = coef
                char.active_spells.append(self)

        # Increase speed back to normal when char left the storm
        for char in self.affected_targets:
            if char not in current_targets:
                char.coef_speed_ratio += self.spell_power["speed_dim_rate"] * self.affected_targets[char]
                char.active_spells.remove(self)

        self.affected_targets = current_targets

    def end_despair_storm(self, is_canceled):
        self.nb_of_turns -= 1
        if self.nb_of_turns == 0:
            self.fight.field.active_spells.remove(self)
            self.end_lasting_spell(False)
            for char in self.affected_targets:
                char.active_spells.remove(self)
        else:
            self.apply_despair_storm()
            self.timeline += 1
        return True

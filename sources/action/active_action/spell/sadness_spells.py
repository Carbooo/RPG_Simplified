import math as math
from sources.action.active_action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
####################### SADNESS SPELL CLASS ###################
#############################################################
class SadnessSpells(Spells):
    """Class to cast sadness spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, spell_code)
        self.name = "Casting a Sadness spell"
        self.feeling_type = "Sadness"
        self.spell_stamina = cfg.sadness_spells_stamina[self.spell_code]
        self.spell_time = cfg.sadness_spells_time[self.spell_code]
        self.spell_energy = cfg.sadness_spells_energy[self.spell_code]
        self.spell_hands = cfg.sadness_spells_hands[self.spell_code]
        self.spell_knowledge = cfg.sadness_spells_knowledge[self.spell_code]
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

    def cast(self):
        super().cast()
        success = False
        if self.spell_code == "IPK":
            success = self.choose_ice_pick_target()
            if success:
                func.optional_print("You have decided to throw an ice pick now.")
        elif self.spell_code == "DST":
            success = self.choose_despair_storm_target()
            if success:
                func.optional_print("You have decided to activate a despair ice storm now.")

        if success:
            self.end_update(cfg.actions["cast_spell"]["stamina"], cfg.actions["cast_spell"]["duration"])
            func.optional_print("The spell is being cast!")
            func.optional_sleep(3)
        return success

    def execute(self):
        super().execute()
        success = False
        if self.spell_code == "IPK":
            success = self.ice_pick()
        elif self.spell_code == "DST":
            success = self.despair_storm()

        if success:
            self.initiator.charged_spell = None
        return success
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "DST":
            return self.end_despair_storm()
        else:
            return False
    
    def start_ice_pick(self):
        if not self.is_able_to_cast():
            return False
        
        func.optional_print("You have decided to send a ice pick")
        func.optional_print("The ice is forming...")
        func.optional_sleep(3)
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   

    def choose_ice_pick_target(self):
        self.print_spell("has an ice pick ready and needs to choose a target", "choosing", True)
        if not self.choose_target(True, False, False):
            func.optional_print("Casting cancelled, the spell remains charged")
            return False
        return True

    def ice_pick(self):
        if not self.is_target_still_reachable(False, False):
            return False

        self.print_spell("is sending an ice pick to", "executing", False)
        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
        self.magical_attack_received(
            attack_value,
            True,  # is_localized
            True,  # can_use_shield
            self.spell_power["life_rate"],
            self.spell_power["ignoring_armor_rate"],
            self.spell_power["pen_rate"],
            self.spell_power["resis_dim_rate"]
        )
        return True
    
    def start_despair_storm(self):
        if not self.is_able_to_cast():
            return False
        
        func.optional_print("You have decided to cast a despair ice storm")
        func.optional_print("The storm is forming...")
        func.optional_sleep(3)
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   

    def choose_despair_storm_target(self):
        self.print_spell("has a despair storm ready and needs to choose a target", "choosing", True)
        if not self.choose_pos_target(is_obstacle_free=True):
            func.optional_print("Casting cancelled, the spell remains charged")
            return False
        return True

    def despair_storm(self):
        if not self.is_target_still_reachable(False, True):
            return False

        self.target_abs = self.target["abscissa"]
        self.target_ord = self.target["ordinate"]
        self.magical_coef *= self.initiator.magic_power_ratio
        self.nb_of_turns = int(round(self.spell_power["duration"] * self.magical_coef))
        self.print_spell("'s despair storm is now activated", "executing", False)
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
            self.print_spell("'s despair storm diminishes", "affecting", False)
            coef = math.sqrt(distance_ratio) * self.magical_coef
            char.update_morale(- self.spell_power["morale_dim_rate"] * coef)
            char.spend_stamina(self.spell_power["stamina_dim_rate"] * coef)
            current_targets[char] = coef
            if char not in self.affected_targets:
                char.coef_speed_ratio -= self.spell_power["speed_dim_rate"] * coef
                char.active_spells.append(self)

        for char in self.affected_targets:
            char.coef_speed_ratio += self.spell_power["speed_dim_rate"] * self.affected_targets[char]
            if char not in current_targets:
                char.active_spells.remove(self)
            else:
                char.coef_speed_ratio -= self.spell_power["speed_dim_rate"] * current_targets[char]

        self.affected_targets = current_targets

    def end_despair_storm(self):
        self.nb_of_turns -= 1
        if self.nb_of_turns == 0:
            self.print_spell("'s despair storm is over", "ending", False)
            self.fight.field.active_spells.remove(self)
            self.end_lasting_spell(False)
            for char in self.affected_targets:
                char.active_spells.remove(self)
                char.coef_speed_ratio += self.spell_power["speed_dim_rate"] * self.affected_targets[char]
        else:
            self.apply_despair_storm()
            self.timeline += 1
        return True

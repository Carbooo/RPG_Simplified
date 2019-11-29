import math as math
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
        if not super().start():
            return False
        if self.spell_code == "OWI":
            return self.start_opposing_winds()
        elif self.spell_code == "GFI":
            return self.start_gigantic_fist()
        else:
            return False

    def cast(self):
        super().cast()
        success = False
        if self.spell_code == "OWI":
            success = True
            func.optional_print("You have decided to activate powerful winds around you.")
        elif self.spell_code == "GFI":
            success = self.choose_gigantic_fist_target()
            if success:
                func.optional_print("You have decided to throw a gigantic magic fist now.")

        if success:
            self.end_update(cfg.actions["cast_spell"]["stamina"], cfg.actions["cast_spell"]["duration"])
            func.optional_print("The spell is being cast!")
            func.optional_sleep(3)
        return success

    def execute(self):
        super().execute()
        success = False
        if self.spell_code == "OWI":
            success = self.opposing_winds()
        elif self.spell_code == "GFI":
            success = self.gigantic_fist()

        if success:
            self.initiator.charged_spell = None
        return success
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "OWI":
            return self.end_opposing_winds(is_canceled)
        else:
            return False
    
    def start_opposing_winds(self):
        if not self.is_able_to_cast():
            return False
        
        func.optional_print("You have decided to generate powerful winds around you, making you harder to reach.")
        func.optional_print("The effect will start soon!")
        func.optional_sleep(3)
            
        self.target = self.initiator
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def opposing_winds(self):
        self.print_spell("has generating powerful winds around themselves", "executing", True)
        self.remove_identical_active_spell()

        self.magical_coef *= math.sqrt(self.initiator.magic_power_ratio)
        self.initiator.equipments.set_magical_shield("Opposing winds shield", 
                                                     self.spell_power["defense"], 0.0, 
                                                     self.spell_power["melee_def_ratio"], 
                                                     1.0, 0.0)

        self.add_lasting_spell("Opposing winds",
                              self.spell_power["duration"] * math.sqrt(self.magical_coef))
        return True
    
    def end_opposing_winds(self, is_canceled):
        if not is_canceled:
            self.print_spell("has no longer powerful winds protecting them against attacks", "ending", True)

        self.initiator.equipments.remove_weapon(self.shield, definitive=True)
        
        self.end_lasting_spell()
        return True
        
    def start_gigantic_fist(self):
        if not self.is_able_to_cast():
            return False

        func.optional_print("You have decided to throw a gigantic magic fist")
        func.optional_print("The fist is forming...")
        func.optional_sleep(3)
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True

    def choose_gigantic_fist_target(self):
        self.print_spell("has a gigantic fist ready and needs to choose a target", "choosing", True)
        if not self.choose_target(True, False, False):
            func.optional_print("Casting cancelled, the spell remains charged")
            return False
        return True

    def gigantic_fist(self):
        if not self.is_target_still_reachable(False, False):
            return False

        self.print_spell("is sending a gigantic magic fist to", "executing", False)
        attack_value = self.spell_power["attack_value"] * self.magical_coef + self.initiator.magic_power
        result = self.magical_attack_received(
            attack_value,
            False,  # is_localized
            False,  # can_use_shield
            self.spell_power["life_rate"],
            self.spell_power["ignoring_armor_rate"],
            self.spell_power["pen_rate"],
            self.spell_power["resis_dim_rate"]
        )
        
        func.optional_print("The powerful impact of the magic fist moves you back!")
        func.optional_sleep(2)
        knockback = self.fight.field.get_next_possible_pos_from_max_distance(
                    self.initiator, self.target, 
                    round(result / self.spell_power["moving_back_ratio"]))
        self.fight.field.move_character(self.target, knockback["new_abscissa"], knockback["new_ordinate"])
        
        if knockback["obstacle_reached"]:
            func.optional_print("During your fall back, you hit an obstacle and get extra damages!")
            func.optional_sleep(2)
            self.target.body.loose_life(result / self.spell_power["obstacle_hit_ratio"])
            
        elif knockback["other_char"] is not None:
            func.optional_print("During your fall back, you hit", skip_line=True)
            knockback["other_char"].print_basic()
            func.optional_print("", "Both of you are delayed by the impact!")
            func.optional_sleep(2)
            self.stop_action(knockback["other_char"], self.initiator.timeline)
            knockback["other_char"].spend_time(result / self.spell_power["char_hit_ratio"])
            self.target.spend_time(result)
            
        return True

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
    
    def end(self):
        if self.spell_code == "STR":
            return self.end_improve_strength()
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
        self.remove_identical_active_spell(self.initiator)
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

        self.add_active_spell(self.initiator, self.spell_power["duration"] * math.sqrt(self.magical_coef),
                              "Strength greatly increased")
        self.initiator.last_action = None  # To remove it from the scheduler
        return True
    
    def end_improve_strength(self):
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
        return True
        
    def start_fireball(self):
        if not self.is_able_to_cast(2):
            return False
        
        self.target = self.choose_enemy_target()
        if not self.target:
            return False
        
        print("You have decided to throw a fireball")
        print("The fireball is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_fireball(self):
        if not self.fight.field.is_target_magically_reachable(self.initiator, self.target):
            print("Your initial target is no longer reachable!")
            print("Please choose a new one or cancel the attack.")
            self.target = self.choose_enemy_target()
            if not self.target:
                return False
    
        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
                     
        for char, distance_ratio in self.get_all_spread_targets(
                self.spell_power["spread_distance"] * self.magical_coef
        ):
            print("")
            print("*********************************************************************")
            self.initiator.print_basic()
            print("is sending a fireball to (", end=' ')
            char.print_basic()
            print(")")
            print("*********************************************************************")
            print("")
            time.sleep(3)

            self.magical_attack_received(
                char,
                attack_value * distance_ratio,
                self.fight.field.get_magical_accuracy(self.initiator, char),
                False,  # is_localized
                True,  # can_use_shield
                self.spell_power["resis_dim_rate"], 
                self.spell_power["pen_rate"]
            )

        self.initiator.last_action = None  # To remove it from the scheduler
        return True

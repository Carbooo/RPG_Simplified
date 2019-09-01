import math as math
import time as time
from sources.action.spell.Spells import Spells
import sources.miscellaneous.global_variables as global_variables

#############################################################
####################### WRATH SPELL CLASS ###################
#############################################################

class WrathSpells(Spells):
    """Class to cast wrath spells"""
    
    spells_energy = {
        "STR" : 10.0,
        "FBL" : 30.0
    }
    spells_time = {
        "STR" : 1.0,
        "FBL" : 2.5
    }
    spells_stamina = {
        "STR" : 1.0,
        "FBL" : 7.5
    }
    spells_power = {
        "STR" : {
            "force" : 2.0,
            "reflex" : 0.8,
            "dexterity" : 0.6,
            "duration" : 5.0
        },
        "FBL" : {
            "attack_value" : 50.0,
            "spread_distance" : 1,
            "resis_dim_rate" : 0.5,
            "pen_rate" : 0.25
        }
    }
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Wrath", spell_code)
        self.spell_stamina = WrathSpells.spells_stamina[self.spell_code]
        self.spell_time = WrathSpells.spells_time[self.spell_code]
        self.spell_energy = WrathSpells.spells_energy[self.spell_code]
        self.spell_power = WrathSpells.spells_power[self.spell_code]
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
        coef = self.magical_coef * self.initiator.magic_power_ratio
        
        self.diff_force = self.target.force
        print(math.pow(self.spell_power["force"], coef))
        self.target.force *= math.pow(self.spell_power["force"], coef)
        self.diff_force -= self.target.force
        
        self.diff_reflex = self.target.reflex
        self.target.reflex *= math.pow(self.spell_power["reflex"], coef)
        self.diff_reflex -= self.target.reflex
        
        self.diff_dexterity = self.target.dexterity
        self.target.dexterity *= math.pow(self.spell_power["dexterity"], coef)
        self.diff_dexterity -= self.target.dexterity
        
        self.add_active_spell(self.initiator, self.spell_power["duration"] * math.sqrt(coef))
        self.initiator.last_action = None  # To remove it from the scheduler
        return True
    
    def end_improve_strength(self):
        self.target.force += self.diff_force
        self.target.reflex += self.diff_reflex
        self.target.dexterity += self.diff_dexterity
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
            self.magical_attack_received(
                attack_value * distance_ratio,
                self.fight.field.get_magical_accuracy(self.initiator, char),
                False,  # is_localized
                True,  # can_use_shield
                self.spell_power["resis_dim_rate"], 
                self.spell_power["pen_rate"]
            )

        self.initiator.last_action = None  # To remove it from the scheduler
        return True


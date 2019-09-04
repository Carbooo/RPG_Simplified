import math as math
import time as time
from sources.action.spell.spells import Spells
import sources.miscellaneous.global_variables as global_variables

#############################################################
####################### JOY SPELL CLASS ###################
#############################################################

class JoySpells(Spells):
    """Class to cast joy spells"""
    
    spells_energy = {
        "EGY": 10.0,
        "LGT": 20.0
    }
    spells_time = {
        "EGY": 1.0,
        "LGT": 1.75
    }
    spells_stamina = {
        "EGY": 1.0,
        "LGT": 3.0
    }
    spells_power = {
        "EGY": {
            "coef": 1.2,
            "duration": 5.0
        },
        "LGT": {
            "attack_value": 20.0,
            "resis_dim_rate": 0.33,
            "pen_rate": 0.1,
            "delay": 1.5
        }
    }
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Joy", spell_code)
        self.name = "Casting a Joy spell"
        self.spell_stamina = JoySpells.spells_stamina[self.spell_code]
        self.spell_time = JoySpells.spells_time[self.spell_code]
        self.spell_energy = JoySpells.spells_energy[self.spell_code]
        self.spell_power = JoySpells.spells_power[self.spell_code]
        self.is_a_success = self.start()
        
    def start(self):
        if self.spell_code == "EGY":
            return self.start_energize()
        elif self.spell_code == "LGT":
            return self.start_light()
        else:
            return False
    
    def execute(self):
        if self.spell_code == "EGY":
            return self.energize()
        elif self.spell_code == "LGT":
            return self.throw_light()
        else:
            return False
    
    def end(self):
        if self.spell_code == "EGY":
            return self.end_energize()
        else:
            return False
    
    def start_energize(self):
        if not self.is_able_to_cast():
            return False
        
        print("You have decided to energize yourselves, improving your overall stats.")
        print("The effect will start soon!")
        time.sleep(3)
            
        self.target = self.initiator
        self.set_magical_coef() 
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def energize(self):
        self.remove_identical_active_spell(self.initiator)
        self.magical_coef *= self.initiator.magic_power_ratio

        self.target.update_constitution(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_constitution
        )
        self.target.update_force(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_force
        )
        self.target.update_agility(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_agility
        )
        self.target.update_dexterity(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_dexterity
        )
        self.target.update_reflex(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_reflex
        )
        self.target.update_willpower(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_willpower
        )
        self.target.update_spirit(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_spirit
        )
        self.target.update_morale(
            (math.pow(self.spell_power["coef"], self.magical_coef) - 1)
            * self.target.original_morale
        )
        self.target.calculate_characteristic()

        self.add_active_spell(self.initiator, self.spell_power["duration"] * math.sqrt(self.magical_coef))
        self.initiator.last_action = None  # To remove it from the scheduler
        return True
    
    def end_energize(self):
        self.target.update_constitution(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_constitution
        )
        self.target.update_force(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_force
        )
        self.target.update_agility(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_agility
        )
        self.target.update_dexterity(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_dexterity
        )
        self.target.update_reflex(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_reflex
        )
        self.target.update_willpower(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_willpower
        )
        self.target.update_spirit(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_spirit
        )
        self.target.update_morale(
            (1 - math.pow(self.spell_power["coef"], self.magical_coef))
            * self.target.original_morale
        )
        self.target.calculate_characteristic()
        return True
        
    def start_light(self):
        if not self.is_able_to_cast(1):
            return False
        
        self.target = self.choose_enemy_target()
        if not self.target:
            return False
        
        print("You have decided to send a burning light")
        print("The light is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_light(self):
        if not self.fight.field.is_target_magically_reachable(self.initiator, self.target):
            print("Your initial target is no longer reachable!")
            print("Please choose a new one or cancel the attack.")
            self.target = self.choose_enemy_target()
            if not self.target:
                return False
    
        attack_value = (self.spell_power["attack_value"] + self.initiator.magic_power) * self.magical_coef
                     
        print("")
        print("*********************************************************************")
        self.initiator.print_basic()
        print("is sending a fireball to (", end=' ')
        self.target.print_basic()
        print(")")
        print("*********************************************************************")
        print("")

        self.magical_attack_received(
            self.target,
            attack_value * distance_ratio,
            self.fight.field.get_magical_accuracy(self.initiator, self.target),
            False,  # is_localized
            True,  # can_use_shield
            self.spell_power["resis_dim_rate"], 
            self.spell_power["pen_rate"]
        )

        self.initiator.last_action = None  # To remove it from the scheduler
        return True


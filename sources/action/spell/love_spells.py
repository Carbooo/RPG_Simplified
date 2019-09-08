import math as math
import time as time
from sources.action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg


#############################################################
######################## JOY SPELL CLASS ####################
#############################################################
class LoveSpells(Spells):
    """Class to cast love spells"""
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator, "Love", spell_code)
        self.name = "Casting a Love spell"
        self.spell_stamina = cfg.love_spells_stamina[self.spell_code]
        self.spell_time = cfg.love_spells_time[self.spell_code]
        self.spell_energy = cfg.love_spells_energy[self.spell_code]
        self.spell_hands = cfg.love_spells_hands[self.spell_code]
        self.spell_power = cfg.love_spells_power[self.spell_code]
        self.is_a_success = self.start()
        
    def start(self):
        if self.spell_code == "SHD":
            return self.start_shield()
        elif self.spell_code == "HEA":
            return self.start_heal()
        else:
            return False
    
    def execute(self):
        if self.spell_code == "SHD":
            return self.shield()
        elif self.spell_code == "HEA":
            return self.throw_heal()
        else:
            return False
    
    def end(self):
        if self.spell_code == "SHD":
            return self.end_shield()
        else:
            return False
    
    def start_shield(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(False, True, False):
            return False
            
        print("You have decided to set up a shield, protecting your target against damages.")
        print("The shield will be set up soon!")
        time.sleep(3)
        
        self.set_magical_coef() 
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def shield(self):
        if not self.rechoose_target_if_necessary(False, True, False):
            return False

        self.print_spell("has set up a magic shield on", "executing", False)
                
        self.remove_identical_active_spell()
        self.magical_coef *= self.initiator.magic_power_ratio
        self.spell_power["defense"] *= self.magical_coef

        self.add_active_spell(1.0, "Magic shield")
        self.initiator.last_action = None  # To remove it from the scheduler
        return True
    
    def end_shield(self):
        self.print_spell("has no longer a magic shield", "ending", False)

        self.spell_power["defense"] -= self.spell_power["turn_decay"]
        if self.spell_power["defense"] > 0:
            self.add_active_spell(1.0, "Protecting shield")
        return True
        
    def start_heal(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(False, True, False):
            return False
        
        print("You have decided to heal an ally")
        print("The heal is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update([], self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_heal(self):
        if not self.rechoose_target_if_necessary(False, True, False):
            return False

        self.print_spell("is going to heal", "executing", False)

        self.magical_coef *= self.initiator.magic_power_ratio
        self.target.body.update_life(self.spell_power["heal"] * self.magical_coef)

        self.initiator.last_action = None  # To remove it from the scheduler
        return True

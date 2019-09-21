import time as time
from sources.action.active_action.spell.spells import Spells
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
####################### LOVE SPELL CLASS ####################
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
        self.spell_knowledge = cfg.love_spells_knowledge[self.spell_code]
        self.spell_power = cfg.love_spells_power[self.spell_code]
        self.armor = None
        self.is_a_success = self.start()
        
    def start(self):
        super().start()
        if self.spell_code == "SHD":
            return self.start_shield()
        elif self.spell_code == "HEA":
            return self.start_heal()
        else:
            return False
    
    def execute(self):
        super().execute()
        if self.spell_code == "SHD":
            return self.shield()
        elif self.spell_code == "HEA":
            return self.throw_heal()
        else:
            return False
    
    def end(self, is_canceled=False):
        super().end(is_canceled)
        if self.spell_code == "SHD":
            return self.end_shield(is_canceled)
        else:
            return False
    
    def start_shield(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(False, True, False):
            return False
            
        func.optional_print("You have decided to set up a shield, protecting your target against damages.")
        func.optional_print("The shield will be set up soon!")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True
        
    def shield(self):
        if not self.rechoose_target_if_necessary(False, True, False):
            return False

        self.print_spell("has set up a magic shield on", "executing", False)
                
        self.remove_identical_active_spell()
        self.magical_coef *= self.initiator.magic_power_ratio
        self.armor = self.target.equipments.set_magical_armor("Love shield", self.spell_power["resistance"] * self.magical_coef)
        
        self.add_lasting_spell("Magic love shield", cfg.recurrent_spell_frequency)
        return True
    
    def end_shield(self, is_canceled):
        if is_canceled:
            self.target.equipments.remove_armor(self.armor)
            self.end_lasting_spell()
            return True
        
        if self.armor.is_broken():
            # Armor is already removed
            self.end_lasting_spell()
            return True
            
        is_depleted = self.target.equipments.decay_magical_armor(self.armor, self.spell_power["turn_decay"])
        if is_depleted:
            self.print_spell("has no longer a magic love shield", "ending", False)
            self.end_lasting_spell()
        else:
            self.timeline += 1
        return True
        
    def start_heal(self):
        if not self.is_able_to_cast():
            return False

        if not self.choose_target(False, True, False):
            return False
        
        func.optional_print("You have decided to heal an ally")
        func.optional_print("The heal is charging...")
        time.sleep(3)
        
        self.set_magical_coef()
        self.end_update(self.get_stamina_with_coef(), self.get_time_with_coef())
        return True   
    
    def throw_heal(self):
        if not self.rechoose_target_if_necessary(False, True, False):
            return False

        self.print_spell("is going to heal", "executing", False)

        self.magical_coef *= self.initiator.magic_power_ratio
        self.target.body.update_life(self.spell_power["heal"] * self.magical_coef)
        return True

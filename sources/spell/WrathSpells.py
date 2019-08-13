from sources.spell.Spells import Spells

#############################################################
####################### WRATH SPELL CLASS ###################
#############################################################

class WrathSpells:
    """Class to cast wrath spells"""
 
    def __init__(self, fight, caster, target, type, energy, spell_id):
        Spells.__init__(self, fight, caster, target, type, energy, spell_id)
        
    def start(self):
        if self.spell_id == "STR":
            return self.improve_strength()
        elif self.spell_id == "FBL":
            return self.fireball()
        else:
            return False
    
    def execute(self):
        if self.spell_id == "STR":
            return self.end_improve_strength()
        else:
            return False
            
    def improve_strength(self):
        self.target.force *= 2 * self.caster.magic_power_ratio
        self.target.reflex *= 0.8 * self.caster.magic_power_ratio
        self.target.dexterity *= 0.6 * self.caster.magic_power_ratio
        self.target.calculate_characteristic()
        self.timeline = self.caster.timeline + 5 * self.caster.magic_power_ratio
        self.fight.scheduler.append(self)
        return True
    
    def end_improve_strength(self):
        self.target.force /= 2 * self.caster.magic_power_ratio
        self.target.reflex /= 0.8 * self.caster.magic_power_ratio
        self.target.dexterity /= 0.6 * self.caster.magic_power_ratio
        self.target.calculate_characteristic()
        return True
        
    def fireball(self):
        attack_power = 50 * self.caster.magic_power / self.target.magic_defense
        self.target.magic_attack_received(attack_power, resistance_dim_rate, penetration_rate):
        return True

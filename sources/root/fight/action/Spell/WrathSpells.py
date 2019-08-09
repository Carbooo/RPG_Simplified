from sources.root.fight.action.spell.Spells import Spells


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
        else:
            return False
    
    def improve_strength(self):
        self.target.force *= 1.5
        return True
        
    def fireball(self):
        self.target.
        return True
        
        
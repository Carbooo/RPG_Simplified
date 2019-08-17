from sources.action.Actions import Actions

#############################################################
######################### SPELL CLASS #######################
#############################################################
class Spells:
    """Super class for all spells"""

    def __init__(self, fight, caster, type, energy, spell_code):
        Actions.__init__(self, fight)
        self.caster = caster
        self.target = None
        self.type = type
        self.energy = energy
        self.spell_code = spell_code
        
    def start(self):
        return Actions.start()

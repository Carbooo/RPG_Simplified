from sources.action.Actions import Actions

#############################################################
######################### SPELL CLASS #######################
#############################################################
class Spells:
    """Super class for all spells"""

    def __init__(self, fight, caster, target, type, energy, spell_id):
        Actions.__init__(self, fight)
        self.caster = caster
        self.target = target
        self.type = type
        self.energy = energy
        self.spell_id = spell_id
        
    def start(self):
        return Actions.start()

from sources.spell.Spells import Spells

#############################################################
####################### WRATH SPELL CLASS ###################
#############################################################

class WrathSpells:
    """Class to cast wrath spells"""
 
    def __init__(self, fight, caster, energy, spell_code):
        Spells.__init__(self, fight, caster, "wrath", energy, spell_code)
        
    def start(self):
        if self.spell_code == "STR":
            return self.improve_strength()
        elif self.spell_code == "FBL":
            return self.fireball()
        else:
            return False
    
    def execute(self):
        if self.spell_code == "STR":
            return self.end_improve_strength()
        else:
            return False
            
    def improve_strength(self):
        self.target = self.caster
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
        if self.fight.belong_to_team(self.caster) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1
        
        print("--------- ATTACKER -----------")
        self.caster.print_attack_state()
        print("")
        print("--------- TARGETS -----------")
        print("Choose one of the following enemies:")
        enemy_list = []
        for char in team.characters_list:
            if self.fight.field.is_target_magically_reachable(self.caster, char):
                enemy_list.append(char)
                char.print_state()
        
        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if self.fight.cancel_action(read):
                    return False
                    
                for enemy in enemy_list:
                    if enemy.get_id() == read:
                        self.target = enemy
                        self.target.magical_damage_received(self.caster, 50, 0.5, True, 0.5, 0.25)
                        return True
                        
                print("ID:", read, "is not available")
                        
            except:
                print("The input is not an ID")
                continue

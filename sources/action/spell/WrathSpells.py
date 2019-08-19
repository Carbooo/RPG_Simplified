from sources.spell.Spells import Spells
import sources.miscellaneous.global_variables as global_variables

#############################################################
####################### WRATH SPELL CLASS ###################
#############################################################

class WrathSpells(Spells):
    """Class to cast wrath spells"""
    
    spells_energy = [
        "STR" : 10.0,
        "FBL" : 30.0
    ]
    spells_time = [
        "STR" : 1.0,
        "FBL" : 2.5
    ]
    spells_stamina = [
        "STR" : 1.0,
        "FBL" : 7.5
    ]
    spells_power = [
        "STR" : [
            "force" : 2.0,
            "reflex" : 0.8,
            "dexterity" : 0.6,
            "duration" : 5.0
        ],
        "FBL" : [
            "attack_value" : 50.0,
            "spread_distance" : 1,
            "resis_dim_rate" : 0.5,
            "pen_rate" : 0.25
        ]
    ]
 
    def __init__(self, fight, initiator, spell_code):
        super().__init__(self, fight, initiator, "wrath", spell_code)
        
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
        if not self.initiator.feelings["wrath"].check_energy(WrathSpells.spells_energy["STR"]):
            return False
            
        self.target = self.initiator
        coef = self.initiator.feelings["wrath"].use_energy(WrathSpells.spells_energy["STR"]) \
             * self.initiator.magic_power_ratio
        self.diff_force = self.target.force
        self.target.force *= WrathSpells.spells_power["STR"]["force"] * coef
        self.diff_force -= self.target.force
        self.diff_reflex = self.target.reflex
        self.target.reflex *= WrathSpells.spells_power["STR"]["reflex"] * coef
        self.diff_reflex -= self.target.reflex
        self.diff_dexterity = self.target.dexterity
        self.target.dexterity *= WrathSpells.spells_power["STR"]["dexterity"] * coef
        self.diff_dexterity -= self.target.dexterity
        self.timeline = self.initiator.timeline + WrathSpells.spells_power["STR"]["duration"] * coef
        self.fight.scheduler.append(self)
        self.end([], WrathSpells.spells_stamina["STR"], WrathSpells.spells_time["STR"])
        return True
    
    def end_improve_strength(self):
        self.target.force += self.diff_force
        self.target.reflex += self.diff_reflex
        self.target.dexterity += self.diff_dexterity
        self.target.calculate_characteristic()
        return True
        
    def fireball(self):
        if not self.initiator.feelings["wrath"].check_energy(WrathSpells.spells_energy["FBL"]):
            print("You don't have enough energy to cast this spell")
            return False
        
        if not self.initiator.check_stamina(WrathSpells.spells_stamina["FBL"]):
            print("You don't have enough stamina to cast this spell")
            return False
        
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1
        
        print("--------- ATTACKER -----------")
        self.initiator.print_attack_state()
        print("")
        print("--------- TARGETS -----------")
        print("Choose one of the following enemies:")
        enemy_list = []
        for char in team.characters_list:
            if self.fight.field.is_target_magically_reachable(self.initiator, char):
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
                        attack_value = (WrathSpells.spells_power["FBL"]["attack_value"] + self.initiator.magic_power) \
                                     * self.initiator.feelings["wrath"].use_energy(WrathSpells.spells_energy["FBL"])
                                     * random.gauss(1, global_variables.high_variance)
                                     
                        for char, distance_ratio in self.get_all_spread_targets(WrathSpells.spells_power["FBL"]["spread_distance"]):
                            self.magical_attack_received(
                                attack_value * distance_ratio,
                                self.fight.field.get_magical_accuracy(self.initiator, char),
                                False,  # is_localized
                                True,  # can_use_shield
                                WrathSpells.spells_power["FBL"]["resis_dim_rate"], 
                                WrathSpells.spells_power["FBL"]["pen_rate"]
                            )       
                                
                        self.end([], WrathSpells.spells_stamina["FBL"], WrathSpells.spells_time["FBL"])
                        return True
                        
                print("ID:", read, "is not available")
                        
            except:
                print("The input is not an ID")
                continue

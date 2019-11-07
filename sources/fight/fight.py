import copy as copy
import random as random
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.character.character import Character
from sources.action.get_char_information import GetCharInformation
from sources.action.active_action.modify_equipments import ModifyEquipments
from sources.action.active_action.melee_attack import MeleeAttack
from sources.action.active_action.move import Move
from sources.action.active_action.ranged_attack import RangedAttack
from sources.action.active_action.reload import Reload
from sources.action.active_action.pass_time import PassTime
from sources.action.active_action.rest import Rest
from sources.action.active_action.concentrate import Concentrate
from sources.action.save_and_load import Save, Load
from sources.action.active_action.spell.spells import Spells
from sources.action.active_action.spell.wrath_spells import WrathSpells
from sources.action.active_action.spell.joy_spells import JoySpells
from sources.action.active_action.spell.love_spells import LoveSpells
from sources.action.active_action.spell.sadness_spells import SadnessSpells
from sources.action.active_action.spell.fear_spells import FearSpells


#############################################################
##################### FIGHTS CLASS ##########################
#############################################################
class Fight:
    """Common base class for all fights"""
    
    def __init__(self, field, team1, team2):
        self.field = field
        self.team1 = team1
        self.team2 = team2
        
        self.nb_of_turn = 1
        self.timeline = 1
        self.current_timeline = 0
        self.last_timeline = 0
        self.speed_ratio_save = []
        self.char_order = []
        self.scheduler = []
        self.set_initial_order()
        self.skip_saving = False
        
        if self.field.set_all_teams(team1,team2) is False:
            func.optional_print("(Fights) Cannot set team, fight cancelled")
        else:
            self.start()
    
    def belong_to_team(self, character):
        for char in self.team1.characters_list:
            if character == char:
                return self.team1
        return self.team2

################## SET FUNCTIONS ###########################
    def set_initial_order(self):
        char_list = []
        
        for char in self.team1.characters_list:
            char_list.append(char)

        for char in self.team2.characters_list:
            char_list.append(char)
  
        while len(char_list) > 0:
            char = char_list.pop(random.choice(range(len(char_list))))
            self.char_order.append(char)
            self.scheduler.append(char)
        
        self.scheduler.append(self)
                
    def start(self):
        while self.team1.is_life_active() and self.team2.is_life_active():
            # Set turn settings
            next_event = self.scheduler[0]
            self.last_timeline = self.current_timeline
            self.current_timeline = next_event.timeline
            self.begin_turn()
            
            # Automatic turn every 1 timeline
            if isinstance(next_event, Fight):
                self.pass_a_turn()
            
            # Terminate / Update active spell
            elif isinstance(next_event, Spells):
                next_event.end()

            # Result of a melee attack (no matter the current state of the attacker)
            elif isinstance(next_event, MeleeAttack):
                next_event.execute()
                
            elif isinstance(next_event, Character):
                func.current_char = next_event  # Used for automatic tests

                if isinstance(next_event.last_action, Move) \
                or isinstance(next_event.last_action, RangedAttack) \
                or (isinstance(next_event.last_action, Rest) and next_event.last_action.nb_of_turns > 0) \
                or (isinstance(next_event.last_action, Concentrate) and next_event.last_action.nb_of_turns > 0) \
                or isinstance(next_event.last_action, Reload) \
                or isinstance(next_event.last_action, ModifyEquipments) \
                or isinstance(next_event.last_action, Spells):
                    # Destination not reached, keep moving
                    # or
                    # Number of resting / concentrating turns not reached, continue it
                    # or
                    # Actually reload, modify equipments, or cast the charged spell
                    if not next_event.last_action.execute():
                        next_event.last_action = None  # Stop action if error encounter
                    
                elif next_event.body.is_shape_ko():
                    # Rest if too exhausted for any actions
                    self.print_ko_state_rest(next_event)
                    next_event.body.global_rest(1)
                    next_event.spend_absolute_time(1)
                    
                else:
                    #Turn possible actions
                    self.print_new_turn()
                    self.choose_actions(next_event)
                    self.nb_of_turn += 1 #Count only character turns
                
            else:
                func.optional_print("(Fights) Event:", next_event, "is not recognized", level=3)
                func.optional_print("The fight stops here", level=3)
                exit(0)
                
            self.end_turn()
        
        #Victory of a team
        if self.team1.is_life_active():
            func.optional_print("Team:", self.team1.name, " (ID:", self.team1.get_id(), ") has won the fight!", level=3)
            func.optional_sleep(3)
        else:
            func.optional_print("Team:", self.team2.name, " (", self.team2.get_id(), ") has won the fight!", level=3)
            func.optional_sleep(3)
            

################################## TURN FUNCTIONS ####################################
    def pass_a_turn(self):
        func.optional_print("")
        func.optional_print("*********************************************************************")
        func.optional_print("******************** A GAME TURN HAS PASSED *************************", level=2)
        func.optional_print("*********************************************************************")
        self.timeline += 1 
        func.optional_sleep(2)
        
        for char in self.char_order:
            if char.body.is_alive() and char.exceeded_feelings_check():
                self.field.remove_dead_char(char)
        
    def print_new_turn(self):
        func.optional_print("")
        func.optional_print("*********************************************************************")
        func.optional_print("************************ NEW CHAR TURN (" + str(self.nb_of_turn) + ") *************************")
        func.optional_print("*********************************************************************")
        
        # Print character team first, then enemy team
        if self.belong_to_team(self.scheduler[0]) == self.team1:
            func.optional_print("************************* ALL DEAD STATE ************************")
            self.team1.print_dead_states()
            self.team2.print_dead_states()
            func.optional_print("")
            func.optional_print("********************* CURRENT TEAM ALIVE STATE ******************")
            self.team1.print_alive_states()
            func.optional_print("")
            func.optional_print("******************** OPPONENT TEAM ALIVE STATE ******************")
            self.team2.print_alive_states()
        else:
            func.optional_print("************************* ALL DEAD STATE ************************")
            self.team2.print_dead_states()
            self.team1.print_dead_states()
            func.optional_print("")
            func.optional_print("********************* CURRENT TEAM ALIVE STATE ******************")
            self.team2.print_alive_states()
            func.optional_print("")
            func.optional_print("******************** OPPONENT TEAM ALIVE STATE ******************")
            self.team1.print_alive_states()
        
        func.optional_print("")
        func.optional_print("******************** CURRENT CHARACTER STATE ******************")
        self.scheduler[0].print_detailed_state()
        func.optional_print("")
        self.field.print_obj()
        func.optional_print("")
        self.scheduler[0].print_basic()
        func.optional_print(", Timeline:", round(self.scheduler[0].timeline, 2))
        func.optional_print("")
        
    def print_ko_state_rest(self, character):
        func.optional_print("")
        func.optional_print("*********************************************************************")
        character.print_basic()
        func.optional_print("stamina is too low and can only rest", level=2)
        func.optional_print("*********************************************************************")
        func.optional_print("")
        func.optional_sleep(3)
        
    def order_scheduler(self):
        scheduler_list = [self.scheduler[0]]
        for event in self.scheduler[1::]:
            if isinstance(event, Character) and not event.body.is_life_active():
                continue
            for j in range(len(scheduler_list)):
                if event.timeline < scheduler_list[j].timeline:
                    scheduler_list.insert(j, event)
                    break
                elif event.timeline == scheduler_list[j].timeline \
                and random.choice([0,1]) == 1:
                    # To be fair in case of equal timeline
                    scheduler_list.insert(j, event)
                    break                        
                elif j == len(scheduler_list) - 1:
                    scheduler_list.append(event)
        if isinstance(self.scheduler[0], Character) and not self.scheduler[0].body.is_life_active():
            # First event has not been tested
            scheduler_list.remove(self.scheduler[0])
        self.scheduler = scheduler_list
        
    def begin_turn(self):
        self.update_team_morale(self.team1)
        self.update_team_morale(self.team2)
        
        time_diff = self.current_timeline - self.last_timeline
        for char in self.char_order:
            if char.body.is_alive():
                char.body.turn_rest(time_diff)

                for type in char.feelings:
                    char.feelings[type].natural_energy_update(time_diff)

                previous_attacks = copy.copy(char.previous_attacks)
                for attack_timeline, attack in previous_attacks:
                    if self.current_timeline >= attack_timeline + cfg.defense_time / char.speed_ratio:
                        char.previous_attacks.remove((attack_timeline, attack))

            self.field.remove_dead_char(char)

    def update_team_morale(self, team):
        total_ratio = 0
        for char in team.characters_list:
            if not char.is_a_zombie:
                total_ratio += char.body.get_global_ratio()
       
        total_ratio /= len(team.characters_list)
        
        for char in team.characters_list:
            char.team_state = total_ratio
                  
    def end_turn(self):
        self.order_scheduler()

        #Automatic saves
        if self.skip_saving:
            self.skip_saving = False
        else:
            Save.copy_all_to_next()
            Save(self, "AutoSave1")

#################### CHOOSE ACTIONS ########################
    def choose_actions(self, character):
        while 1:
            func.optional_print("")
            func.optional_print("Choose one of the following action:")
            
            for key in cfg.actions:
                func.optional_print("-", cfg.actions[key]["description"], "(", cfg.actions[key]["command"], ")")
            
            read = func.optional_input('--> ACT: ')
            
            if read == cfg.actions["pass_time"]["command"]:
                if self.pass_action(character):
                    break
            
            elif read == cfg.actions["rest"]["command"]:
                if self.rest_action(character):
                    break

            elif read == cfg.actions["concentrate"]["command"]:
                if self.concentrate_action(character):
                    break

            elif read == cfg.actions["melee_attack"]["command"]:
                if self.melee_attack_action(character):
                    break
            
            elif read == cfg.actions["ranged_attack"]["command"]:
                if self.ranged_attack_action(character):
                    break
            
            elif read == cfg.actions["reload"]["command"]:
                if self.reload_action(character):
                    break
            
            elif read == cfg.actions["move"]["command"]:
                if self.move_action(character):
                    break
            
            elif read == cfg.actions["modify_equip"]["command"]:
                if self.equip_action(character):
                    break

            elif read == cfg.actions["spell"]["command"]:
                if self.initiate_spell_object(character):
                    break

            elif read == cfg.actions["information"]["command"]:
                self.information_action(character)
            
            elif read == cfg.actions["save"]["command"]:
                self.save_action(character)
            
            elif read == cfg.actions["load"]["command"]:
                self.load_action(character)
            else:
                func.optional_print("Action:", read, "is not recognized")

    def pass_action(self, character):
        action = PassTime(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True

    def rest_action(self, character):
        action = Rest(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def melee_attack_action(self, character):
        action = MeleeAttack(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
        
    def ranged_attack_action(self, character):
        action = RangedAttack(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
        
    def reload_action(self, character):
        action = Reload(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def move_action(self, character):
        action = Move(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
                        
    def equip_action(self, character):     
        func.optional_print("You have decided to modify your equipment")
        action = ModifyEquipments(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def information_action(self, character):
        func.optional_print("You have decided to look for information")
        action = GetCharInformation(self)
        if not action.is_a_success:
            return False
        return True

    def save_action(self, character):
        func.optional_print("You have decided to save the current game state")
        action = Save(self)
        if not action.is_a_success:
            return False
        self.skip_saving = True
        return True
    
    def load_action(self, character):
        func.optional_print("You have decided to load a previous game state")
        action = Load(self)
        if not action.is_a_success:
            return False
        self.skip_saving = True
        return True
    
    def concentrate_action(self, character):
        action = Concentrate(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def initiate_spell_object(self, character):
        choice = Spells.choose_spell()
        if not choice:
            return False
        else:
            spell_type, spell_code = choice

        if spell_type == "WRA":
            action = WrathSpells(self, character, spell_code)
        elif spell_type == "JOY":
            action = JoySpells(self, character, spell_code)
        elif spell_type == "LOV":
            action = LoveSpells(self, character, spell_code)
        elif spell_type == "SAD":
            action = SadnessSpells(self, character, spell_code)
        elif spell_type == "FEA":
            action = FearSpells(self, character, spell_code)

        if not action.is_a_success:
            return False
        character.last_action = action
        return True

    def stop_action(self, char, timeline):
        # Loose reloaded bow ammo no matter last action
        char.equipments.loose_reloaded_bow_ammo()
            
        # Stop action without penalty
        if isinstance(char.last_action, Move) or isinstance(char.last_action, PassTime):
            func.optional_print("Your current action (", char.last_action.name, ") is canceled by the attack!", level=2)
            func.optional_sleep(2)
            char.last_action = None
            char.timeline = timeline
            return False
        
        # Stop action with penalty
        elif isinstance(char.last_action, ModifyEquipments) \
                or isinstance(char.last_action, Reload) \
                or isinstance(char.last_action, RangedAttack) \
                or isinstance(char.last_action, Rest) \
                or isinstance(char.last_action, Concentrate) \
                or isinstance(char.last_action, Spells):
            
            func.optional_print("The attack surprises you during your current action(",
                                char.last_action.name, ")!", level=2)
            func.optional_print("Your defense is diminished!", level=2)
            func.optional_sleep(2)
            func.optional_print("Your current action is also canceled!", level=2)
            func.optional_sleep(2)
            
            if isinstance(char.last_action, Reload):
                func.optional_print("You loose the ammo being used for reloading!", level=2)
                func.optional_sleep(2)
                char.equipments.ammo.remove(char.last_action.ammo_to_load)
            
            char.last_action = None  # Has to be done after the unreload
            char.timeline = timeline
            char.spend_time(cfg.defense_time)
            return True

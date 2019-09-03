import copy as copy
import random as random
import time as time
import sources.miscellaneous.global_variables as global_variables
from sources.action.actions import actions
from sources.character.character import Character
from sources.action.get_char_information import GetCharInformation
from sources.action.modify_equipments import ModifyEquipments
from sources.action.melee_attack import MeleeAttack
from sources.action.move import Move
from sources.action.ranged_attack import RangedAttack
from sources.action.reload import Reload
from sources.action.pass_time import PassTime
from sources.action.rest import Rest
from sources.action.concentrate import Concentrate
from sources.action.save_and_load import Save, Load
from sources.action.spell.spells import Spells
from sources.action.spell.wrath_spells import WrathSpells


#############################################################
##################### FIGHTS CLASS ##########################
#############################################################
class Fight:
    """Common base class for all fights"""
    list = []    
    
    def __init__(self, field, team1, team2):
        Fight.list.append(self)
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
        self.automatic_mode = False
        
        if self.field.set_all_teams(team1,team2) is False:
            print("(Fights) Cannot set team, fight cancelled")
            Fight.list.pop(len(Character.list) - 1)
        else:
            self.start()
    
    def get_id(self):
        for i in range(len(Character.list)):
            if Fight.list[i] == self:
                return i
    
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
            self.time_effect_on_all()
            
            # Automatic turn every 1 timeline
            if isinstance(next_event, Fight):
                self.pass_a_turn()
            
            # Terminate active spell
            elif isinstance(next_event, Spells):
                next_event.end_active_spell()
                
            elif isinstance(next_event, Character):
                if (isinstance(next_event.last_action, Move) and next_event.last_action.path) \
                or (isinstance(next_event.last_action, Rest) and next_event.last_action.nb_of_turns > 0) \
                or (isinstance(next_event.last_action, Concentrate) and next_event.last_action.nb_of_turns > 0) \
                or isinstance(next_event.last_action, Reload) \
                or isinstance(next_event.last_action, Spells):
                    # Destination not reached, keep moving
                    # or
                    # Number of resting / concentrating turns not reached, continue it
                    # or
                    # Actually reload their range weapon
                    # or
                    # Actually cast the charged spell
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
                print("(Fights) Event:", next_event, "is not recognized")
                print("The fight stops here")
                exit(0)
                
            self.end_turn()
        
        #Victory of a team
        if self.team1.is_life_active():
            print("Team:", self.team1.name, " (ID:", self.team1.get_id(), ") has won the fight!")
            time.sleep(3)
        else:
            print("Team:", self.team2.name, " (", self.team2.get_id(), ") has won the fight!")
            time.sleep(3)
            

################################## TURN FUNCTIONS ####################################
    def pass_a_turn(self):
        print("")
        print("*********************************************************************")
        print("******************** A GAME TURN HAS PASSED *************************")
        print("*********************************************************************")
        self.timeline += 1 
        time.sleep(3)
        
        for char in self.char_order:
            if char.exceeded_feelings_check():
                self.field.remove_dead_char(char)
        
    def print_new_turn(self):
        print("")
        print("*********************************************************************")
        print("************************ NEW CHAR TURN (" + str(self.nb_of_turn) + ") *************************")
        print("*********************************************************************")
        
        # Print character team first, then enemy team
        if self.belong_to_team(self.scheduler[0]) == self.team1:
            print("************************* ALL DEAD STATE ************************")
            self.team1.print_dead_states()
            self.team2.print_dead_states()
            print("")
            print("********************* CURRENT TEAM ALIVE STATE ******************")                          
            self.team1.print_alive_states()
            print("")
            print("******************** OPPONENT TEAM ALIVE STATE ******************")
            self.team2.print_alive_states()
        else:
            print("************************* ALL DEAD STATE ************************")
            self.team2.print_dead_states()
            self.team1.print_dead_states()
            print("")
            print("********************* CURRENT TEAM ALIVE STATE ******************")                          
            self.team2.print_alive_states()
            print("")
            print("******************** OPPONENT TEAM ALIVE STATE ******************")
            self.team1.print_alive_states()
        
        print("")
        print("******************** CURRENT CHARACTER STATE ******************")
        self.scheduler[0].print_detailed_state()
        print("")
        self.field.print_obj()
        
    def print_ko_state_rest(self, character):
        print("")
        print("*********************************************************************")
        character.print_basic()
        print("stamina is too low and can only rest")
        print("New state:")
        character.print_state()
        print("*********************************************************************")
        print("")
        time.sleep(3)
        
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
                    #To be fair in case of equal timeline
                    scheduler_list.insert(j, event)
                    break                        
                elif j == len(scheduler_list) - 1:
                    scheduler_list.append(event)
        if isinstance(self.scheduler[0], Character) and not self.scheduler[0].body.is_life_active():
            #First event has not been tested
            scheduler_list.remove(self.scheduler[0])
        self.scheduler = scheduler_list
        
    def time_effect_on_all(self):
        time_diff = self.current_timeline - self.last_timeline
        for char in self.char_order:
            char.body.turn_rest(time_diff)
            self.field.remove_dead_char(char)
            
            for type in char.feelings:
                char.feelings[type].natural_energy_update(time_diff)
            
            previous_attacks = copy.copy(char.previous_attacks)
            for attack_timeline, attack in previous_attacks:
                if self.current_timeline >= attack_timeline + global_variables.defense_time / char.speed_ratio:
                    char.previous_attacks.remove((attack_timeline, attack))
                    
    def end_turn(self):
        self.order_scheduler()

        #Automatic saves
        Save(self, "AutoSave1")
        if self.nb_of_turn % 3 == 0:
            Save(self, "AutoSave3")
        if self.nb_of_turn % 5 == 0:
            Save(self, "AutoSave5")    

#################### CHOOSE ACTIONS ########################
    def choose_actions(self, character):
        while 1:
            print("")
            print("Choose one of the following action:")
            
            for key in actions:
                print("-", actions[key]["description"], "(", actions[key]["command"], ")")
            
            read = input('--> ACT: ')
            
            if read == actions["pass_time"]["command"]:
                if self.pass_action(character):
                    break
            
            elif read == actions["rest"]["command"]:
                if self.rest_action(character):
                    break

            elif read == actions["concentrate"]["command"]:
                if self.concentrate_action(character):
                    break

            elif read == actions["melee_attack"]["command"]:
                if self.melee_attack_action(character):
                    break
            
            elif read == actions["ranged_attack"]["command"]:
                if self.ranged_attack_action(character):
                    break
            
            elif read == actions["reload"]["command"]:
                if self.reload_action(character):
                    break
            
            elif read == actions["move"]["command"]:
                if self.move_action(character):
                    break
            
            elif read == actions["modify_equip"]["command"]:
                if self.equip_action(character):
                    break

            elif read == actions["spell"]["command"]:
                if self.choose_spell(character):
                    break

            elif read == actions["information"]["command"]:
                self.information_action(character)
            
            elif read == actions["save"]["command"]:
                self.save_action(character)
            
            elif read == actions["load"]["command"]:
                self.load_action(character)
            else:
                print("Action:", read, "is not recognized")

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
        print("You have decided to modify your equipment")
        action = ModifyEquipments(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def information_action(self, character):
        print("You have decided to look for information")
        action = GetCharInformation(self)
        if not action.is_a_success:
            return False
        return True

    def save_action(self, character):
        print("You have decided to save the current game state")
        action = Save(self)
        if not action.is_a_success:
            return False
        return True
    
    def load_action(self, character):
        print("You have decided to load a previous game state")
        action = Load(self)
        if not action.is_a_success:
            return False
        return True
    
    def concentrate_action(self, character):
        action = Concentrate(self, character)
        if not action.is_a_success:
            return False
        character.last_action = action
        return True
    
    def choose_spell(self, character):
        print("You have decided to cast a spell")
        print("Which type of spell?")
        for spell_type in Character.spells:
            print("-", spell_type["description"], "(" + spell_type["code"] + ")")
        
        while 1:
            read = input('--> Spell type (0 for cancel) : ')
            if self.cancel_action(read):
                return False
            
            for spell_type in Character.spells:
                if read == spell_type["code"]:
                    print("You chose to cast a " + spell_type["description"])
                    print("Which spell do you want to cast?")
                    
                    for spell in spell_type["list"]:
                        print("- ", spell["description"] + " (" + spell["code"] + ")")
        
                    while 1:
                        read = input('--> Spell (0 for cancel) : ')
                        if self.cancel_action(read):
                            return False
                        
                        for spell in spell_type["list"]:
                            if read == spell["code"]:
                                action = self.initiate_spell_object(character, spell_type["code"], spell["code"])
                                if not action.is_a_success:
                                    return False
                                character.last_action = action
                                return True
                            
                        print("Spell:", read, "is not recognized")
                    
            print("Spell type:", read, "is not recognized")
    
    def initiate_spell_object(self, caster, spell_type_code, spell_code):
        if spell_type_code == "WRA":
            return WrathSpells(self, caster, spell_code)
    
    def cancel_action(self, read):
        try:
            read = int(read)
            if read == 0 or read == '0':
                print("Action cancelled!")
                time.sleep(1)
                return True
            return False            
        except:
            return False

    def stop_action(self, char, timeline):
        if isinstance(char.last_action, ModifyEquipments) \
                or isinstance(char.last_action, Reload) \
                or isinstance(char.last_action, Rest) \
                or isinstance(char.last_action, Concentrate) \
                or isinstance(char.last_action, Spells):
            char.previous_attacks.append((timeline, char.last_action))
            print("The attack surprises you during your current action(", char.last_action.name, ")!")
            print("Your defense is diminished!")

            if isinstance(char.last_action, Reload) \
                    or isinstance(char.last_action, Rest) \
                    or isinstance(char.last_action, Concentrate) \
                    or isinstance(char.last_action, Spells):
                print("Your current action is canceled!")
                char.last_action = None
                char.timeline = timeline
                char.spend_time(global_variables.defense_time / 2)

            if isinstance(char.last_action, Reload):
                print("You loose the ammo used for reloading!")
                char.ammo.remove(char.last_action.ammo_to_load)

        if char.equipments.loose_reloaded_ammo():
            print("Your bow has lost its loaded arrow!")

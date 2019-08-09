import copy as copy
import random as random
import time as time
from sources.character.Characters import Characters, NoneCharacter
from sources.action.GetCharInformation import GetCharInformation
from sources.action.EquipChar import EquipChar
from sources.action.MeleeAttackChar import MeleeAttackChar
from sources.action.MoveChar import MoveChar
from sources.action.RangedAttackChar import RangedAttackChar
from sources.action.ReloadChar import ReloadChar
from sources.action.RestChar import RestChar
from sources.action.SaveAndLoad import Save, Load


#############################################################
##################### FIGHTS CLASS ##########################
#############################################################
class Fights:
    'Common base class for all fights'
    list = []    
    
    def __init__(self, field, team1, team2):
        Fights.list.append(self)
        self.field = field
        self.team1 = team1.copy()
        self.team2 = team2.copy()
        
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
            Fights.list.pop(len(Characters.list) - 1)
        else:
            self.start()
    
    
    def get_id(self):
        for i in range(len(Characters.list)):
            if Fights.list[i] == self:
                return i   


################## SET FUNCTIONS ###########################
    def set_initial_order(self):
        char_list = []
        
        for char in self.team1.characters_list:
            char_list.append(char)

        for char in self.team2.characters_list:
            char_list.append(char)
  
        while len(char_list) > 0:
            char = char_list.pop(random.choice(range(len(char_list))))
            char.current_action = Characters.Pass #Default char action
            self.char_order.append(char)
            self.scheduler.append(char)
        
        self.scheduler.append(self)
                
                
    def start(self):
        while self.team1.is_life_active() and self.team2.is_life_active():
            #Set turn settings
            next_event = self.scheduler[0]
            self.save_all_speed()
            self.current_timeline = next_event.timeline
            self.time_effect_on_all()
            self.reset_all()
            self.last_timeline = self.current_timeline
            
            #Automatic turn every 1 timeline
            if isinstance(next_event, Fights):
                self.pass_aturn()
                self.end_turn()
                continue
            
            #Execute pending action
            if isinstance(next_event, MeleeAttackChar) or isinstance(next_event, RangedAttackChar) \
            or isinstance(next_event, MoveChar) or isinstance(next_event, ReloadChar) or isinstance(next_event, EquipChar) \
            or isinstance(next_event, RestChar):
                next_event.result()
                self.end_turn()
                continue
            
            if isinstance(next_event, Characters):                
                #Spend the rest of unconscious time if the fighting has just ended
                if next_event.unconsciousness > 0:
                    next_event.current_action = Characters.NoAction
                    next_event.spend_absolute_time(next_event.unconsciousness)
                    self.print_unconscious_turn(next_event)
                    self.end_turn()
                    continue
                
                #Rest if too exhausted for any actions
                if next_event.is_shape_k_o():
                    next_event.current_action = Characters.Rest
                    #Rest, automatically, on deep rest mode with the minimum rest turn possible
                    RestChar(self, next_event, RestChar.rest_type[1], True, RestChar.rest_type[1][2])
                    self.print_k_o_state_rest(next_event)
                    self.end_turn()
                    continue
                
                #Start defending just after the current action ends
                defending_fight = self.char_wants_to_defend(next_event)
                if defending_fight:
                    next_event.current_action = Characters.Defending
                    next_event.timeline = defending_fight.attack_end_time
                    self.print_defending_turn(next_event)
                    self.end_turn()
                    continue
                
                #Turn possible actions
                self.print_new_turn()
                if next_event.is_moving() and next_event.action_in_progress:
                    next_event.action_in_progress.browse_current_path()
                else:
                    self.choose_actions(next_event)
                
                #Actions post-turn
                self.end_turn()
                self.nb_of_turn += 1 #Count only character turns
            
            else:
                print("(Fights) Event:", next_event, "is not recognized")
                print("The fight stops here")
                exit(0)
        
        #Victory of a team
        if self.team1.is_life_active():
            print("Team:", self.team1.name, " (ID:", \
                self.team1.get_id(), ") has won the fight!")
            time.sleep(3)
        else:
            print("Team:", self.team2.name, " (", \
                self.team2.get_id(), ") has won the fight!")
            time.sleep(3)
            

################################## TURN FUNCTIONS ####################################
    def pass_aturn(self):
        print("")
        print("*********************************************************************")
        print("******************** A GAME TURN HAS PASSED *************************")
        print("*********************************************************************")
        self.timeline += 1 
        time.sleep(3)    
    
    
    def print_new_turn(self):
        print("")
        print("*********************************************************************")
        print("************************ NEW CHAR TURN (" + str(self.nb_of_turn) + ") *************************")
        print("*********************************************************************")
        
        #Print character team first, then enemy team
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
        self.field.print_obj()
        print("")
        self.scheduler[0].print_state()
        self.scheduler[0].print_weapons_use()
    
    
    def print_unconscious_turn(self, character):
        print("")
        print("*********************************************************************")
        character.print_basic()
        print("is still unconscious / unready.")
        print("His turn has been delayed !")
        print("*********************************************************************")
        print("")
        time.sleep(5)
        
    
    def print_defending_turn(self, character):
        print("")
        print("*********************************************************************")
        character.print_basic()
        print("has finished his current action.")
        print("He will now start defending against the current melee attack")
        print("*********************************************************************")
        print("")
        time.sleep(5)
        
        
    def print_k_o_state_rest(self, character):
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
            if isinstance(event, Characters) and not event.is_life_active():
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
        if isinstance(self.scheduler[0], Characters) and not self.scheduler[0].is_life_active():
            #First event has not been tested
            scheduler_list.remove(self.scheduler[0])
        self.scheduler = scheduler_list
        
        
    def time_effect_on_all(self):
        for char in self.char_order:
            char.body.turn_rest(self.current_timeline - self.last_timeline)
            self.field.calculate_state(char)
    
    
    def end_turn(self):
        #Timelines and scheduling
        self.recalculate_all_timelines()
        copy_list = copy.copy(self.scheduler)
        for event in copy_list:
            if isinstance(event, Characters) and not event.is_active():
                self.remove_inactive_char_actions(event)
        self.order_scheduler()
        
        #Automatic saves
        Save(self, "AutoSave1")
        if self.nb_of_turn % 3 == 0:
            Save(self, "AutoSave3")
        if self.nb_of_turn % 5 == 0:
            Save(self, "AutoSave5")
        

################################## RESET FUNCTIONS ####################################
    def reset_all(self):
        time_spent = self.current_timeline - self.last_timeline
        for char in self.char_order:
            self.reset_reload(char)
            char.reset_current_melee_attacks(self.current_timeline)
            self.reset_unconsciousness(char, time_spent)
            char.calculate_characteristic()
        #print(self.scheduler)
    
    
    def reset_unconsciousness(self, character, time_spent):
        #Calculate unconscious time
        time_spent = min(character.unconsciousness, time_spent)
        character.unconsciousness -= time_spent
        
        #Add unconscious time to current melee attacks
        for att in character.current_melee_attacks:
            if att.timeline < self.current_timeline:
                continue
            elif att.defender == character:
                att.defense_handicap += time_spent
                att.defense_unconsciousness_period.append([self.last_timeline, \
                    min(self.current_timeline, self.last_timeline + character.unconsciousness)])
            else:
                att.attack_handicap += time_spent
                att.attack_unconsciousness_period.append([self.last_timeline, \
                    min(self.current_timeline, self.last_timeline + character.unconsciousness)])
        
        #Add unconscious time to delayed action
        self.delay_char_actions(character, time_spent)
        
        #Stat logs
        """  
        print("")
        print("name:", character.name)
        print("speed_run_level:", character.speed_run_level)
        print("timeline:", character.timeline)
        print("unconsciousness:", character.unconsciousness)
        for i in range(len(character.current_melee_attacks)):
            print("current_attack (", i, "):", end=' ')
            character.current_melee_attacks[i].defender.print_basic()
            print("---", character.current_melee_attacks[i].defense_handicap, "---", end=' ')
            character.current_melee_attacks[i].attacker.print_basic()
            print("---", character.current_melee_attacks[i].attack_handicap, "---", end=' ')
            print(character.current_melee_attacks[i].attack_begin_time)
        print("current_action:", character.current_action)
        """

    def delay_char_actions(self, character, delayed_time):
        if not isinstance(character.action_in_progress, MeleeAttackChar):
            character.spend_absolute_time(delayed_time)
            
        if isinstance(character.action_in_progress, RangedAttackChar) and \
        character.action_in_progress.timeline > self.current_timeline:
                character.action_in_progress.timeline += delayed_time
            
        elif isinstance(character.action_in_progress, MoveChar) and \
        character.action_in_progress.timeline > self.current_timeline:
            character.action_in_progress.timeline += delayed_time
                
            if isinstance(character.action_in_progress.linked_action, EquipChar):
                self.delay_equip_action(character.action_in_progress.linked_action, delayed_time)
            elif isinstance(character.action_in_progress.linked_action, ReloadChar):
                self.delay_reload_action(character.action_in_progress.linked_action, delayed_time)
                
        elif isinstance(character.action_in_progress, EquipChar):
            self.delay_equip_action(character.action_in_progress, delayed_time)
                
        elif isinstance(character.action_in_progress, ReloadChar):
            self.delay_reload_action(character.action_in_progress, delayed_time)    
    
    
    def delay_equip_action(self, event, delayed_time):
        if event.timeline > self.current_timeline:
            event.timeline += delayed_time
            event.equip_handicap += delayed_time
        else:
            event.after_equip_handicap += delayed_time
        event.end_time += delayed_time
        

    def delay_reload_action(self, event, delayed_time):
        if event.timeline > self.current_timeline:
            event.timeline += delayed_time
        event.end_time += delayed_time
                    
        
    def save_all_speed(self):
        self.speed_ratio_save = []
        for char in self.team1.characters_list:
            self.speed_ratio_save.append(char.speed_ratio)
        for char in self.team2.characters_list:
            self.speed_ratio_save.append(char.speed_ratio)
    
    
    def recalculate_all_timelines(self):
        #Use team lists to assure the same order with speed_save
        for char in self.team1.characters_list:
            self.recalculate_char_timelines(char, self.speed_ratio_save.pop(0))                
        for char in self.team2.characters_list:
            self.recalculate_char_timelines(char, self.speed_ratio_save.pop(0))
                
    
    def recalculate_char_timelines(self, character, old_speed_ratio):
        time_shift = (character.timeline - self.current_timeline) * (old_speed_ratio / character.speed_ratio - 1)
        self.delay_char_actions(character, time_shift)
        
    
    def reset_reload(self, character):
        if not (character.is_waiting() or character.current_action == Characters.Reload \
        or character.is_moving() or character.current_action == Characters.RangedAttack):
            if character.loose_reloaded_ammo():
                print("Character (", end=' ')
                character.print_basic()
                print(") due to its current action (", character.current_action[4], \
                      ") has lost its current ammo")
                return True
            return False
        
                    
################################## STOP FUNCTIONS ####################################    
    def stop_action(self, character):
        #Unload bows if they are reloaded
        if character.loose_reloaded_ammo():
            print("The attack has made (", end=' ')
            character.print_basic()
            print(") loose his reloaded bow ammo")

        #Inform the defender of the action stopped
        if character.current_action == Characters.Rest:
            print("The attack has stopped the rest of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(3)
            
        elif character.current_action == Characters.RangedAttack:
            print("The attack has stopped the ranged attack of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(3)
            try:
                self.scheduler.remove(character.action_in_progress)
            except:
                pass #Action already removed
                   
        elif character.current_action == Characters.Reload:
            print("The attack has stopped the reload of (", end=' ')
            character.print_basic()
            print(") and the ammo being reloaded has been lost")
            time.sleep(3)
            self.stop_reloading(character, character.action_in_progress)
                
        elif character.is_equip_moving():
            print("The attack has shaken up the equipment modification of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(2)
            self.stop_equip_event(character, character.action_in_progress.linked_action)
            print("The attack has shaken up the movement of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(2)
            self.stop_moving(character, character.action_in_progress)
            
        elif character.is_modifying_equipment():
            print("The attack has shaken up the equipment modification of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(3)
            self.stop_equip_event(character, character.action_in_progress)
            
        elif character.is_moving():
            print("The attack has shaken up the movement of (", end=' ')
            character.print_basic()
            print(")")
            time.sleep(2)
            self.stop_moving(character, character.action_in_progress)
        
        else:
            return False
        
        if not character.is_melee_fighting():
            #Cancel current action
            character.current_action = Characters.NoAction
            character.timeline = self.current_timeline
            character.action_in_progress = False
            
        return True
    
    
    def stop_moving(self, character, move_action):
        character.path = []
        character.speed_run_level = 0
        character.action_in_progress = False
        try:
            self.scheduler.remove(move_action)
        except:
            pass #Action already removed
        
        
    def stop_equip_event(self, character, event):
        if self.current_timeline < event.timeline:
            nxt_time = max(0, self.current_timeline - event.begin_time - event.equip_handicap)
            print("The equipment modification is cancelled and", \
                "unconscious time (", round(nxt_time,2), ") is added")
            try:
                self.scheduler.remove(event)
            except:
                pass #Action already removed
            
        else:
            nxt_time = event.end_time - self.current_timeline - event.after_equip_handicap
            print("The current equipment modification will be finished,", \
                "but unconscious time (", round(nxt_time,2), ") is added")
        time.sleep(3)
        
        character.unconsciousness += nxt_time
        self.next_equiment = []
        self.next_unequipment = []
        return True
    
    
    def stop_reloading(self, character, reload_action):
        for reload in reload_action.reload_list:
            try:
                character.ammo.remove(reload[1])
            except:
                pass #Ammo already removed
            
        try:
            self.scheduler.remove(reload_action)
        except:
            pass #Action already removed
        
    
    def remove_inactive_char_actions(self, character):
        character.current_action = Characters.NoAction
        character.action_in_progress = False
        
        copy_list = copy.copy(self.scheduler)
        for event in copy_list:
            
            if isinstance(event, MeleeAttackChar):
                if not character.is_alive() and \
                (event.attacker == character or event.defender == character):
                    try:
                        self.scheduler.remove(event)
                    except:
                        pass #Action already removed
                    event.attacker.timeline = character.get_last_possible_timeline()
                    print("The melee attack of (", end=' ')
                    event.attacker.print_basic()
                    print(") has been stopped due to the death of", end=' ')
                    character.print_basic()
                    continue
                
            if isinstance(event, RangedAttackChar):
                if event.attacker == character or \
                (event.defender == character and not event.defender.is_alive()):
                    try:
                        self.scheduler.remove(event)
                    except:
                        pass #Action already removed
                    #event.attacker.timeline = self.current_timeline
                    print("The ranged attack of (", end=' ')
                    event.attacker.print_basic()
                    print(") has been stopped due to the inactive state of (", end=' ')
                    character.print_basic()
                    print(")")
                    continue
                
            if isinstance(event, MoveChar):
                if event.character == character:
                    character.path = []
                    character.speed_run_level = 0
                    try:
                        self.scheduler.remove(event)
                    except:
                        pass #Action already removed
                    continue
                        
            if isinstance(event, EquipChar):
                if event.character == character:
                    self.stop_equip_event(character, event)
                    continue
    
    
    def char_wants_to_defend(self, character):
        for event in self.scheduler:
            if isinstance(event, MeleeAttackChar) and event.defender == character \
            and event.defense_type != MeleeAttackChar.NoDefense:
                return event
        return False
    

#################### CHOOSE ACTIONS ########################
    def choose_actions(self, character):
        while 1:
            print("")
            print("Choose one of the following action:")
            
            for action in Characters.Actions:
                print(action[0:2])
            
            read = input('--> ACT: ')
            
            if read == Characters.Pass[1]:
                if self.pass_action(character):
                    break
            
            elif read == Characters.Rest[1]:
                if self.rest_action(character):
                    break
            
            elif read == Characters.MeleeAttack[1]:
                if self.melee_attack_action(character):
                    break
            
            elif read == Characters.RangedAttack[1]:
                if self.ranged_attack_action(character):
                    break
            
            elif read == Characters.Reload[1]:
                if self.reload_action(character):
                    break
            
            elif read == Characters.Move[1]:
                if self.move_action(character):
                    break
            
            elif read == Characters.EquipAll[1]:
                if self.equip_all_action(character):
                    break
            
            elif read == Characters.EquipSpec[1]:
                if self.equip_spec_action(character):
                    break

            elif read == Characters.UnequipAll[1]:
                if self.unequip_all_action(character):
                    break
            
            elif read == Characters.UnequipSpec[1]:
                if self.unequip_spec_action(character):
                    break
            
            elif read == Characters.Information[1]:
                self.information_action(character)
            
            elif read == Characters.Save[1]:
                self.save_action(character)
            
            elif read == Characters.Load[1]:
                self.load_action(character)
                
            else:
                print("Action:", read, "is not recognized")


    def pass_action(self, character):
        character.current_action = Characters.Pass
        
        print("How much time do you want to wait?")
        txt = "--> Number of " + str(Characters.Pass[2]) + " turns (0 = Cancel): "
        while 1:
            try:
                read = int(input(txt))
                if self.cancel_action(read):
                    return False
                else:
                    break
            except:
                print("The input is not a number")
                continue
            
        character.spend_time(read * Characters.Pass[2])
        character.spend_stamina(read * Characters.Pass[3])
        character.calculate_characteristic()
        print("You have decided to wait", round(read*Characters.Pass[2],1), "turn(s)")
        time.sleep(3)
        return True


    def rest_action(self, character):
        character.current_action = Characters.Rest
        action = RestChar(self, character)
        if not action.is_a_success:
            return False
        return True
    
    
    def melee_attack_action(self, character, target = NoneCharacter):
        character.current_action = Characters.MeleeAttack
        action = MeleeAttackChar(self, character, target)
        if not action.is_a_success:
            return False
        return True
        
        
    def ranged_attack_action(self, character):
        character.current_action = Characters.RangedAttack
        action = RangedAttackChar(self, character)
        if not action.is_a_success:
            return False
        return True

        
    def reload_action(self, character):
        character.current_action = Characters.Reload
        action = ReloadChar(self, character)
        if not action.is_a_success:
            return False
        return True
    
    
    def move_action(self, character):
        character.current_action = Characters.Move
        action = MoveChar(self, character)
        if action.is_a_success:
            return True
        return False
                        
    
    def dodge_move_action(self, character):
        character.current_action = Characters.DodgeMove
        action = MoveChar(self, character)
        if action.is_a_success:
            print("You have decided to move and dodge")
            print("Ranged attacks will, most of the time, have more difficulties to touch you")
            time.sleep(3)
            return True
        return False
    
        
    def def_move_action(self, character):   
        character.current_action = Characters.DefMove
        action = MoveChar(self, character)
        if action.is_a_success:
            print("You have decided to move and defend")
            print("You will have less defense handicap")
            time.sleep(3)
            return True
        return False


    def equip_all_action(self, character):     
        print("You have decided to equip all your weapons")
        character.current_action = Characters.EquipAll
        action = EquipChar(self, character)
        if not action.is_a_success:
            return False
        return True
    
    
    def equip_spec_action(self, character):
        character.current_action = Characters.EquipSpec
        print("You have decided to equip specific weapons")
        action = EquipChar(self, character)
        if not action.is_a_success:
            return False
        return True            
    
    
    def unequip_all_action(self, character):
        character.current_action = Characters.UnequipAll
        print("You have decided to unequipped all your weapons")
        action = EquipChar(self, character)
        if not action.is_a_success:
            return False
        return True            


    def unequip_spec_action(self, character):
        if not character.weapons_use:
            print("You have already unequip all your weapons")
            return False
        else:        
            character.current_action = Characters.UnequipSpec
            print("You have decided to unequip specific weapons")
            action = EquipChar(self, character)
            if not action.is_a_success:
                return False
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
    
        
    def switch_automatic_mode(self, character):
        print("Automatic mode is currently set to: " + str(self.automatic_mode))
        print("Do you want to switch the mode?")
        read = input('--> (Y/N): ')
        if read == "Y":
            self.automatic_mode = not self.automatic_mode
        else:
            self.cancel_action(0)
        return True
    
    
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

    
    def belong_to_team(self, character):
        for char in self.team1.characters_list:
            if character == char:
                return self.team1
        return self.team2
    
    
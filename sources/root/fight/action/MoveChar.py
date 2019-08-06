import math as math
import time as time
from sources.root.character.Characters import Characters
from sources.root.fight.action.Actions import Actions
from sources.root.fight.action.EquipChar import EquipChar
from sources.root.fight.action.ReloadChar import ReloadChar


#############################################################
######################## MOVE CHAR CLASS ####################
#############################################################
class MoveChar:
    'Class to move a self.character'
 
    nb_of_move_before_recalculating_path = 2 #Ratio when the path will be recalculated
    
    
    def __init__(self, fight, character):
        Actions.__init__(self, fight)
        self.character = character
        self.old_abs = self.character.abscissa
        self.old_ord = self.character.ordinate
        self.target_abs = -1
        self.target_ord = -1
        self.quick_turn_asked = False
        self.nb_of_move_left = MoveChar.nb_of_move_before_recalculating_path
        self.is_a_success = self.start()
    

####################### MOVE ACTIONS ########################  
    def start(self):
        Actions.start(self)
        
        if not self.initial_move_check():
            return False
             
        print("Choose your destination:")
        while 1:
            abscissa = -1
            ordinate = -1
            
            read = input('--> Abscissa (-1 = Cancel): ')
            if read == "-1":
                self.fight.cancel_action(0)
                return False
            try:
                abscissa = int(read)
            except:
                print("Abscissa:", read, "is not recognized")
                print("")
                continue
            
            read = input('--> Ordinate (-1 = Cancel): ')
            if read == "-1":
                self.fight.cancel_action(0)
                return False
            try:
                ordinate = int(read)
            except:
                print("Ordinate:", read, "is not recognized")
                print("")
                continue
            
            if not self.fight.field.is_case_free(abscissa, ordinate):
                print("Position:", abscissa, "x", ordinate, "is not available")
                print("")
                continue
    
            path = self.fight.field.choose_path_move(self.character, abscissa, ordinate)
            if not path:
                print("Position:", abscissa, "x", ordinate, "cannot be reached")
                continue
            
            old_move_direction = self.character.move_direction
            coord = path[len(path)-1]
            self.character.move_direction = self.character.char_to_point_angle(coord[0], coord[1])
            
            coord = path.pop(0)
            self.character.current_path = path
            self.target_abs = coord[0]
            self.target_ord = coord[1]
            self.character.move_direction = old_move_direction
            self.character.current_path = []
            return False

                
    def move_character(self):
        if not self.fight.field.is_case_free(self.target_abs, self.target_ord):
            print("Position:", self.target_abs, "x", self.target_ord, "is not available")
            print("")
            return False

        if not self.check_move_stamina():
            return False
        
        self.character.spend_time(self.get_time_coef())
            
        print("You are moving to", self.target_abs, "x", self.target_ord)
        time.sleep(2)
        print("You are following the path:", self.character.current_path)
        time.sleep(3)
        return True
    
    def get_move_coef(self):
        if abs(self.target_abs - self.old_abs) + abs(self.target_ord - self.old_ord) == 2:
            return math.sqrt(2) / self.character.movement_handicap_ratio() / \
                self.fight.field.obstacle_movement_ratio(self.old_abs, self.old_ord, self.target_abs, self.target_ord) / \
                self.character.speed_ratio
        else:
            return 1.0 / self.character.movement_handicap_ratio() / \
                self.fight.field.obstacle_movement_ratio(self.old_abs, self.old_ord, self.target_abs, self.target_ord) / \
                self.character.speed_ratio
                
    
    def get_time_coef(self):
        return self.get_move_coef() / self.character.speed_run_ratio() / self.character.movement_handicap_ratio() \
            * Characters.Move[2]
    
    def get_stamina_coef(self):
        stamina_coef = 1 + (self.character.speed_run_ratio() - 1) * 2 #Between 1 and 3
        stamina_coef /= self.character.movement_handicap_ratio()
        return self.get_move_coef() * stamina_coef * Characters.Move[3]
    
    def result(self):
        Actions.result(self)
        if not self.fight.field.move_character(self.character, self.target_abs, self.target_ord):
            self.cancel_move()
            return False
        else:
            self.character.spend_move_stamina(self.get_stamina_coef())  
            self.character.calculate_characteristic()
            return True
    
    
    def cancel_move(self):
        print("")
        print("*********************************************************************")
        print("Position:", self.target_abs, "x", self.target_ord, "is no longer available")
        print("The move of (", end=' ')
        self.character.print_basic()
        print(") has been cancelled !")
        print("*********************************************************************")
        print("")
        time.sleep(5)
        self.fight.stop_moving(self.character, self)
        self.character.timeline = self.timeline
        self.character.current_action = Characters.NoAction
        
        
######################## BROWSE PATH ##########################
    def browse_current_path(self):
        #Finish equiping when moving is finished
        if not self.character.current_path:
            self.character.action_in_progress = False
            if self.character.current_action == Characters.EquipSpecMove:
                self.character.current_action = Characters.EquipSpec
                self.finish_linked_action(Characters.EquipSpec[2] / Characters.EquipSpecMove[2])
                self.printfinish_modifying_equipment()
                return True
            elif self.character.current_action == Characters.UnequipSpecMove:
                self.character.current_action = Characters.UnequipSpec
                self.finish_linked_action(Characters.UnequipSpec[2] / Characters.UnequipSpecMove[2])
                self.printfinish_modifying_equipment()
                return True
            elif self.character.current_action == Characters.ReloadMove:
                self.character.current_action = Characters.Reload
                self.finish_linked_action(Characters.Reload[2] / Characters.ReloadMove[2])
                self.printfinish_reloading()
                return True
            else:
                self.fight.choose_actions(self.character)
                if not self.character.is_moving():
                    self.character.speed_run_level = 0
                return True
        
        #Normal move when linked action is finished  
        if (self.character.current_action == Characters.EquipSpecMove \
        or self.character.current_action == Characters.UnequipSpecMove \
        or self.character.current_action == Characters.ReloadMove) \
        and self.linked_action.end_time < self.character.timeline:
            self.character.current_action = Characters.Move
            self.linked_action = False
        
        #Update path
        if self.nb_of_move_left <= 0:
            coord = self.character.current_path[len(self.character.current_path) - 1]
            path = self.fight.field.choose_path_move(self.character, coord[0], coord[1])
            if path:
                self.character.current_path = path
            self.nb_of_move_left = MoveChar.nb_of_move_before_recalculating_path
        else:
            self.nb_of_move_left -= 1 
        
        #Choose the next move
        print("")
        print("You are currently moving through the following path ", \
            "(mode used:", self.character.current_action[1], "):", self.character.current_path)
        can_browse_path = True
        while 1:
            print("")
            if can_browse_path and self.fight.automatic_mode:
                if self.continue_browse_path():
                    return True
                can_browse_path = False
                continue
                
            print("Do you want to keep going through this path?")
            if can_browse_path:
                read = input('--> Yes (Y), No (N), Modify move (M): ')
            else:
                read = input('--> No (N), Modify move (M): ')
                
            if can_browse_path and read == "Y":
                if self.continue_browse_path():
                    return True
                can_browse_path = False
                continue
            
            if read == "N":
                if self.stop_browse_path():
                    return True
                return False
            
            if read == "M":
                if self.modify_browse_path():
                    return True
                continue

            print("Answer:", read, "is not recognized")                   


    def continue_browse_path(self):
        coord = self.character.current_path.pop(0)
        self.old_abs = self.target_abs
        self.old_ord = self.target_ord
        self.target_abs = coord[0]
        self.target_ord = coord[1]
        
        if self.move_character():
            return True
        
        print("Movement is impossible through this path!")
        time.sleep(3)
        return False


    def modify_browse_path(self):
        print("")
        if not self.character.is_equip_moving():
            print("Which move mode do you want to use?")
            print("Current mode:", self.character.current_action[1])
            while 1:
                read = input(\
                    '--> Standard Move (' + Characters.Move[1] + \
                    '), Dodge Move (' + Characters.DodgeMove[1] + \
                    '), Defense Move (' + Characters.DefMove[1] + '): ')
                
                if read == Characters.Move[1]:
                    self.character.current_action = Characters.Move
                elif read == Characters.DodgeMove[1]:
                    self.character.current_action = Characters.DodgeMove
                elif read == Characters.DefMove[1]:
                    self.character.current_action = Characters.DefMove
                else:
                    print("Answer:", read, "is not recognized")
                    continue
                break
            
        if self.start():
            return True
        else:
            print("Modifying move failed!")
            time.sleep(3)
            return False
            

    def stop_browse_path(self):
        print("")
        print("Movement is stopped!")
        self.character.current_path = []
        self.character.action_in_progress = False
        if self.character.current_action == Characters.EquipSpecMove:
            print("Character will now finish equiping")
            time.sleep(3)
            self.character.current_action = Characters.EquipSpec
            self.finish_linked_action(Characters.EquipSpec[2] / Characters.EquipSpecMove[2])
            return True
        elif self.character.current_action == Characters.UnequipSpecMove:
            print("Character will now finish unequiping")
            time.sleep(3)
            self.character.current_action = Characters.UnequipSpec
            self.finish_linked_action(Characters.UnequipSpec[2] / Characters.UnequipSpecMove[2])
            return True
        elif self.character.current_action == Characters.ReloadMove:
            print("Character will now finish reloading")
            time.sleep(3)
            self.character.current_action = Characters.Reload
            self.finish_linked_action(Characters.Reload[2] / Characters.ReloadMove[2])
            return True
        else:
            time.sleep(3)
            self.fight.choose_actions(self.character)
            if not self.character.is_moving():
                self.character.speed_run_level = 0
            return True
        return False

    def initial_move_check(self):
        if self.fight.field.can_move(self.character) is False:
            print("No free case available for move action")
            print("")
            return False
        
        if not self.character.check_stamina(1.0 / self.character.movement_handicap_ratio()):
            print("You do not have enough stamina (", \
                self.character.body.return_current_stamina(), ") to move")     
            print("")
            return False
        
        return True
    
    
    def check_move_stamina(self):
        if not self.character.check_stamina(self.get_stamina_coef()):
            print("You do not have enough stamina (", \
                self.character.body.return_current_stamina(), \
                ") to move in that position (abs:", \
                self.target_abs, ",ord:", self.target_ord, ")")
            return False
        
        return True
    
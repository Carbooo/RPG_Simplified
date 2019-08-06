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
    """Class to move a self.character"""
 
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
        #Finish moving
        if not self.character.current_path:
            self.fight.choose_actions(self.character)
        
        #Update path
        if self.nb_of_move_left <= 0:
            coord = self.character.current_path[len(self.character.current_path) - 1]
            path = self.fight.field.choose_path_move(self.character, coord[0], coord[1])
            if path:
                self.character.current_path = path
            self.nb_of_move_left = MoveChar.nb_of_move_before_recalculating_path
        else:
            self.nb_of_move_left -= 1 

        if self.continue_browse_path():
            return True
        else:
            return self.stop_browse_path()

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

    def stop_browse_path(self):
        print("")
        print("Movement is stopped!")
        self.character.current_path = []
        self.character.action_in_progress = False
        time.sleep(3)
        self.fight.choose_actions(self.character)
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
    
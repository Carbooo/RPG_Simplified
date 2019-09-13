import math as math
import time as time
import sources.miscellaneous.configuration as cfg
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions


#############################################################
######################## MOVE CHAR CLASS ####################
#############################################################
class Move(ActiveActions):
    """Class to move a character"""

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Moving"
        self.target_abs = -1
        self.target_ord = -1
        self.path = []
        self.nb_of_move_left = cfg.nb_of_move_before_recalculating_path
        self.total_nb_of_move = cfg.max_move_per_action
        self.is_a_success = self.start()

    ####################### MOVE ACTIONS ########################
    def start(self):
        if not self.initial_move_check():
            return False

        print("Choose your destination:")
        while 1:
            abscissa = -1
            ordinate = -1

            read = input('--> Abscissa (-1 = Cancel): ')
            if read == "-1":
                Actions.cancel_action(0)
                return False
            try:
                abscissa = int(read)
            except:
                print("Abscissa:", read, "is not recognized")
                print("")
                continue

            read = input('--> Ordinate (-1 = Cancel): ')
            if read == "-1":
                Actions.cancel_action(0)
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

            self.path = self.fight.field.choose_path_move(self.initiator, abscissa, ordinate)
            if not self.path:
                print("Position:", abscissa, "x", ordinate, "cannot be reached")
                print("")
                continue

            coord = self.path.pop(0)
            self.target_abs = coord[0]
            self.target_ord = coord[1]
            
            if not self.check_move_stamina():
                print("You do not have enough stamina (", self.initiator.body.stamina, ") to move there")
                print("")
                continue

            self.end_update(self.get_move_coef() * cfg.actions["move"]["stamina"],
                            self.get_move_coef() * cfg.actions["move"]["duration"])
            return True

    def execute(self):
        # Move
        if not self.fight.field.move_character(self.initiator, self.target_abs, self.target_ord):
            return self.cancel_move()

        print("")
        print("*********************************************************************")
        print(self.initiator.print_basic(), "has moved to", self.target_abs, "x", self.target_ord)
        print("Next steps are:", self.path)
        print("*********************************************************************")
        print("")
        time.sleep(3)
        
        # Test if destination is reachex
        if not self.path:
            return False  # To stop looping
        
        # Stop moving if max move is reached
        self.total_nb_of_move -= 1 
        if self.total_nb_of_move == 0:
            print("********* Max number of moves reached ********")
            return self.cancel_move()
            
        # Update path regularly to adapt to field changes
        if self.nb_of_move_left <= 0:
            coord = self.path[-1]
            path = self.fight.field.choose_path_move(self.initiator, coord[0], coord[1])
            if path:
                self.path = path
                self.nb_of_move_left = cfg.nb_of_move_before_recalculating_path
            else:
                print("******* Target destination is no longer reachable *******")
                return self.cancel_move()
        else:
            self.nb_of_move_left -= 1
        
        # Prepare next step
        coord = self.path.pop(0)
        self.target_abs = coord[0]
        self.target_ord = coord[1]
            
        if not self.check_move_stamina():
            print("******* You do not have enough stamina (", 
                    self.initiator.body.stamina, 
                    ") to keep moving *******")
            return self.cancel_move()
        
        if not self.fight.field.is_case_free(self.target_abs, self.target_ord):
            print("******* Position:", self.target_abs, 
                    "x", self.target_ord, 
                    "is no longer available *******")
            return self.cancel_move()

        self.end_update(self.get_move_coef() * cfg.actions["move"]["stamina"],
                        self.get_move_coef() * cfg.actions["move"]["duration"])
        return True

    def get_move_coef(self):
        coef = 1.0 \
               / self.fight.field.obstacle_movement_ratio(self.initiator.abscissa, self.initiator.ordinate,
                                                          self.target_abs, self.target_ord) \
               / self.initiator.movement_handicap_ratio()
        if abs(self.target_abs - self.initiator.abscissa) + abs(self.target_ord - self.initiator.ordinate) == 2:
            return coef * math.sqrt(2)
        else:
            return coef

    def cancel_move(self):
        print("")
        print("*********************************************************************")
        print("Position:", self.target_abs, "x", self.target_ord, "is no longer reachable")
        print("The move of (", end=' ')
        self.initiator.print_basic()
        print(") has been cancelled !")
        print("*********************************************************************")
        print("")
        self.path = []
        time.sleep(5)
        return False

    ######################## BROWSE PATH ##########################
    def initial_move_check(self):
        if self.fight.field.can_move(self.initiator) is False:
            print("No free case available for move action")
            print("")
            return False

        if not self.initiator.check_stamina(1.0 / self.initiator.movement_handicap_ratio()):
            print("You do not have enough stamina (", self.initiator.body.stamina, ") to move")
            print("")
            return False

        return True

    def check_move_stamina(self):
        if not self.initiator.check_stamina(self.get_move_coef() * cfg.actions["move"]["stamina"]):
            print("You do not have enough stamina (",
                  self.initiator.body.return_current_stamina(),
                  ") to move in that position (abs:",
                  self.target_abs, ",ord:", self.target_ord, ")")
            return False

        return True

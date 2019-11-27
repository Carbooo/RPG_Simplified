import math as math
import time as time
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
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
        self.type = "Move"
        self.target_abs = -1
        self.target_ord = -1
        self.path = []
        self.nb_of_move_left = cfg.nb_of_move_before_recalculating_path
        self.total_nb_of_move = cfg.max_move_per_action
        self.is_a_success = self.start()

    ####################### MOVE ACTIONS ########################
    def start(self):
        if not super().start():
            return False
        if not self.initial_move_check():
            return False

        func.optional_print("Choose your destination:")
        while 1:
            abscissa = -1
            ordinate = -1

            read = func.optional_input('--> Abscissa (-1 = Cancel): ')
            if read == "-1":
                Actions.cancel_action(0)
                return False
            try:
                abscissa = int(read)
            except:
                func.optional_print("Abscissa:", read, "is not recognized")
                func.optional_print("")
                continue

            read = func.optional_input('--> Ordinate (-1 = Cancel): ')
            if read == "-1":
                Actions.cancel_action(0)
                return False
            try:
                ordinate = int(read)
            except:
                func.optional_print("Ordinate:", read, "is not recognized")
                func.optional_print("")
                continue

            if not self.fight.field.is_case_free(abscissa, ordinate):
                func.optional_print("Position:", abscissa, "x", ordinate, "is not available")
                func.optional_print("")
                continue

            self.path = self.fight.field.choose_path_move(self.initiator, abscissa, ordinate)
            if not self.path:
                func.optional_print("Position:", abscissa, "x", ordinate, "cannot be reached")
                func.optional_print("")
                continue

            coord = self.path.pop(0)
            self.target_abs = coord[0]
            self.target_ord = coord[1]
            
            if not self.check_move_stamina():
                func.optional_print("You do not have enough stamina (", self.initiator.body.stamina, ") to move there")
                func.optional_print("")
                continue

            func.optional_print("Moving:", self.get_move_coef() * cfg.actions["move"]["duration"], level=2, debug=True)
            self.end_update(self.get_move_coef() * cfg.actions["move"]["stamina"],
                            self.get_move_coef() * cfg.actions["move"]["duration"])
            return True

    def execute(self):
        # Move
        if not self.fight.field.is_case_adjacent_to_char(self.initiator, self.target_abs, self.target_ord) or not self.fight.field.move_character(self.initiator, self.target_abs, self.target_ord):
            return self.cancel_move()

        func.optional_print("", level=0)
        func.optional_print("*********************************************************************", level=0)
        func.optional_print(self.initiator.print_basic(), "has moved to", self.target_abs, "x", self.target_ord, level=0)
        func.optional_print("Next steps are:", self.path, level=0)
        func.optional_print("*********************************************************************", level=0)
        func.optional_print("", level=0)
        
        # Test if destination is reachex
        if not self.path:
            return False  # To stop looping
        
        # Stop moving if max move is reached
        self.total_nb_of_move -= 1 
        if self.total_nb_of_move == 0:
            func.optional_print("********* Max number of moves reached ********")
            return self.cancel_move()
            
        # Update path regularly to adapt to field changes
        if self.nb_of_move_left <= 0:
            coord = self.path[-1]
            path = self.fight.field.choose_path_move(self.initiator, coord[0], coord[1])
            if path:
                self.path = path
                self.nb_of_move_left = cfg.nb_of_move_before_recalculating_path
            else:
                func.optional_print("******* Target destination is no longer reachable *******")
                return self.cancel_move()
        else:
            self.nb_of_move_left -= 1
        
        # Prepare next step
        coord = self.path.pop(0)
        self.target_abs = coord[0]
        self.target_ord = coord[1]
            
        if not self.check_move_stamina():
            func.optional_print("******* You do not have enough stamina (",
                    self.initiator.body.stamina, 
                    ") to keep moving *******")
            return self.cancel_move()
        
        if not self.fight.field.is_case_free(self.target_abs, self.target_ord):
            func.optional_print("******* Position:", self.target_abs,
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
        func.optional_print("")
        func.optional_print("*********************************************************************")
        func.optional_print("Position:", self.target_abs, "x", self.target_ord, "is no longer reachable")
        func.optional_print("The move of (", skip_line=True)
        self.initiator.print_basic()
        func.optional_print(") has been cancelled !")
        func.optional_print("*********************************************************************")
        func.optional_print("")
        self.path = []
        func.optional_sleep(3)
        return False

    ######################## BROWSE PATH ##########################
    def initial_move_check(self):
        if self.fight.field.can_move(self.initiator) is False:
            func.optional_print("No free case available for move action")
            func.optional_print("")
            return False

        if not self.initiator.check_stamina(1.0 / self.initiator.movement_handicap_ratio()):
            func.optional_print("You do not have enough stamina (", self.initiator.body.stamina, ") to move")
            func.optional_print("")
            return False

        return True

    def check_move_stamina(self):
        if not self.initiator.check_stamina(self.get_move_coef() * cfg.actions["move"]["stamina"]):
            func.optional_print("You do not have enough stamina (",
                  self.initiator.body.return_current_stamina(),
                  ") to move in that position (abs:",
                  self.target_abs, ",ord:", self.target_ord, ")")
            return False

        return True

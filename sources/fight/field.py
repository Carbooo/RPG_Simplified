import copy as copy
import math as math
import numpy as np
import random as random
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
##################### FIELDS CLASS ##########################
#############################################################
class Field:
    """Common base class for all fields"""

    def __init__(self, name, obstacles_array, reliefs_array):
        self.ID = len(cfg.field_list) + 1
        self.name = name
        self.abscissa_size = len(obstacles_array[0::, 0])
        self.ordinate_size = len(obstacles_array[0, 0::])
        self.characters_array = []
        self.obstacles_array = obstacles_array
        self.reliefs_array = reliefs_array
        self.active_spells = []
        self.reset_characters_array()
        if self.validate_arrays_size():
            if self.validate_obstacles_array():
                cfg.field_list.append(self)

    def get_id(self):
        return self.ID

#################### CHECK FUNCTIONS ###########################
    def validate_arrays_size(self):
        # Check the minimum size of a field
        if self.abscissa_size < cfg.max_position_area * 2 \
                or self.ordinate_size < cfg.max_position_area:
            func.optional_print("(Field) The field is too small.",
                  "It must be at least:",
                  cfg.max_position_area * 2,
                  "x", cfg.max_position_area)

        # Check the columns size
        for i in range(self.abscissa_size):
            if len(self.obstacles_array[i, 0::]) != self.ordinate_size \
                    or len(self.reliefs_array[i, 0::]) != self.ordinate_size:
                func.optional_print("(Field) Not all the columns have the same size")
                return False

        # Check the line size
        for i in range(self.ordinate_size):
            if len(self.obstacles_array[0::, i]) != self.abscissa_size or \
                    len(self.reliefs_array[0::, i]) != self.abscissa_size:
                func.optional_print("(Field) Not all the lines have the same size")
                return False

        return True

    def validate_obstacles_array(self):
        # Check the obstacles value
        for i in range(self.abscissa_size):
            for j in range(self.ordinate_size):
                if self.obstacles_array[i, j] not in cfg.obstacle_types_list:
                    func.optional_print("(Fields) The obstacle array contains illegal values")
                    return False
        return True

    def is_a_case(self, abscissa, ordinate):
        if abscissa not in range(self.abscissa_size) or \
                ordinate not in range(self.ordinate_size):
            return False
        return True

    def is_case_free(self, abscissa, ordinate):
        if not self.is_case_obstacle_free(abscissa, ordinate):
            return False
        if not self.is_case_character_free(abscissa, ordinate):
            return False
        return True

    def is_case_obstacle_free(self, abscissa, ordinate):
        if not self.is_a_case(abscissa, ordinate):
            return False
        if self.obstacles_array[abscissa, ordinate] == cfg.melee_obstacle \
                or self.obstacles_array[abscissa, ordinate] == cfg.full_obstacle:
            return False
        return True

    def is_case_character_free(self, abscissa, ordinate):
        if not self.is_a_case(abscissa, ordinate):
            return False
        if not self.characters_array[abscissa, ordinate] is None:
            return False
        return True
        
    def is_case_adjacent_to_char(self, character, abscissa, ordinate):
        if not self.is_a_case(abscissa, ordinate):
            return False
            
        adjacent = False
        for i in range(character.abscissa - 1, character.abscissa + 2):
            for j in range(character.ordinate - 1, character.ordinate + 2):
                if abscissa == i and ordinate == j:
                    adjacent = True
                    break
        return adjacent
    
    def get_character_from_pos(self, abscissa, ordinate):
        if not self.is_a_case(abscissa, ordinate):
            return False
        if self.characters_array[abscissa, ordinate] is None:
            return False
        else:
            return self.characters_array[abscissa, ordinate]

    def is_case_ranged_free(self, abscissa, ordinate):
        if not self.is_a_case(abscissa, ordinate):
            return False
        if not self.obstacles_array[abscissa, ordinate] == cfg.ranged_obstacle \
                or not self.obstacles_array[abscissa, ordinate] == cfg.full_obstacle:
            return False
        return True

    def is_target_reachable(self, attacker, target):
        if target.body.is_alive() and attacker.is_distance_reachable(target) and \
                self.calculate_ranged_obstacle_ratio(attacker, target.abscissa, target.ordinate) > 0:
            return True
        return False
        
    def is_target_magically_reachable(self, attacker, target):
        if target.body.is_alive() and attacker.is_enemy_magically_reachable(target) and \
                self.calculate_ranged_obstacle_ratio(attacker, target.abscissa, target.ordinate) >= cfg.min_visibility:
            return True
        return False
    
    def is_pos_magically_reachable(self, attacker, abscissa, ordinate):
        if attacker.is_distance_magically_reachable(abscissa, ordinate) and \
                self.calculate_ranged_obstacle_ratio(attacker, abscissa, ordinate) >= cfg.min_visibility:
            return True
        return False
        
    def get_magical_accuracy(self, attacker, target):
        coef = attacker.get_magic_distance_ratio(target) \
             * self.calculate_ranged_obstacle_ratio(attacker, target.abscissa, target.ordinate) \
             * attacker.magic_power_ratio
        return 0.5 + coef  # Between 0.5 and 1.5 as other attacks

    def calculate_ranged_obstacle_ratio(self, attacker, target_abs, target_ord):
        min_abs = min(attacker.abscissa, target_abs)
        min_ord = min(attacker.ordinate, target_ord)
        path_ratio = 1

        for i in range(abs(attacker.abscissa - target_abs) + 1):
            for j in range(abs(attacker.ordinate - target_ord) + 1):
                if (min_abs + i != attacker.abscissa or min_ord + j != attacker.ordinate) and \
                        (min_abs + i != target_abs or min_ord + j != target_ord) and \
                        attacker.calculate_point_to_enemy_path_distance(target_abs, target_ord, min_abs + i, min_ord + j) <= 0.5:

                    if self.obstacles_array[min_abs + i, min_ord + j] == cfg.ranged_obstacle or \
                            self.obstacles_array[min_abs + i, min_ord + j] == cfg.full_obstacle or \
                            (self.characters_array[min_abs + i, min_ord + j] is not None and (
                                # Very closed, not busy, allies do not count as obstacles
                                not (i in (0, 1) and j in (0, 1) and (
                                    self.characters_array[min_abs + i, min_ord + j].last_action is None or
                                    self.characters_array[min_abs + i, min_ord + j].last_action.type == "Waiting"
                                ))
                                and
                                # If path is at the border of the case, the character is not an obstacle
                                attacker.calculate_point_to_enemy_path_distance(target_abs, target_ord,
                                                                                min_abs + i, min_ord + j) < 0.25
                            )):
                        return 0

                    if self.obstacles_array[min_abs + i, min_ord + j] == cfg.ranged_handicap or \
                            self.obstacles_array[min_abs + i, min_ord + j] == cfg.full_handicap:
                        path_ratio *= cfg.ranged_handicap_ratio

        return path_ratio

    def shoot_has_hit_another_target(self, attacker, target, hit_chance):
        # Test if it has missed the target
        rd = random.random()
        if rd <= hit_chance:
            # Not missed
            return True

        # Test wrong direction of the arrow
        # Calculate target position at +/- variation angle
        variation = random.gauss(0, cfg.variance) * 10
        pos_p = copy.copy(target)
        attacker.set_target_pos_variation(pos_p, variation)
        min_abs_p = min(attacker.abscissa, pos_p.abscissa)
        min_ord_p = min(attacker.ordinate, pos_p.ordinate)

        # Calculate shoot direction
        pos_p_abs_range = list(range(abs(attacker.abscissa - pos_p.abscissa) + 1))
        if attacker.abscissa > pos_p.abscissa:
            pos_p_abs_range.reverse()
        pos_p_ord_range = list(range(abs(attacker.ordinate - pos_p.ordinate) + 1))
        if attacker.ordinate > pos_p.ordinate:
            pos_p_ord_range.reverse()

        # Calculate shoot length
        length = attacker.calculate_point_distance(target.abscissa, target.ordinate)
        length += (attacker.equipments.get_range() - length) / 3  # shoot length depend of target distance
        length *= max(0, random.gauss(cfg.mean, cfg.variance))

        # Browse shoot path
        for i in pos_p_abs_range:
            for j in pos_p_ord_range:
                c_abs = min_abs_p + i
                c_ord = min_ord_p + j

                # Not in the path of the arrow
                if (c_abs == target.abscissa and c_ord == target.ordinate) or \
                        (c_abs == attacker.abscissa and c_ord == attacker.ordinate) or \
                        attacker.calculate_point_distance(c_abs, c_ord) > length or \
                        attacker.calculate_point_to_enemy_path_distance(pos_p.abscissa, pos_p.ordinate, c_abs, c_ord) >= 0.5:
                    continue

                # Shoot out of field or blocked by an obstacle
                if not self.is_a_case(c_abs, c_ord) or \
                        not self.is_case_ranged_free(c_abs, c_ord) or \
                        (self.obstacles_array[c_abs, c_ord] == cfg.ranged_handicap and random.random() < 0.5):
                    return False

                # Shoot has hit another character
                if not self.is_case_character_free(c_abs, c_ord) \
                        and random.random() < 0.35:
                    return self.characters_array[c_abs, c_ord]
        return False

    def get_next_possible_pos_from_max_distance(self, attacker, target, max_distance):  # Used to knock back a char
        obstacle_reached = False
        other_char = None
        new_abscissa = target.abscissa
        new_ordinate = target.ordinate
        
        for i in range(1, max_distance + 1):
            coord = attacker.get_next_pos_from_add_distance(target, i)
            other_char = self.get_character_from_pos(coord["new_abscissa"], coord["new_ordinate"])
            if not self.is_case_obstacle_free(coord["new_abscissa"], coord["new_ordinate"]):
                obstacle_reached = True
                break
            elif not self.is_case_character_free(coord["new_abscissa"], coord["new_ordinate"]) and \
                    target != other_char:
                break
            else:
                new_abscissa = coord["new_abscissa"]
                new_ordinate = coord["new_ordinate"]
        
        return {
            "new_abscissa": new_abscissa, 
            "new_ordinate": new_ordinate,
            "obstacle_reached": obstacle_reached,
            "other_char": other_char
        }

    ###################### SET AND MOVE FUNCTIONS #####################
    def remove_dead_char(self, character):
        if character.body.state == "Dead" and \
                character == self.characters_array[character.abscissa, character.ordinate]:
            self.characters_array[character.abscissa, character.ordinate] = None

    def reset_characters_array(self):
        char_array = [None for _ in range(self.abscissa_size * self.ordinate_size)]
        char_array = np.array(char_array)
        self.characters_array = np.reshape(char_array, (self.abscissa_size, self.ordinate_size))

    def remove_character(self, character):
        self.characters_array[character.abscissa, character.ordinate] = None

    def move_character(self, character, new_abscissa, new_ordinate):
        old_abscissa = character.abscissa
        old_ordinate = character.ordinate

        self.remove_character(character)

        character.set_position(new_abscissa, new_ordinate)
        if self.set_character(character):
            return True

        # If the set_character failed, reset the previous position
        character.set_position(old_abscissa, old_ordinate)
        self.set_character(character)
        return False

    def melee_fight_move(self, target, attacker):
        # Find all possible positions
        target_positions = []
        attacker_positions = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                def_abs = target.abscissa + i
                def_ord = target.ordinate + j
                if self.is_case_free(def_abs, def_ord) or (i == 0 and j == 0):
                    target_positions.append([def_abs, def_ord])
                att_abs = attacker.abscissa + i
                att_ord = attacker.ordinate + j
                if self.is_case_free(att_abs, att_ord) or (i == 0 and j == 0):
                    attacker_positions.append([att_abs, att_ord])

        # Set target position (farthest possible from attacker)
        max_chance = 0
        position = -1
        for i in range(len(target_positions)):
            ratio = (1 + abs(target_positions[i][0] - attacker.abscissa) +
                     abs(target_positions[i][1] - attacker.ordinate)
                     ) * random.random()
            if max_chance < ratio:
                max_chance = ratio
                position = i
        self.move_character(target, target_positions[position][0], target_positions[position][1])

        # Set attacker position (closest possible from target)
        max_chance = 0
        position = -1
        for i in range(len(attacker_positions)):
            ratio = (1.0 / (1 + abs(attacker_positions[i][0] - target.abscissa) +
                            abs(attacker_positions[i][1] - target.ordinate))
                     ) * random.random()
            if max_chance < ratio:
                max_chance = ratio
                position = i
        self.move_character(attacker, attacker_positions[position][0], attacker_positions[position][1])

    def obstacle_movement_ratio(self, current_abs, current_ord, target_abs, target_ord):
        if self.is_a_case(target_abs, target_ord):
            ratio = 1
            if self.obstacles_array[current_abs, current_ord] == cfg.melee_handicap:
                ratio *= cfg.melee_handicap_ratio
            if self.obstacles_array[target_abs, target_ord] == cfg.full_handicap:
                ratio *= cfg.melee_handicap_ratio
            return ratio

    def set_character(self, character):
        # Set a character into its position values
        if self.is_case_free(character.abscissa, character.ordinate):
            self.characters_array[character.abscissa, character.ordinate] = character
            return True
        return False

    def set_initial_character(self, character):
        # Set a character into its position values. If not available,
        # choose the first position around the default position

        # Try the character position
        if self.set_character(character):
            return True

        # If pos not available, try random position around character position
        pos_list = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                pos_list.append((i, j))

        for _ in range(9):
            i, j = random.choice(pos_list)
            pos_list.remove((i, j))

            abscissa = character.abscissa + i
            ordinate = character.ordinate + j

            if self.is_case_free(abscissa, ordinate):
                character.set_position(abscissa, ordinate)
                self.characters_array[abscissa, ordinate] = character
                return True

        return False

    def set_team(self, team):
        # Set the team on the left of the field
        # Calculate the middle ordinate
        zero_ordinate = int(round((self.ordinate_size - cfg.max_position_area) / 2))

        for char in team.characters_list:
            # update the zero ordinate
            char.ordinate += zero_ordinate
            char.last_direction = 0

            # If a character could not be set, reset all characters
            if not self.set_initial_character(char):
                team.reset_characters()
                func.optional_print("(Fields) Cannot set team:")
                team.print_obj()
                return False
        return True

    def set_reverse_team(self, team):
        # Set the team on the right of the field (abscissa are reversed)
        for char in team.characters_list:
            # Set the max position in the array minus the character position
            char.abscissa = self.abscissa_size - char.abscissa - 1
            char.last_direction = math.pi / 2

        if self.set_team(team):
            for char in team.characters_list:
                char.last_direction = math.pi / 2
            return True
        return False

    def set_all_teams(self, team1, team2):
        self.reset_characters_array()

        # Check if the team are correctly positioned
        # The control is only done here and not in the sub-set function
        # To prevent the new field position to be erronous
        if not team1.is_positioned():
            func.optional_print("(Fields) Cannot set team:")
            team1.print_obj()
            return False
        if not team2.is_positioned():
            func.optional_print("(Fields) Cannot set team:")
            team2.print_obj()
            return False

        # set teams
        if random.choice([0, 1]) == 0:
            self.set_team(team1)
            self.set_reverse_team(team2)
        else:
            self.set_team(team2)
            self.set_reverse_team(team1)
        return True

    def can_move(self, character):
        for i in range(character.abscissa - 1, character.abscissa + 2):
            for j in range(character.ordinate - 1, character.ordinate + 2):
                if self.is_case_free(i, j):
                    return True
        return False

    def random_move(self, character, probability):
        possible_moves = []
        for i in range(character.abscissa - 1, character.abscissa + 2):
            for j in range(character.ordinate - 1, character.ordinate + 2):
                if self.is_case_free(i, j):
                    possible_moves.append((i, j))
        
        if possible_moves and random.random() < probability:
            new_abs, new_ord = random.choice(possible_moves)
            self.move_character(character, new_abs, new_ord)
            return True

        return False

    @staticmethod
    def heuristic_value(source_abs, source_ord, target_abs, target_ord):
        return math.sqrt(math.pow(source_abs - target_abs, 2) + math.pow(source_ord - target_ord, 2))

    def movement_cost(self, current_abs, current_ord, target_abs, target_ord):
        if abs(current_abs - target_abs) + abs(current_ord - target_ord) == 2:
            # Diagonal move
            cost = math.sqrt(2)
        else:
            # Standard move
            cost = 1
        return cost / self.obstacle_movement_ratio(current_abs, current_ord, target_abs, target_ord)

    @staticmethod
    def is_a_browsed_pos(current_paths, new_abs, new_ord):
        for path in range(len(current_paths)):
            for i in range(len(current_paths[path][3])):
                if new_abs == current_paths[path][3][i][0] and \
                        new_ord == current_paths[path][3][i][1]:
                    return True
        return False

    def choose_path_move(self, character, target_abs, target_ord):
        # A* Algorithm
        path_abs = character.abscissa
        path_ord = character.ordinate
        current_paths = []
        current_paths.append([path_abs, path_ord, 0, []])

        # Browse until the destination is reached
        while path_abs != target_abs or path_ord != target_ord:
            # Calcultate for each path the best move
            possible_paths = []
            for path in range(len(current_paths)):
                current_abs = current_paths[path][0]
                current_ord = current_paths[path][1]
                current_cost = current_paths[path][2]
                current_path_browsed = current_paths[path][3]

                # Calculate all moves for a path
                possible_moves = []
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        new_abs = current_abs + i
                        new_ord = current_ord + j
                        # Only browse new available case
                        if not self.is_case_free(new_abs, new_ord) or \
                                (i == 0 and j == 0) or \
                                Field.is_a_browsed_pos(current_paths, new_abs, new_ord):
                            continue

                        # Store information
                        move_values = []
                        possible_moves.append(move_values)
                        move_values.append(new_abs)
                        move_values.append(new_ord)

                        # Calculate movement cost
                        move_values.append(self.movement_cost(current_abs, current_ord, new_abs, new_ord))

                        # Calculate all heuristic values
                        move_values.append(Field.heuristic_value(new_abs, new_ord, target_abs, target_ord))

                # Choose min (cost-heuristic) path
                min_cost = 10000000
                min_path = []
                for i in range(len(possible_moves)):
                    cost = possible_moves[i][2] + possible_moves[i][3]
                    if cost < min_cost:
                        min_cost = cost
                        new_path = copy.copy(current_path_browsed)
                        new_path.append([possible_moves[i][0], possible_moves[i][1]])
                        min_path = [possible_moves[i][0], possible_moves[i][1],
                                    current_cost + possible_moves[i][2], new_path,
                                    possible_moves[i][3]]
                if min_cost < 10000000:
                    possible_paths.append(min_path)

            # Stop the search if no new path is available
            if len(possible_paths) == 0:
                return False

            # Only save the best new path
            min_cost = 10000000
            min_path = []
            for i in range(len(possible_paths)):
                cost = possible_paths[i][2] + possible_paths[i][4]
                if cost < min_cost:
                    min_cost = cost
                    min_path = possible_paths[i][0:4]

                    # Set last position to break the while
                    path_abs = possible_paths[i][0]
                    path_ord = possible_paths[i][1]
            current_paths.append(min_path)

        return current_paths[len(current_paths) - 1][3]

################ PRINTING FUNCTIONS ########################
    def print_line(self):
        stri = "----|"
        for _ in range(1, self.abscissa_size + 1):
            stri += "----|"
        stri += "----"
        func.optional_print(stri)

    def print_abs_scale(self):
        stri = "  "
        for j in range(self.abscissa_size):
            if (j <= 10):
                stri += "  | " + str(j)
            else:
                stri += " | " + str(j)
        stri += " |"
        func.optional_print(stri)

    def print_obj(self):
        func.optional_print("************************** FIELD ************************")
        func.optional_print("--  ACTIVE SPELLS --")
        for spell in self.active_spells:
            func.optional_print("   -", spell.surname, "(", spell.target_abs, "x", spell.target_ord, ") : ",
                                int(round(spell.spell_power["spread_distance"] * spell.magical_coef)), "cases")
        func.optional_print("")

        obs_array = np.transpose(self.obstacles_array)
        char_array = np.transpose(self.characters_array)
        func.optional_print("ID:", self.get_id(), ", name:", self.name)

        # Top abscissa scale
        self.print_abs_scale()

        # Separation line
        self.print_line()

        stri = ""
        current_ord = self.ordinate_size - 1
        for i in range(self.ordinate_size - 1, -1, -1):
            # Left ordinate scale
            if (i < 10):
                stri += " " + str(current_ord) + "  |"
            else:
                stri += " " + str(current_ord) + " |"

            # Array content
            for j in range(self.abscissa_size):
                if char_array[i, j] is None:
                    temp = " " + obs_array[i, j] + "  "
                else:
                    temp = " " + char_array[i, j].name[:2] + " "

                stri += temp + "|"

            # Right ordinate scale
            stri += " " + str(current_ord)

            # Print the whole line
            func.optional_print(stri)
            stri = ""

            # Separation line
            self.print_line()

            current_ord -= 1

        # Bottom abscissa scale
        self.print_abs_scale()

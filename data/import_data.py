import csv as csv
import numpy as np
from sources.character.equipments import Armors, Shields, MeleeWeapons, RangedWeapons, Bows, Crossbows, Ammo
from sources.character.character import Character
from sources.fight.team import Team
from sources.fight.field import Field
import sources.miscellaneous.configuration as cfg


###########################################################
##################### IMPORT CLASS ########################
###########################################################
class ImportData:
    """Common base class for all data importing"""

    def __init__(self, import_type, file_path):
        self.my_csv = csv.reader(
            open(file_path, 'rt'), delimiter=';')
        next(self.my_csv)

        self.name = file_path.split("\\")
        self.name = self.name[len(self.name) - 1]

        if import_type == "Armors":
            self.import_armors()
        elif import_type == "Shields":
            self.import_shields()
        elif import_type == "MeleeWeapons":
            self.import_melee_weapons()
        elif import_type == "Ammo":
            self.import_ammo()
        elif import_type == "RangedWeapons":
            self.import_ranged_weapons()
        elif import_type == "Characters":
            self.import_characters()
        elif import_type == "Teams":
            self.import_teams()
        elif import_type == "ObstaclesField":
            self.import_obstacles_field()
        else:
            print("Type:", import_type, "is not recognized.",
                  "No data has been imported")

    def import_armors(self):
        for row in self.my_csv:
            if len(row) != 6:
                print("Armors import does not contain the right number of columns")
                return False
            else:
                Armors(row[0], float(row[1]), float(row[2]), float(row[3]),
                       float(row[4]), float(row[5]))
        return True

    def import_shields(self):
        for row in self.my_csv:
            if len(row) != 11:
                print("Shields import does not contain the right number of columns")
                return False
            else:
                Shields(row[0], float(row[1]), float(row[2]), float(row[3]),
                        int(row[4]), float(row[5]), float(row[6]), float(row[7]),
                        float(row[8]), float(row[9]), float(row[10]))
        return True

    def import_melee_weapons(self):
        for row in self.my_csv:
            if len(row) != 11:
                print("Melee weapons import does not contain the right number of columns")
                return False
            else:
                MeleeWeapons(row[0], float(row[1]), float(row[2]),
                             float(row[3]), int(row[4]), float(row[5]), float(row[6]),
                             float(row[7]), float(row[8]), float(row[9]), float(row[10]))
        return True

    def import_ammo(self):
        for row in self.my_csv:
            if len(row) != 8:
                print("Ammo import does not contain the right number of columns")
                return False
            else:
                Ammo(row[0], float(row[1]), float(row[2]), float(row[3]),
                     row[4], float(row[5]), float(row[6]), float(row[7]))
        return True

    def import_ranged_weapons(self):
        for row in self.my_csv:
            if len(row) != 15:
                print("Ranged weapons import does not contain the right number of columns")
                return False
            elif int(row[14]) == 0:
                Bows(row[0], float(row[1]), float(row[2]), float(row[3]),
                     int(row[4]), float(row[5]), float(row[6]), float(row[7]),
                     float(row[8]), float(row[9]), float(row[10]), float(row[11]),
                     float(row[12]), float(row[13]))
            elif int(row[14]) == 1:
                Crossbows(row[0], float(row[1]), float(row[2]), float(row[3]),
                          int(row[4]), float(row[5]), float(row[6]), float(row[7]),
                          float(row[8]), float(row[9]), float(row[10]), float(row[11]),
                          float(row[12]), float(row[13]))
            else:
                print("Ranged weapons is neither defined as a bow or a crossbow")
                return False
        return True

    def import_characters(self):
        for row in self.my_csv:
            if len(row) != 39:
                print("Characters import does not contain the right number of columns")
                return False
            else:
                Character(row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4]),
                          int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]),
                          row[10], row[11], row[12], row[13], row[14], row[15], int(row[16]), row[17], int(row[18]),
                          int(row[19]), int(row[20]), int(row[21]), int(row[22]), int(row[23]), int(row[24]),
                          int(row[25]), int(row[26]), int(row[27]), int(row[28]), int(row[29]), int(row[30]),
                          int(row[31]), int(row[32]), int(row[33]), int(row[34]), int(row[35]), int(row[36]),
                          int(row[37]), int(row[38]))
        return True

    def import_teams(self):
        for row in self.my_csv:
            if len(row) < 2:
                print("Teams import does not contain the right number of columns")
                return False
            else:
                characters_name_list = []
                for name in row[1::]:
                    characters_name_list.append(name)
                Team(row[0], characters_name_list)
        return True

    def import_obstacles_field(self):
        obstacle_array = []
        ordinate_size = 0

        # Browse all CSV
        for row in self.my_csv:

            # Set abscissa_size
            if ordinate_size == 0:
                abscissa_size = len(row[1::])

            # Verify consistency (array)
            elif len(row[1::]) != abscissa_size:
                print("Obstacle field import is not consistent.",
                      "It must be an array.")
                return False

            # Import all data, except the first column
            obstacle_array.append(row[1::])

            ordinate_size += 1

        # Verify minimum abscissa size
        if abscissa_size < cfg.max_position_area * 2:
            print("Field import is not large enough (min:",
                  cfg.max_position_area * 2, ")")
            return False

        # Verify minimum ordinate size
        if ordinate_size < cfg.max_position_area:
            print("Field import is not long enough (min:",
                  cfg.max_position_area, ")")
            return False

        # Convert a list into an array
        obstacle_array = np.array(obstacle_array)
        obstacle_array = np.transpose(obstacle_array)

        # Convert string into fields number
        for i in range(abscissa_size):
            for j in range(ordinate_size):
                for k in range(len(cfg.obstacle_types_list)):
                    if obstacle_array[i, j] == \
                            cfg.obstacle_types_list[k]:
                        break
                    if k == len(cfg.obstacle_types_list) - 1:
                        print(i, j)
                        print("Obstacle field import contains ",
                              "non-supported obstacle type:",
                              obstacle_array[i, j])
                        return False

        # Create Field object (no reliefs_array for now)
        Field(self.name, obstacle_array, obstacle_array)
        return True


###########################################################
###################### print(CLASS ########################
###########################################################
class PrintData:
    """Common base class for all data printing"""

    def __init__(self, data_type):
        if data_type == "Armors":
            self.print_armors()
        elif data_type == "Equipments":
            self.print_equipments()
        elif data_type == "Shields":
            self.print_shields()
        elif data_type == "MeleeWeapons":
            self.print_melee_weapons()
        elif data_type == "Ammo":
            self.print_ammo()
        elif data_type == "RangedWeapons":
            self.print_ranged_weapons()
        elif data_type == "Characters":
            self.print_characters()
        elif data_type == "CharactersCharacteristics":
            self.print_characteristics()
        elif data_type == "Teams":
            self.print_teams()
        else:
            print("Type:", data_type, "is not recognized.",
                  "No data has been imported")

    def print_equipments(self):
        print("All equipments:")
        for i in range(len(cfg.equipments_list)):
            cfg.equipments_list[i].print_obj()

    def print_armors(self):
        print("All armors:")
        for i in range(len(cfg.equipments_list)):
            if isinstance(cfg.equipments_list[i], Armors):
                cfg.equipments_list[i].print_obj()

    def print_shields(self):
        print("All shields:")
        for i in range(len(cfg.equipments_list)):
            if isinstance(cfg.equipments_list[i], Shields):
                cfg.equipments_list[i].print_obj()

    def print_melee_weapons(self):
        print("All melee weapons:")
        for i in range(len(cfg.equipments_list)):
            if isinstance(cfg.equipments_list[i], MeleeWeapons):
                cfg.equipments_list[i].print_obj()

    def print_ammo(self):
        print("All ammo:")
        for i in range(len(cfg.equipments_list)):
            if isinstance(cfg.equipments_list[i], Ammo):
                cfg.equipments_list[i].print_obj()

    def print_ranged_weapons(self):
        print("All ranged weapons:")
        for i in range(len(cfg.equipments_list)):
            if isinstance(cfg.equipments_list[i], RangedWeapons):
                cfg.equipments_list[i].print_obj()

    def print_characters(self):
        print("All characters:")
        for i in range(len(cfg.char_list)):
            cfg.char_list[i].print_obj()

    def print_characteristics(self):
        print("All characters state:")
        for i in range(len(cfg.char_list)):
            cfg.char_list[i].print_characteristics()

    def print_teams(self):
        print("All teams:")
        for i in range(len(cfg.team_list)):
            cfg.team_list[i].print_obj()

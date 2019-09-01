import copy as copy
from sources.character.Characters import Characters


#############################################################
##################### TEAMS CLASS ###########################
#############################################################
class Teams:
    """Common base class for all teams"""
    list = []

    def __init__(self, name, characters_name_list):
        for team in Teams.list:
            if team.name == name:
                print("(Teams) Team creation failed because the name:", name, "is already used !")
                exit(0)
        self.name = name

        self.characters_list = []
        for name in characters_name_list:
            char_found = False
            for char in Characters.list:
                if name == char.name:
                    self.characters_list.append(char)
                    char_found = True
                    break
            if not char_found:
                print("(Teams) Team creation failed because the character name:", name, "cannot be found !")
                exit(0)

        self.ID = len(Teams.list)
        Teams.list.append(self)

    def get_id(self):
        return self.ID

    #################### BASIC FUNCTIONS ########################
    def is_life_active(self):
        for char in self.characters_list:
            if char.body.is_life_active():
                return True
        return False

    def is_alive(self):
        for char in self.characters_list:
            if char.body.is_alive():
                return True
        return False

    def is_positioned(self):
        # List to keep an historic of all positions
        abscissa_list = []
        ordinate_list = []

        # Check on all members of a team
        for char in self.characters_list:

            # Test if a position is set or not
            if char.check_position() is False:
                print("(Teams) Character:")
                char.print_position()
                print("is not positioned")
                return False

            # Test if a position is taken or not
            for j in range(len(abscissa_list)):
                if char.abscissa == abscissa_list[j] and char.ordinate == ordinate_list[j]:
                    print("(Teams) Character:")
                    char.print_position()
                    print("is using a position already taken")
                    return False

            # add the current position for historic
            abscissa_list.append(char.abscissa)
            ordinate_list.append(char.ordinate)

        # all positions are correctly set
        return True

    ################ PRINTING FUNCTIONS ########################
    def print_obj(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            print("\\", end=' ')
            char.print_basic()
            print("\\")

    def print_positions(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            print("\\")
            char.print_position()

    def print_alive_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            if char.body.state != "Dead":
                print("\\", end=' ')
                char.print_state()

    def print_dead_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            if char.body.state == "Dead":
                print("\\", end=' ')
                char.print_state()

    def print_all_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            print("\\", end=' ')
            char.print_state()

    def print_alive_defense_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            if char.body.state != "Dead":
                print("\\", end=' ')
                char.print_defense_state()

    def print_all_defense_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            print("\\", end=' ')
            char.print_defense_state()

    def print_alive_attack_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            if char.body.state != "Dead":
                print("\\", end=' ')
                char.print_state()

    def print_all_attack_states(self):
        print("Team name:", self.name, ", Team members:")
        for char in self.characters_list:
            print("\\", end=' ')
            char.print_attack_state()

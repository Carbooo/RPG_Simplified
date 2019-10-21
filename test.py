import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from data.import_data import ImportData
from sources.fight.fight import Fight


##################### SET UP ###################
ImportData("Armors", "data/Armors.csv")
ImportData("Shields", "data/Shields.csv")
ImportData("MeleeWeapons", "data/MeleeWeapons.csv")
ImportData("Ammo", "data/Ammo.csv")
ImportData("RangedWeapons", "data/RangedWeapons.csv")
ImportData("Characters", "data/Characters.csv")
ImportData("Teams", "data/Teams.csv")
ImportData("ObstaclesField", "data/maps/Short.csv")
ImportData("ObstaclesField", "data/maps/ShortObstacles.csv")
ImportData("ObstaclesField", "data/maps/TwoBridges.csv")
ImportData("ObstaclesField", "data/maps/LongObstacles.csv")


##################### TESTING ###################
def test_melee1():  # Big def vs Big attack
    func.log_level = 1
    func.automatic = False
    func.log_debug = True
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[9])


def test_melee2():  # Big def vs Big def
    func.log_level = 1
    func.automatic = False
    func.log_debug = True
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[10])


def test_melee3():  # Medium def vs Medium def
    func.log_level = 1
    func.automatic = False
    func.log_debug = True
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[11], cfg.team_list[12])


def test_melee_vs_ranged1():  # Small shield vs bow
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.actions = ["EQP", 244, "EQP", 27, 28,
                    "MOV", 0, 0, "MOV", 11, 5,
                    "REL", "PAS", 100, "REL", "RAT", 2,
                    "REL", "PAS", 100, "REL", "RAT", 2,
                    "REL", "PAS", 100, "REL", "RAT", 2,
                    "REL", "PAS", 100, "REL", "RAT", 2,
                    "REL", "PAS", 100, "REL", "RAT", 2
                    ]
    Fight(cfg.field_list[0], cfg.team_list[11], cfg.team_list[15])


def test_melee_vs_ranged2():  # Big shield vs bow
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.actions = ["EQP", 244, "EQP", 24, 25,
                    "MOV", 0, 0, "MOV", 11, 5,
                    "REL", "PAS", 100, "REL", "RAT", 1,
                    "REL", "PAS", 100, "REL", "RAT", 1,
                    "REL", "PAS", 100, "REL", "RAT", 1,
                    "REL", "PAS", 100, "REL", "RAT", 1,
                    "REL", "PAS", 100, "REL", "RAT", 1
                    ]
    Fight(cfg.field_list[0], cfg.team_list[13], cfg.team_list[15])


def test_ranged():
    func.log_level = 1
    func.automatic = False
    func.log_debug = True
    func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[14], cfg.team_list[15])


def test_magic():
    func.log_level = 1
    func.automatic = False
    func.log_debug = True
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[16], cfg.team_list[17])


test_melee_vs_ranged2()

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
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.action0 = ["EQP", 314, 315, "PAS", 1,
                    "MAT", 24, "MAT", 24,
                    "MAT", 24, "MAT", 24,
                    "MAT", 24, "MAT", 24,
                    "MAT", 24, "MAT", 24,
                    "MAT", 24, "MAT", 24
                    ]
    func.action1 = ["EQP", 317, "PAS", 4,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23
                    ]
    func.actions = {"t0": func.action0, "t1": func.action1}
    Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[9])


def test_melee2():  # Big def vs Big def
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.action0 = ["EQP", 314, 315, "PAS", 1,
                    "MAT", 25, "MAT", 25,
                    "MAT", 25, "MAT", 25,
                    "MAT", 25, "MAT", 25,
                    "MAT", 25, "MAT", 25,
                    "MAT", 25, "MAT", 25
                    ]
    func.action1 = ["EQP", 319, 320,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23,
                    "MAT", 23, "MAT", 23
                    ]
    func.actions = {"t0": func.action0, "t2": func.action1}
    Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[10])


def test_melee3():  # Medium def vs Medium def
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.action0 = ["MOV", 5, 3, "PAS", 5, "EQP", 34, 35, "PAS", 5,
                    "MAT", 2, "MAT", 2,
                    "MAT", 2, "MAT", 2,
                    "MAT", 2, "MAT", 2,
                    "MAT", 2, "MAT", 2,
                    "MAT", 2, "MAT", 2
                    ]
    func.action1 = ["EQP", 27, 28, "PAS", 5, "MOV", 6, 3, "PAS", 5,
                    "MAT", 5, "MAT", 5,
                    "MAT", 5, "MAT", 5,
                    "MAT", 5, "MAT", 5,
                    "MAT", 5, "MAT", 5,
                    "MAT", 5, "MAT", 5
                    ]
    func.actions = {"a4": func.action0, "a1": func.action1}
    Fight(cfg.field_list[0], cfg.team_list[11], cfg.team_list[12])


def test_melee_vs_ranged1():  # Small shield vs bow
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.action0 = ["EQP", 244, "MOV", 0, 0,
                    "REL", "RAT", 2,
                    "REL", "RAT", 2,
                    "REL", "RAT", 2,
                    "REL", "RAT", 2,
                    "REL", "RAT", 2
                    ]
    func.action1 = ["EQP", 27, 28, "MOV", 11, 5,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100
                    ]
    func.actions = {"r1": func.action0, "a1": func.action1}
    Fight(cfg.field_list[0], cfg.team_list[11], cfg.team_list[15])


def test_melee_vs_ranged2():  # Big shield vs bow
    func.log_level = 3
    func.automatic = True
    func.log_debug = True
    func.action0 = ["EQP", 244, "MOV", 0, 0,
                    "REL", "RAT", 1,
                    "REL", "RAT", 1,
                    "REL", "RAT", 1,
                    "REL", "RAT", 1,
                    "REL", "RAT", 1
                    ]
    func.action1 = ["EQP", 24, 25, "MOV", 11, 5,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100,
                    "PAS", 100, "PAS", 100
                    ]
    func.actions = {"r1": func.action0, "a0": func.action1}
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


test_melee3()

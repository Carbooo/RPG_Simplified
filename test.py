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
def test_melee():
    func.log_level = 1
    func.automatic = False
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[9])


def test_ranged():
    func.log_level = 1
    func.automatic = False
    func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[10], cfg.team_list[11])


def test_magic():
    func.log_level = 1
    func.automatic = False
    # func.actions = ["EQP", 236]
    Fight(cfg.field_list[0], cfg.team_list[12], cfg.team_list[13])


Fight(cfg.field_list[0], cfg.team_list[8], cfg.team_list[9])

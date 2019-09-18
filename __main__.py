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
ImportData("ObstaclesField", "data/Short.csv")
ImportData("ObstaclesField", "data/ShortObstacles.csv")
ImportData("ObstaclesField", "data/TwoBridges.csv")
ImportData("ObstaclesField", "data/LongObstacles.csv")

##################### FIGHT #####################
func.log_level = 1

Fight(cfg.field_list[3], cfg.team_list[0], cfg.team_list[1])  # Melee vs Ranged
# Fight(cfg.field_list[0], cfg.team_list[10], cfg.team_list[11])
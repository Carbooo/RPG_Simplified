from sources.miscellaneous.import_data import ImportData
from sources.fight.fight import Fight
import sources.miscellaneous.configuration as cfg

ImportData("Armors", "data/Armors.csv")
# PrintData("Armors")

print("")
ImportData("Shields", "data/Shields.csv")
# PrintData("Shields")

print("")
ImportData("MeleeWeapons", "data/MeleeWeapons.csv")
# PrintData("MeleeWeapons")

print("")
ImportData("Ammo", "data/Ammo.csv")
# PrintData("Ammo")

print("")
ImportData("RangedWeapons", "data/RangedWeapons.csv")
# PrintData("RangedWeapons")

print("")
# PrintData("Equipments")

print("")
ImportData("Characters", "data/Characters.csv")
# PrintData("Characters")
# PrintData("CharactersCharacteristics")

print("")
ImportData("Teams", "data/Teams.csv")
# PrintData("Teams")

print("")
ImportData("ObstaclesField", "data/Short.csv")
ImportData("ObstaclesField", "data/ShortObstacles.csv")
ImportData("ObstaclesField", "data/TwoBridges.csv")
ImportData("ObstaclesField", "data/LongObstacles.csv")
# Fields.list[0].print_obj()

print("")
# Fights(Fields.list[3], Teams.list[0], Teams.list[1])
# Fights(Fields.list[0], Teams.list[8], Teams.list[9])
Fight(cfg.field_list[0], cfg.team_list[10], cfg.team_list[11])
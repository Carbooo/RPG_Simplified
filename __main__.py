from sources.miscellaneous.ImportData import ImportData
from sources.root.fight.Fields import Fields
from sources.root.fight.Teams import Teams
from sources.root.fight.Fights import Fights

ImportData("Armors", "data\\Armors.csv")
# PrintData("Armors")

print("")
ImportData("Shields", "data\\Shields.csv")
# PrintData("Shields")

print("")
ImportData("MeleeWeapons", "data\\MeleeWeapons.csv")
# PrintData("MeleeWeapons")

print("")
ImportData("Ammo", "data\\Ammo.csv")
# PrintData("Ammo")

print("")
ImportData("RangedWeapons", "data\\RangedWeapons.csv")
# PrintData("RangedWeapons")

print("")
# PrintData("Equipments")

print("")
ImportData("Characters", "data\\Characters.csv")
# PrintData("Characters")
# PrintData("CharactersCharacteristics")

print("")
ImportData("Teams", "data\\Teams.csv")
# PrintData("Teams")

print("")
ImportData("ObstaclesField", "data\\Short.csv")
ImportData("ObstaclesField", "data\\ShortObstacles.csv")
ImportData("ObstaclesField", "data\\TwoBridges.csv")
ImportData("ObstaclesField", "data\\LongObstacles.csv")
# Fields.list[0].print_obj()

print("")
# Fights(Fields.list[3], Teams.list[0], Teams.list[1])
Fights(Fields.list[0], Teams.list[9], Teams.list[10])
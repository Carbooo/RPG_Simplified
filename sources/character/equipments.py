import copy as copy
import math as math
import random as random
import time as time


#############################################################
################## EQUIPMENTS CLASS #########################
#############################################################
class Equipments:
    """Common base class for all equipments"""
    list = []
    instances_count = 0
    armor_def_malus_rate = 0.1  # Armor def lost when being hit
    shield_def_malus_rate = 0.01  # Armor def lost when defending
    attack_weapon_def_malus_rate = 0.01  # Attack weapon def lost when defending
    variance = 0.5  # Gauss variance for equipment to break

    def __init__(self, name, load, bulk, resistance):
        for equip in Equipments.list:
            if equip.name == name:
                print("(Equipments) Equipment creation failed because the name:", name, "is already used !")
                exit(0)
    
        self.name = name
        self.type = "None"
        self.original_life = 100.0
        self.life = self.original_life
        self.original_load = float(load)
        self.load = self.original_load
        self.original_bulk = float(bulk)
        self.bulk = self.original_bulk
        self.original_resistance = float(resistance)
        self.resistance = self.original_resistance
        
        self.ID = Equipments.instances_count
        Equipments.instances_count += 1
        self.original_i_d = len(Equipments.list)
        Equipments.list.append(self)
        
    
    def print_obj(self):
        print("ID:", self.get_id(), ", Name:", self.name, ", Type:", \
            self.type, ", Life:", round(self.life), ", Load:", \
            round(self.load, 1), ", Bulk:", round(self.bulk, 1), \
            ", Resistance:", round(self.resistance, 1), end=' ')
    
    
    def get_id(self):
        return self.ID
    
            
    def copy(self):
        equip = copy.copy(self)
        if equip.ID != 0:
            equip.ID = Equipments.instances_count
            Equipments.instances_count += 1
        return equip
    
    
    def decrease(self, damage, def_malus_rate):
        decrease = min(self.life, max(0, random.gauss(1, Equipments.variance)) \
            * damage  * def_malus_rate / self.resistance_ratio())
        self.life -= decrease
        print("decrease", decrease)
        
        if self.is_broken():
            self.life = 0
            self.resistance = 0        
            self.load = 0
            self.bulk = 0
            return 0
        else:
            ratio = self.life / self.original_life
            self.resistance = self.original_resistance * math.pow(ratio, 1.0/2)
            self.load = self.original_load * math.pow(ratio, 1.0/2)
            self.bulk = self.original_bulk * math.pow(ratio, 1.0/2)
            return ratio
    
        
    def is_broken(self):
        if self.life <= 0 or random.gauss(self.life, Equipments.variance * 10) <= 0:
            return True
        else:
            return False
    
        
    def resistance_ratio(self):
        return max(0.05, self.original_resistance / 10)    


#############################################################
#################### ARMORS CLASS ###########################
#############################################################
class Armors(Equipments):
    'Common sub class of equipments for all armors'
    
    def __init__(self, name, load, bulk, resistance, def_cover, defense):
        Equipments.__init__(self, name, load, bulk, resistance)
        self.type = "Armor"
        self.original_def_cover = float(def_cover)
        self.def_cover = self.original_def_cover
        self.original_defense = float(defense)
        self.defense = self.original_defense
        
    def print_obj(self):
        Equipments.print_obj(self)
        print(", DefCover:", round(self.def_cover, 1), ", Defense:", round(self.defense, 1))
        

    def decrease(self, damage):
        ratio = Equipments.decrease(self, damage, Equipments.armor_def_malus_rate)
        self.def_cover = self.original_def_cover * math.pow(ratio, 1.0/2)
        self.defense = self.original_defense * math.pow(ratio, 1.0/2)
        return ratio
    
        
    def cover_ratio(self):
        return self.def_cover / 10
    
    
    def damage_absorbed(self, damage, armor_coef, resis_dim_rate, pen_rate):
        if armor_coef == 0:
            #The armor did not cover the attack
            return [1, damage] #1 = Not broken ratio
        
        damage_result = damage * pen_rate + max(0, damage * (1 -pen_rate) - self.defense * armor_coef)
        if damage_result <= 0:
            print("Damages absorbed by armor:", int(round(damage * (1 -pen_rate))))
            time.sleep(2)
            ratio = self.decrease(damage * armor_coef * resis_dim_rate)
            print("The armor has absorbed the remaining damages and no life has been lost")
            time.sleep(3)
            return [ratio, 0]
        else:
            print("Damages absorbed by armor:", int(round(min(damage * (1 - pen_rate), self.defense * armor_coef))))
            time.sleep(2)
            ratio = self.decrease(self.defense * armor_coef * resis_dim_rate)
            return [ratio, damage_result]
        
    
    def is_none_armor(self):
        if self.name == "--none_armor--":
            return True
        return False
            

#############################################################
##################### WEAPONS CLASS #########################
#############################################################
class Weapons(Equipments):
    'Common sub class of equipments for all weapons'

    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range):
        #Defense is managed in one parameter only (all characteristics, except resistance, are merged)
        #Attack is managed in several parameters (melee_power, pen_rate, resis_dim_rate, melee_handiness, melee_range)
        Equipments.__init__(self, name, load, bulk, resistance)
        self.hand = hand
        self.original_defense = float(defense)
        self.defense = self.original_defense
        self.original_melee_power = float(melee_power)
        self.melee_power = self.original_melee_power
        self.original_pen_rate = float(pen_rate) / 100.0
        self.pen_rate = self.original_pen_rate
        self.original_resis_dim_rate = float(resis_dim_rate) / 100.0
        self.resis_dim_rate = self.original_resis_dim_rate
        self.original_melee_handiness = float(melee_handiness)
        self.melee_handiness = self.original_melee_handiness
        self.original_melee_range = float(melee_range)
        self.melee_range = self.original_melee_range
    
        
    def print_obj(self):
        Equipments.print_obj(self)
        print(", Hand:", self.hand, ", Defense:", round(self.defense, 1), \
            ", Melee power:", round(self.melee_power, 1), ", Penetration rate:", \
            round(self.pen_rate, 2), ", Resistance dim. rate:", \
            round(self.resis_dim_rate, 2), ", Melee handiness:", \
            round(self.melee_handiness, 1), ", Melee range:", \
            round(self.melee_range, 1),  end=' ')
    
        
    def decrease(self, damage, def_malus_rate):
        ratio = Equipments.decrease(self, damage, def_malus_rate)
        self.defense = self.original_defense * math.pow(ratio, 1.0/3)
        self.melee_power = self.original_melee_power * math.pow(ratio, 1.0/3)
        self.pen_rate = self.original_pen_rate * math.pow(ratio, 1.0/4)
        self.resis_dim_rate = self.original_resis_dim_rate * math.pow(ratio, 1.0/4)
        self.melee_handiness = self.original_melee_handiness * math.pow(ratio, 1.0/4)
        self.melee_range = self.original_melee_range * math.pow(ratio, 1.0/4)
        return ratio


#############################################################
##################### SHIELDS CLASS #########################
#############################################################
class Shields(Weapons):
    'Common sub class of weapons for all shields'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range):
        Weapons.__init__(self, name, load, bulk, resistance, hand, defense, \
            melee_power, pen_rate, resis_dim_rate, melee_handiness, melee_range)
        self.type = "Shield"
    
        
    def print_obj(self):
        Weapons.print_obj(self)
        print("")


    def decrease(self, damage):
        ratio = Weapons.decrease(self, damage, Equipments.shield_def_malus_rate)
        return ratio
    

#############################################################
################## ATTACK WEAPONS CLASS #####################
#############################################################
class AttackWeapons(Weapons):
    'Common sub class of weapons for all attack weapons'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range):
        Weapons.__init__(self, name, load, bulk, resistance, hand, defense, \
            melee_power, pen_rate, resis_dim_rate, melee_handiness, melee_range)
    
        
    def print_obj(self):
        Weapons.print_obj(self)


    def decrease(self, damage):
        ratio = Weapons.decrease(self, damage, Equipments.attack_weapon_def_malus_rate)
        return ratio


#############################################################
################## MELEE WEAPONS CLASS ######################
#############################################################
class MeleeWeapons(AttackWeapons):
    'Common sub class of attack weapons for all melee weapons'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range):
        AttackWeapons.__init__(self, name, load, bulk, resistance, hand, defense, \
            melee_power, pen_rate, resis_dim_rate, melee_handiness, melee_range)
        self.type = "MeleeWeapon"
    
        
    def print_obj(self):
        AttackWeapons.print_obj(self)
        print("")
    
            
    def decrease(self, damage):
        ratio = AttackWeapons.decrease(self, damage)
        return ratio


#############################################################
######################## AMMO CLASS #########################
#############################################################
class Ammo(Equipments):
    'Common sub class of equipments for all ammo'
    
    def __init__(self, name, load, bulk, resistance, ranged_weapon_type, stability, \
    flesh_damage, pen_rate, resis_dim_rate):
        Equipments.__init__(self, name, load, bulk, resistance)
        self.type = "Arrow"
        self.original_stability = float(stability)
        self.stability = self.original_stability
        self.original_flesh_damage = float(flesh_damage)
        self.flesh_damage = self.original_flesh_damage
        self.original_pen_rate = float(pen_rate) / 10.0
        self.pen_rate = self.original_pen_rate
        self.original_resis_dim_rate = float(resis_dim_rate) / 10.0
        self.resis_dim_rate = self.original_resis_dim_rate
        self.ranged_weapon_type = False
        if ranged_weapon_type == "Bow":
            self.ranged_weapon_type = Bows
        elif ranged_weapon_type == "Crossbow":
            self.ranged_weapon_type = Crossbows
    
    
    def print_obj(self):
        Equipments.print_obj(self)
        print(", stability:", round(self.stability, 1), \
            ", flesh damage:", round(self.flesh_damage, 1), \
            ", Penetration rate:", round(self.pen_rate, 2))
            
    
    def decrease(self, damage):
        ratio = Equipments.decrease(self, damage)
        self.stability = self.original_stability * math.pow(ratio, 1.0/3)
        self.flesh_damage = self.original_flesh_damage * math.pow(ratio, 1.0/2)
        self.pen_rate = self.original_pen_rate * math.pow(ratio, 1.0/2)
        return ratio
    
    
    def stability_ratio(self):
        return self.stability / 10.0
                
                
#############################################################
################## RANGED WEAPONS CLASS #####################
#############################################################
class RangedWeapons(AttackWeapons):
    'Common sub class of attack weapons for all ranged weapons'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range, range_power, \
    accuracy, reload_time):
        AttackWeapons.__init__(self, name, load, bulk, resistance, hand, defense, \
            melee_handiness, melee_range, melee_power, pen_rate, resis_dim_rate)
        self.type = "RangedWeapon"
        self.original_range_power = float(range_power)
        self.range_power = self.original_range_power
        self.original_accuracy = float(accuracy)
        self.accuracy = self.original_accuracy
        self.reload_time = reload_time
        self.current_ammo = None

    def print_obj(self):
        AttackWeapons.print_obj(self)
        print(", RangePower:", round(self.range_power, 1), ", Accuracy:", round(self.accuracy, 1),
              ", MaxRange:", self.get_max_range(), ", ReloadTime:", round(self.reload_time, 1), ", Ammo:", end=' ')
        if self.current_ammo:
            print(self.current_ammo.name, end=' ')
        else:
            print("--None--", end=' ')
    
    def decrease(self, damage):
        ratio = AttackWeapons.decrease(self, damage)
        self.accuracy = self.original_accuracy * math.pow(ratio, 1.0/3)
        return ratio

    def is_reloaded(self):
        if self.current_ammo:
            return True
        else:
            return False

    def reload(self, ammo):
        self.current_reload = self.reload_time
        if (isinstance(ammo, Ammo)):
            self.current_ammo = ammo
        else:
            print("(Equipments) Error, parameter (", ammo, ") is not an ammo")

    def unload(self):
        self.current_reload = 0
        ammo_used = self.current_ammo 
        self.current_ammo = None
        return ammo_used
        
    def get_accuracy(self):
        if not self.current_ammo:
            return 0.0
        else:
            return self.accuracy * self.current_ammo.stability_ratio()
        
    def get_accuracy_ratio(self):
        return self.get_accuracy() / 10.0

    def get_max_range(self):
        if not self.current_ammo:
            return 0.0
        else:
            return math.pow(self.current_ammo.stability_ratio(), 1.0 / 1.75) * 10 \
                * self.get_accuracy_ratio() 


#############################################################
####################### BOW CLASS ###########################
#############################################################
class Bows(RangedWeapons):
    'Common sub class of attack weapons for all ranged weapons'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range, range_power, \
    accuracy, reload_time):
        RangedWeapons.__init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
            pen_rate, resis_dim_rate, melee_handiness, melee_range, range_power, \
            accuracy, reload_time)
        self.type = "Bow"
        
    
    def print_obj(self):
        RangedWeapons.print_obj(self)
        print("")


#############################################################
##################### CROSSBOW CLASS ########################
#############################################################
class Crossbows(RangedWeapons):
    'Common sub class of attack weapons for all ranged weapons'
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
    pen_rate, resis_dim_rate, melee_handiness, melee_range, range_power, \
    accuracy, reload_time):
        RangedWeapons.__init__(self, name, load, bulk, resistance, hand, defense, melee_power, \
            pen_rate, resis_dim_rate, melee_handiness, melee_range, range_power, \
            accuracy, reload_time)
        self.type = "Crossbow"
        
    
    def print_obj(self):
        RangedWeapons.print_obj(self)
        print("")

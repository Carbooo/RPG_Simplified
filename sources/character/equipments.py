import copy as copy
import math as math
import random as random
import time as time
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
################## EQUIPMENTS CLASS #########################
#############################################################
class Equipments:
    """Common base class for all equipments"""

    def __init__(self, name, load, bulk, resistance):
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
        self.ID = len(cfg.equipments_list) + 1
        cfg.equipments_list.append(self)
    
    def print_obj(self):
        func.optional_print("ID:", self.get_id(), ", Name:", self.name, ", Type:",
              self.type, ", Life:", round(self.life), ", Load:",
              round(self.load, 1), ", Bulk:", round(self.bulk, 1),
              ", Resistance:", round(self.resistance, 1), skip_line=True)
    
    def get_id(self):
        return self.ID
    
    def copy(self):
        equip = copy.copy(self)
        equip.ID = len(cfg.equipments_list)
        cfg.equipments_list.append(equip)
        return equip
    
    def decrease(self, damage, def_malus_rate):
        decrease = min(self.life, max(0, random.gauss(1, cfg.high_variance)) \
            * damage  * def_malus_rate / self.resistance_ratio())
        self.life -= decrease
        
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
        if self.life <= 0 or random.gauss(self.life, cfg.high_variance * 10) <= 0:
            return True
        else:
            return False
    
        
    def resistance_ratio(self):
        return max(0.05, self.original_resistance / 10)    


#############################################################
#################### ARMORS CLASS ###########################
#############################################################
class Armors(Equipments):
    """Common sub class of equipments for all armors"""
    
    def __init__(self, name, load, bulk, resistance, def_cover):
        super().__init__(name, load, bulk, resistance)
        self.type = "Armor"
        self.original_def_cover = float(def_cover)
        self.def_cover = self.original_def_cover
        self.original_defense = self.resistance * 10.0
        self.defense = self.original_defense
        
    def print_obj(self):
        super().print_obj()
        func.optional_print(", DefCover:", round(self.def_cover, 1), ", Defense:", round(self.defense, 1))

    def decrease(self, damage):
        ratio = super().decrease(damage, cfg.armor_def_malus_rate)
        self.def_cover = self.original_def_cover * math.pow(ratio, 1.0/2)
        self.defense = self.original_defense * math.pow(ratio, 1.0/2)
        return ratio

    def cover_ratio(self):
        return self.def_cover / 10.0

    def damage_absorbed(self, damages, armor_coef, damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        pen_damages = damages * pen_rate
        defense_value = self.defense * armor_coef
        remaining_damages_ratio = max(0, (1 - defense_value / pen_damages))
        direct_life_damages = damages * remaining_damages_ratio * damage_life_rate
        ignoring_armor_damages = damages * (1 - remaining_damages_ratio) * ignoring_armor_rate * (1 - pen_rate)
        absorbed_damages = damages - direct_life_damages - ignoring_armor_damages
        total_damages = direct_life_damages + ignoring_armor_damages

        func.optional_print("pen_damages", pen_damages, level=3, debug=True)
        func.optional_print("defense_value", defense_value, level=3, debug=True)
        func.optional_print("remaining_damages_ratio", remaining_damages_ratio, level=3, debug=True)
        func.optional_print("direct_life_damages", direct_life_damages, level=3, debug=True)
        func.optional_print("ignoring_armor_damages", ignoring_armor_damages, level=3, debug=True)
        func.optional_print("Damages absorbed by", self.name, ":", int(round(absorbed_damages)), level=3)
        time.sleep(2)
        ratio = self.decrease(absorbed_damages * resis_dim_rate)
            
        if total_damages == 0:
            func.optional_print("The", self.name, "has absorbed the damages and no life has been lost", level=3)
            time.sleep(3)
        
        return [ratio, total_damages]
            

#############################################################
#################### MAGICAL ARMORS CLASS ###################
#############################################################
class MagicalArmors(Armors):
    """Common sub class of equipments for all purely magical armors"""
    
    def __init__(self, name, resistance):
        super().__init__(name, 0.0, 0.0, resistance, 10.0)
        self.type = "MagicalArmor"
        
    def damage_absorbed(self, damage, armor_coef, damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        # Same parameters as parent for consistency
        ratio, damage_result = super().damage_absorbed(damage, 1, 0, 0, 1, 0)
        ratio = self.decrease(damage)
        return ratio, damage_result
    
    def decrease(self, damage):
        self.defense -= damage
        if self.defense <= 0:
            self.life = 0
            return 0
        else:
            return 1

        
#############################################################
######################## AMMO CLASS #########################
#############################################################
class Ammo(Equipments):
    """Common sub class of equipments for all ammo"""
    
    def __init__(self, name, load, bulk, resistance, ranged_weapon_type,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        super().__init__(name, load, bulk, resistance)
        self.type = "Arrow"
        self.original_damage_life_rate = float(damage_life_rate)
        self.damage_life_rate = self.original_damage_life_rate
        self.original_ignoring_armor_rate = float(ignoring_armor_rate) / 100.0
        self.ignoring_armor_rate = self.original_ignoring_armor_rate
        self.original_pen_rate = float(pen_rate) / 100.0
        self.pen_rate = self.original_pen_rate
        self.original_resis_dim_rate = float(resis_dim_rate) / 100.0
        self.resis_dim_rate = self.original_resis_dim_rate
        self.ranged_weapon_type = False
        if ranged_weapon_type == "Bow":
            self.ranged_weapon_type = Bows
        elif ranged_weapon_type == "Crossbow":
            self.ranged_weapon_type = Crossbows

    def print_obj(self):
        super().print_obj()
        func.optional_print(", Damage life rate:", round(self.damage_life_rate, 2),
                            ", Ignoring armor rate:", round(self.ignoring_armor_rate, 2),
                            ", Penetration rate:", round(self.pen_rate, 2),
                            ", Resistance dim rate:", round(self.resis_dim_rate, 2))

    def decrease(self, damage):
        ratio = super().decrease(self, damage)
        self.damage_life_rate = self.original_damage_life_rate * math.pow(ratio, 1.0/2)
        self.ignoring_armor_rate = self.original_ignoring_armor_rate * math.pow(ratio, 1.0 / 2)
        self.pen_rate = self.original_pen_rate * math.pow(ratio, 1.0/2)
        self.resis_dim_rate = self.original_resis_dim_rate * math.pow(ratio, 1.0/2)
        return ratio

                
#############################################################
##################### WEAPONS CLASS #########################
#############################################################
class Weapons(Equipments):
    """Common sub class of equipments for all weapons"""

    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        super().__init__(name, load, bulk, resistance)
        self.hand = hand
        self.original_defense = float(defense)
        self.defense = self.original_defense
        self.original_melee_power = float(melee_power)
        self.melee_power = self.original_melee_power
        self.original_melee_handiness = float(melee_handiness)
        self.melee_handiness = self.original_melee_handiness
        self.original_damage_life_rate = float(damage_life_rate)
        self.damage_life_rate = self.original_damage_life_rate
        self.original_ignoring_armor_rate = float(ignoring_armor_rate) / 100.0
        self.ignoring_armor_rate = self.original_ignoring_armor_rate
        self.original_pen_rate = float(pen_rate) / 100.0
        self.pen_rate = self.original_pen_rate
        self.original_resis_dim_rate = float(resis_dim_rate) / 100.0
        self.resis_dim_rate = self.original_resis_dim_rate
        self.attack_ratio = 1.0
        self.melee_defend_ratio = 1.0
        self.ranged_defend_ratio = 1.0
        self.magic_defend_ratio = 1.0

    def print_obj(self):
        super().print_obj()
        func.optional_print(", Hand:", self.hand,
                            ", Defense:", round(self.defense, 1),
                            ", Melee power:", round(self.melee_power, 1),
                            ", Melee handiness:", round(self.melee_handiness, 1),
                            ", Damage life rate:", round(self.damage_life_rate, 2),
                            ", Ignoring armor rate:", round(self.ignoring_armor_rate, 2),
                            ", Penetration rate:", round(self.pen_rate, 2),
                            ", Resistance dim. rate:", round(self.resis_dim_rate, 2), skip_line=True)
        
    def decrease(self, damage, def_malus_rate):
        ratio = super().decrease(damage, def_malus_rate)
        self.defense = self.original_defense * math.pow(ratio, 1.0/3)
        self.melee_power = self.original_melee_power * math.pow(ratio, 1.0/3)
        self.melee_handiness = self.original_melee_handiness * math.pow(ratio, 1.0/4)
        self.damage_life_rate = self.original_damage_life_rate * math.pow(ratio, 1.0/4)
        self.ignoring_armor_rate = self.original_ignoring_armor_rate * math.pow(ratio, 1.0/4)
        self.pen_rate = self.original_pen_rate * math.pow(ratio, 1.0/4)
        self.resis_dim_rate = self.original_resis_dim_rate * math.pow(ratio, 1.0/4)
        return ratio


#############################################################
##################### SHIELDS CLASS #########################
#############################################################
class Shields(Weapons):
    """Common sub class of weapons for all shields"""
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate)
        self.type = "Shield"
        
    def print_obj(self):
        super().print_obj()
        func.optional_print("")

    def decrease(self, damage):
        ratio = super().decrease(damage, cfg.shield_def_malus_rate)
        return ratio
    

#############################################################
##################### MAGICAL SHIELDS CLASS #################
#############################################################
class MagicalShields(Shields):
    """Common sub class of weapons for all shields"""
    
    def __init__(self, name, defense, attack_ratio, melee_def_ratio, ranged_def_ratio, magic_def_ratio):
        super().__init__(name, 0.0, 0.0, 0.0, 0, defense, 0.0, 0.0, 0.0, 0.0, 0.0,  0.0)
        self.type = "MagicalShield"
        self.attack_ratio = attack_ratio
        self.melee_defend_ratio = melee_def_ratio
        self.ranged_defend_ratio = ranged_def_ratio
        self.magic_defend_ratio = magic_def_ratio
        
    def print_obj(self):
        super().print_obj()
        func.optional_print("")

    def decrease(self, damage):
        return 1
    

#############################################################
################## ATTACK WEAPONS CLASS #####################
#############################################################
class AttackWeapons(Weapons):
    """Common sub class of weapons for all attack weapons"""
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                         damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate)
        self.ranged_defend_ratio = 0.0
        self.magic_defend_ratio = 0.0
        
    def print_obj(self):
        super().print_obj()

    def decrease(self, damage):
        ratio = super().decrease(damage, cfg.attack_weapon_def_malus_rate)
        return ratio


#############################################################
################## MELEE WEAPONS CLASS ######################
#############################################################
class MeleeWeapons(AttackWeapons):
    """Common sub class of attack weapons for all melee weapons"""

    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                         damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate)
        self.type = "MeleeWeapon"

    def print_obj(self):
        super().print_obj()
        func.optional_print("")

    def decrease(self, damage):
        ratio = super().decrease(damage)
        return ratio



#############################################################
################## RANGED WEAPONS CLASS #####################
#############################################################
class RangedWeapons(AttackWeapons):
    """Common sub class of attack weapons for all ranged weapons"""
    
    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate,
                 range_power, accuracy, reload_time):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                         damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate)
        self.type = "RangedWeapon"
        self.original_range_power = float(range_power)
        self.range_power = self.original_range_power
        self.original_accuracy = float(accuracy)
        self.accuracy = self.original_accuracy
        self.reload_time = reload_time
        self.current_ammo = None

    def print_obj(self):
        super().print_obj()
        func.optional_print(", RangePower:", round(self.range_power, 1), ", Accuracy:", round(self.accuracy, 1),
                            ", MaxRange:", self.get_range(), ", ReloadTime:", round(self.reload_time, 1),
                            ", Ammo:", skip_line=True)
        if self.current_ammo:
            func.optional_print(self.current_ammo.name,
                                ", DamageLifeRate:", round(self.damage_life_rate, 2),
                                ", IgnoringArmorRate:", round(self.ignoring_armor_rate, 2),
                                ", PenetrationRate:", round(self.pen_rate, 2),
                                ", ResistanceDimRate:", round(self.resis_dim_rate, 2))
        else:
            func.optional_print("--None--")
    
    def decrease(self, damage):
        ratio = super().decrease(damage)
        self.range_power = self.original_range_power * math.pow(ratio, 1.0/2.0)
        self.accuracy = self.original_accuracy * math.pow(ratio, 1.0/2.0)
        return ratio

    def is_reloaded(self):
        if self.current_ammo:
            return True
        else:
            return False

    def reload(self, ammo):
        if isinstance(ammo, Ammo):
            self.current_ammo = ammo
        else:
            func.optional_print("(Equipments) Error, parameter (", ammo, ") is not an ammo")

    def unload(self):
        ammo_used = self.current_ammo 
        self.current_ammo = None
        return ammo_used
        
    def get_accuracy_ratio(self):
        return self.accuracy / 10.0
        
    def get_range(self):
        # 1 range power = 20 meters
        # 1 case = 2 meters
        # range gives as number of cases
        return self.range_power * 10.0
        

#############################################################
####################### BOW CLASS ###########################
#############################################################
class Bows(RangedWeapons):
    """Common sub class for bows"""

    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate,
                 range_power, accuracy, reload_time):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                         damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate,
                         range_power, accuracy, reload_time)
        self.type = "Bow"


#############################################################
##################### CROSSBOW CLASS ########################
#############################################################
class Crossbows(RangedWeapons):
    """Common sub class of attack weapons for all ranged weapons"""

    def __init__(self, name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                 damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate,
                 range_power, accuracy, reload_time):
        super().__init__(name, load, bulk, resistance, hand, defense, melee_power, melee_handiness,
                         damage_life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate,
                         range_power, accuracy, reload_time)
        self.type = "Crossbow"

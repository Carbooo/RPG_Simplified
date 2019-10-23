import time as time
from sources.character.equipments import Armors, MagicalArmors, Weapons, MeleeWeapons, \
    Shields, MagicalShields, RangedWeapons, Bows, Crossbows, Ammo
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#########################################################################
########################## CHAR EQUIPMENTS CLASS ########################
#########################################################################
class CharEquipments:
    """Common base class for all equipments carried by a character"""

    def __init__(self, char, armor, 
                 weapon1, weapon2, weapon3, weapon4, 
                 ammo_type1, ammo_number1, ammo_type2, ammo_number2):
        self.character = char
        self.armors = []
        self.weapons_stored = []
        self.weapons_in_use = []
        self.ammo = []
        self.free_hands = 2
        
        self.set_armor(armor)

        weapon_list = [weapon1, weapon2, weapon3, weapon4]
        for weapon_name in weapon_list:
            if not weapon_name:
                continue
            else:
                self.set_weapon_in_stored(weapon_name)

        if ammo_type1:
            self.set_ammo(ammo_type1, ammo_number1)
        if ammo_type2:
            self.set_ammo(ammo_type2, ammo_number2)

    ############################### EQUIP FUNCTIONS ###############################
    def set_armor(self, armor_name):
        # Find armor
        armor_found = False
        for equip in cfg.equipments_list:
            if isinstance(equip, Armors) and equip.name == armor_name:
                armor_found = equip.copy()
                break

        # Set armor
        if armor_found is False:
            func.optional_print("(Bodies) Armor (", armor_name, ") has not been found and therefore cannot be set", level=3)
            return False
        else:
            self.armors.append(armor_found)
            return True

    def set_magical_armor(self, armor_name, armor_defense):
        new_armor = MagicalArmors(armor_name, armor_defense)
        # Put the new armor at the first position (first to receive damages)
        current_armors = self.armors.copy()
        self.armors = [new_armor]
        self.armors.extend(current_armors)
        return new_armor
    
    def remove_armor(self, armor):
        self.armors.remove(armor)
        return True

    def set_weapon_in_stored(self, weapon_name):
        # Find weapon
        weapon_found = False
        for equip in cfg.equipments_list:
            if isinstance(equip, Weapons) and equip.name == weapon_name:
                weapon_found = equip.copy()
                break

        # Check prerequisites
        if not weapon_found:
            func.optional_print("(Bodies) Weapon (", weapon_name, ") has not been found and therefore cannot be set", level=3)
            return False

        # Set weapon
        self.weapons_stored.append(weapon_found)
        return True
    
    def set_weapon_in_use(self, weapon):
        if self.free_hands < weapon.hand:
            func.optional_print("(Bodies) Weapon (", weapon.name, ") cannot be set, because there are not enough free hands", level=3)
            return False

        # Set weapon
        self.weapons_stored.remove(weapon)
        self.weapons_in_use.append(weapon)
        self.free_hands -= weapon.hand
        return True
        
    def set_magical_shield(self, name, defense, attack_ratio, melee_def_ratio, ranged_def_ratio, magic_def_ratio):
        new_shield = MagicalShields(name, defense, attack_ratio, melee_def_ratio, ranged_def_ratio, magic_def_ratio)
        self.set_weapon_in_use(new_shield)

    def remove_weapon(self, weapon, definitive=False):
        if weapon not in self.weapons_in_use:
            func.optional_print("(Bodies) Error, cannot remove weapon because it is not equiped", level=3)
            return False
        else:
            self.weapons_in_use.remove(weapon)
            self.free_hands += weapon.hand
            if not definitive:
                self.weapons_stored.append(weapon)
                if isinstance(weapon, Bows) and weapon.current_ammo:
                    self.ammo.append(weapon.current_ammo)
                    weapon.unload()
            return True
                
    def set_ammo(self, ammo_type, ammo_number):
        # Find ammo
        ammo_found = False
        for equip in cfg.equipments_list:
            if isinstance(equip, Ammo) and equip.name == ammo_type:
                ammo_found = equip.copy()
                break

        if ammo_found:
            for _ in range(ammo_number):
                self.ammo.append(ammo_found.copy())
            return True

        func.optional_print("(Bodies) Ammo cannot be set because ammo type (", ammo_type, ") has not been found !", level=3)
        return False

    ############################# DAMAGE FUNCTIONS #############################
    def get_armor_cover_ratio(self):
        if not self.armors:
            return 0
        else:
            return self.armors[0].def_cover

    def armor_damage_absorbed(self, damages, armor_coef, damages_coef, life_rate, ignoring_armor_rate, pen_rate, resis_dim_rate):
        damage_result = damages
        armors = self.armors.copy()
        for armor in armors:
            if damage_result > 0:
                result = armor.damage_absorbed(damage_result, armor_coef, damages_coef, life_rate,
                                               ignoring_armor_rate, pen_rate, resis_dim_rate)
                damage_result = result[1]
                if result[0] == 0:
                    func.optional_print("Your armor \\ID:", armor.get_id(), "\\Name:", armor.name, "has been broken!", level=3)
                    self.remove_armor(armor)
            else:
                break
            
        return damage_result
    
    def decay_magical_armor(self, armor, value):
        ratio = armor.decrease(value)
        if ratio == 0:
            self.remove_armor(armor)
            return True
        return False

    def all_weapons_absorbed_damage(self, damage, resis_dim_rate):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            try:
                defense += weapon.defense
                weapons_list.append(weapon)
            except:
                pass
        
        damage *= resis_dim_rate
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_melee_weapons_absorbed_damage(self, damage, resis_dim_rate):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, MeleeWeapons):
                defense += weapon.defense
                weapons_list.append(weapon)
        
        damage *= resis_dim_rate
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_shields_absorbed_damage(self, damage, resis_dim_rate):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                defense += weapon.defense
                weapons_list.append(weapon)
        
        damage *= resis_dim_rate
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def weapon_absorbed_damage(self, weapon, damage):
        if weapon.decrease(damage) == 0:
            func.optional_print("Your weapon \\ID:", weapon.get_id(), "\\Name:", weapon.name, "has been broken!", level=3)
            self.weapons_in_use.remove(weapon)

    ############################# RANGE FUNCTIONS ###########################
    def get_range(self):
        max_range = 10000
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                max_range = min(max_range, weapon.get_range())

        if max_range == 10000:
            return 0
        else:
            return max_range

    def has_ammo(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                if self.ranged_weapon_has_ammo(weapon):
                    return True
        return False
    
    def ranged_weapon_has_ammo(self, ranged_weapon):  
        for ammo in self.ammo:
            if ranged_weapon.__class__ == ammo.ranged_weapon_type:
                return True
        return False    

    def has_reloaded(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons) and not weapon.is_reloaded():
                return False
        return True

    def reload(self, weapon, ammo):
        weapon.print_obj()
        weapon.reload(ammo)
        self.ammo.remove(ammo)

    def get_current_ammo(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                return weapon.current_ammo

    def use_ammo(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                weapon.unload()
                break
        return True

    def loose_reloaded_ammo(self):
        has_lost = False
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Bows) and weapon.is_reloaded():
                has_lost = True
                weapon.unload()
                func.optional_print("Your bow has lost its loaded arrow!", level=2)
                func.optional_sleep(2)
        return has_lost

    ############################# TEST ON EQUIP ###########################
    def is_using_a_ranged_weapon(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                return True
        return False

    def is_using_a_crossbow(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Crossbows):
                return True
        return False

    def is_using_a_bow(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Bows):
                return True
        return False

    def is_using_a_shield(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                return True
        return False

    ############################# LOAD / BULK FUNCTIONS ###########################
    def get_full_load(self):
        load = 0.0
        for weapon in self.weapons_stored:
            load += weapon.load
        for weapon in self.weapons_in_use:
            load += weapon.load
        for armor in self.armors:
            load += armor.load
        return load

    def get_armor_load(self):
        load = 0.0
        for armor in self.armors:
            load += armor.load
        return load
    
    def get_stored_load(self):
        load = 0.0
        for weapon in self.weapons_stored:
            load += weapon.load
        return load

    def get_in_use_load(self):
        load = 0.0
        for weapon in self.weapons_in_use:
            load += weapon.load
        return load
    
    def get_full_bulk(self):
        bulk = 0
        for weapon in self.weapons_stored:
            bulk += weapon.bulk
        for weapon in self.weapons_in_use:
            bulk += weapon.bulk
        for armor in self.armors:
            bulk += armor.bulk
        return bulk

    def get_armor_bulk(self):
        bulk = 0.0
        for armor in self.armors:
            bulk += armor.load
        return bulk

    def get_stored_bulk(self):
        bulk = 0.0
        for weapon in self.weapons_stored:
            bulk += weapon.bulk
        return bulk

    def get_in_use_bulk(self):
        bulk = 0.0
        for weapon in self.weapons_in_use:
            bulk += weapon.bulk
        return bulk

    ########################## CHARACTERISTICS FUNCTIONS #########################
    def calculate_attack(self):
        attack_powers = {
            "melee_power": 0.0,
            "melee_handiness": 0.0,
            "range_power": 0.0,
            "range_accuracy": 0.0,
        }

        for weapon in self.weapons_in_use:
            attack_powers["melee_power"] += weapon.melee_power * weapon.attack_ratio
            attack_powers["melee_handiness"] += weapon.melee_handiness * weapon.attack_ratio
            if isinstance(weapon, RangedWeapons) and self.ranged_weapon_has_ammo(weapon):
                attack_powers["range_power"] += weapon.range_power * weapon.attack_ratio
                attack_powers["range_accuracy"] += weapon.accuracy * weapon.attack_ratio

        # Free hands melee attack power
        attack_powers["melee_power"] += self.free_hands * cfg.free_hand_melee_power
        attack_powers["melee_handiness"] += self.free_hands * cfg.free_hand_melee_handiness

        return attack_powers

    def calculate_defense(self):
        defenses = {
            "melee_defense": 0.0,
            "ranged_defense": 0.0,
            "magic_defense": 0.0  # Where shield can be used against magic attacks
        }

        for weapon in self.weapons_in_use:
            defenses["melee_defense"] += weapon.defense * weapon.melee_defend_ratio
            defenses["ranged_defense"] += weapon.defense * weapon.ranged_defend_ratio
            defenses["magic_defense"] += weapon.defense * weapon.magic_defend_ratio

        # Free hands melee defense
        defenses["melee_defense"] += self.free_hands * cfg.free_hand_melee_defense

        return defenses

    ########################## PRINTING FUNCTIONS #########################
    def print_armors(self):
        func.optional_print("   - Armors:")
        if not self.armors:
            func.optional_print("      \\No armor")
            return False
        for armor in self.armors:
            func.optional_print("      \\", skip_line=True)
            func.optional_print("ArmorID:", armor.get_id(), ", Armor:", armor.name, ", Defense:", round(armor.defense, 1))
        return True

    def print_full_armors(self):
        func.optional_print("   - Armors:")
        if not self.armors:
            func.optional_print("      \\No armor")
            return False
        for armor in self.armors:
            func.optional_print("      \\", skip_line=True)
            armor.print_obj()
        return True
        
    @staticmethod
    def print_weapon(weapon):
        if isinstance(weapon, RangedWeapons):
            func.optional_print("WeaponID:", weapon.get_id(), ", Weapon:", weapon.name, ", NbOfHand(s):", weapon.hand,
                                ", ReloadTime:", round(weapon.reload_time, 1),
                                ", RangePower:", round(weapon.range_power, 1),
                                ", Accuracy:", round(weapon.accuracy, 1), skip_line=True)

            if weapon.current_ammo is None:
                func.optional_print(", Reloaded: No")
            else:
                func.optional_print(", Reloaded: Yes",
                                    ", DamageLifeRate:", round(weapon.current_ammo.life_rate, 2),
                                    ", IgnoringArmorRate:", round(weapon.current_ammo.ignoring_armor_rate, 2),
                                    ", PenetrationRate:", round(weapon.current_ammo.pen_rate, 2))

        else:
            func.optional_print("WeaponID:", weapon.get_id(), ", Weapon:", weapon.name, ", NbOfHand(s):", weapon.hand,
                                ", Defense:", round(weapon.defense, 1),
                                ", MeleePower:", round(weapon.melee_power, 1),
                                ", MeleeHandiness:", round(weapon.melee_handiness, 1),
                                ", DamageLifeRate:", round(weapon.life_rate, 2),
                                ", IgnoringArmorRate:", round(weapon.ignoring_armor_rate, 2),
                                ", PenetrationRate:", round(weapon.pen_rate, 2))

    @staticmethod
    def print_full_weapon(weapon):
        weapon.print_obj()

    def print_weapons_stored(self):
        func.optional_print("   - Weapons stored:")
        if not self.weapons_stored:
            func.optional_print("      \\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            func.optional_print("      \\", skip_line=True)
            CharEquipments.print_weapon(weapon)
        return True

    def print_full_weapons_stored(self):
        func.optional_print("   - Weapons stored:")
        if not self.weapons_stored:
            func.optional_print("      \\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            func.optional_print("      \\", skip_line=True)
            CharEquipments.print_full_weapon(weapon)
        return True
    
    def print_weapons_in_use(self):
        func.optional_print("   - Weapons used:")
        if not self.weapons_in_use:
            func.optional_print("      \\No weapon used")
            return False
        for weapon in self.weapons_in_use:
            func.optional_print("      \\", skip_line=True)
            CharEquipments.print_weapon(weapon)
        return True

    def print_full_weapons_in_use(self):
        func.optional_print("   - Weapons used:")
        if self.weapons_in_use:
            func.optional_print("      \\No weapon used")
            return False
        for weapon in self.weapons_in_use:
            func.optional_print("      \\", skip_line=True)
            CharEquipments.print_full_weapon(weapon)
        return True
    
    def print_ammo(self):
        func.optional_print("   - Ammo available:")
        if not self.ammo:
            func.optional_print("      \\No ammo")
            return False

        ammo_type_list = {}
        for ammo in self.ammo:
            if ammo.name in ammo_type_list:
                ammo_type_list[ammo.name]["number"] += 1
            else:
                ammo_type_list[ammo.name] = {}
                ammo_type_list[ammo.name]["number"] = 1
                ammo_type_list[ammo.name]["ammo_type"] = ammo

        for key in ammo_type_list:
            func.optional_print("      \\", ammo_type_list[key]["number"], "arrow(s) of ...")
            func.optional_print("       ", skip_line=True)
            ammo_type_list[key]["ammo_type"].print_obj()
        return True

    def print_equipments(self):
        func.optional_print("-- EQUIPMENTS --")
        self.print_armors()
        self.print_weapons_in_use()
        self.print_weapons_stored()
        self.print_ammo()

    def print_full_equipments(self):
        func.optional_print("-- EQUIPMENTS --")
        self.print_full_armors()
        self.print_full_weapons_in_use()
        self.print_full_weapons_stored()
        self.print_ammo()

    def print_obj(self):
        self.print_equipments()

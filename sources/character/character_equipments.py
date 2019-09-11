from sources.character.equipments import Armors, MagicalArmors, Weapons, AttackWeapons, MeleeWeapons, \
    Shields, RangedWeapons, Bows, Crossbows, Ammo
import sources.miscellaneous.configuration as cfg


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
            print("(Bodies) Armor (", armor_name, ") has not been found and therefore cannot be set")
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
            print("(Bodies) Weapon (", weapon_name, ") has not been found and therefore cannot be set")
            return False

        # Set weapon
        self.weapons_stored.append(weapon_found)
        return True
    
    def set_weapon_in_use(self, weapon):
        if self.free_hands < weapon.hand:
            print("(Bodies) Weapon (", weapon.name, ") cannot be set, because there are not enough free hands")
            return False

        # Set weapon
        self.weapons_stored.remove(weapon)
        self.weapons_in_use.append(weapon)
        self.free_hands -= weapon.hand
        return True

    def remove_weapon(self, weapon, definitive=False):
        if weapon not in self.weapons_in_use:
            print("(Bodies) Error, cannot remove weapon because it is not equiped")
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

        print("(Bodies) Ammo cannot be set because ammo type (", ammo_type, ") has not been found !")
        return False

    ############################# DAMAGE FUNCTIONS #############################
    def get_armor_cover_ratio(self):
        if not self.armors:
            return 0
        else:
            return self.armors[0].def_cover

    def armor_damage_absorbed(self, damage, armor_coef, resistance_dim_rate, penetration_rate, flesh_dam_rate):
        damage_result = damage
        armors = self.armors.copy()
        for armor in armors:
            if damage_result > 0:
                result = armor.damage_absorbed(damage_result, armor_coef, resistance_dim_rate,
                                               penetration_rate, flesh_dam_rate)
                damage_result = result[1]
                if result[0] == 0:
                    print("Your armor \\ID:", armor.get_id(), "\\Name:", armor.name, "has been broken!")
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

    def all_weapons_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            try:
                defense += weapon.defense
                weapons_list.append(weapon)
            except:
                pass
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_melee_weapons_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, MeleeWeapons):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_shields_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def weapon_absorbed_damage(self, weapon, damage):
        if weapon.decrease(damage) == 0:
            print("Your weapon \\ID:", weapon.get_id(), "\\Name:", weapon.name, "has been broken!")
            self.weapons_in_use.remove(weapon)

    ############################# RANGE FUNCTIONS ###########################
    def get_range(self):
        max_range = 10000
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                max_range = min(max_range, weapon.get_max_range())

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
    def calculate_accuracies(self):
        accuracies = {
            "melee_weapons": 0.0,
            "ranged_weapons": 0.0
        }
        nb_of_weapon = 0.0

        for weapon in self.weapons_in_use:
            nb_of_weapon += 1.0
            accuracies["melee_weapons"] += weapon.melee_handiness
            if isinstance(weapon, RangedWeapons):
                accuracies["ranged_weapons"] += weapon.accuracy

        # Free hands melee power
        accuracies["melee_weapons"] += self.free_hands * cfg.free_hand_melee_handiness
        nb_of_weapon += self.free_hands

        accuracies["melee_weapons"] /= nb_of_weapon
        accuracies["ranged_weapons"] /= nb_of_weapon
        return accuracies

    def calculate_melee_range(self):
        melee_range = 0.0
        nb_of_weapon = 0.0
        for weapon in self.weapons_in_use:
            melee_range += weapon.melee_range
            nb_of_weapon += 1.0

        # Free hands melee range
        if self.free_hands == 2:
            melee_range = cfg.free_hand_melee_range
            nb_of_weapon = 1.0

        return melee_range / nb_of_weapon

    def calculate_attack_power(self):
        attack_powers = {
            "melee_power": 0.0,
            "ranged_power": 0.0,
            "pen_rate": 0.0,
            "resis_dim_rate": 0.0
        }
        nb_of_weapons = 0.0

        for weapon in self.weapons_in_use:
            nb_of_weapons += 1
            attack_powers["melee_power"] += weapon.melee_power
            attack_powers["pen_rate"] += weapon.pen_rate
            attack_powers["resis_dim_rate"] += weapon.resis_dim_rate
            if isinstance(weapon, RangedWeapons) and self.ranged_weapon_has_ammo(weapon):
                attack_powers["ranged_power"] += weapon.range_power

        # Free hands melee attack power
        attack_powers["melee_power"] += self.free_hands * cfg.free_hand_melee_power
        attack_powers["pen_rate"] += self.free_hands * cfg.free_hand_pen_rate
        attack_powers["resis_dim_rate"] += self.free_hands * cfg.free_hand_resis_dim_rate
        nb_of_weapons += self.free_hands

        attack_powers["pen_rate"] /= nb_of_weapons
        attack_powers["resis_dim_rate"] /= nb_of_weapons
        return attack_powers

    def calculate_defense(self):
        defenses = {
            "melee_defense": 0.0,
            "ranged_defense": 0.0,
            "magic_defense": 0.0  # Where shield can be used against magic attacks
        }

        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                defenses["melee_defense"] += weapon.defense
                defenses["ranged_defense"] += weapon.defense
                defenses["magic_defense"] += weapon.defense
            elif isinstance(weapon, AttackWeapons):
                defenses["melee_defense"] += weapon.defense

        # Free hands melee defense
        defenses["melee_defense"] += self.free_hands * cfg.free_hand_melee_defense

        return defenses

    ########################## PRINTING FUNCTIONS #########################
    def print_armors(self):
        print("   - Armors:")
        if not self.armors:
            print("      \\No armor")
            return False
        for armor in self.armors:
            print("      \\", end=' ')
            print("ArmorID:", armor.get_id(), ", Armor:", armor.name, ", Defense:", round(armor.defense, 1))
        return True

    def print_full_armors(self):
        print("   - Armors:")
        if not self.armors:
            print("      \\No armor")
            return False
        for armor in self.armors:
            print("      \\", end=' ')
            armor.print_obj()
        return True
        
    @staticmethod
    def print_weapon(weapon):
        print("WeaponID:", weapon.get_id(), ", Weapon:", weapon.name, ", Defense:", round(weapon.defense, 1),
              ", MeleePower:", round(weapon.melee_power, 1), ", NbOfHand(s):", weapon.hand, end=' ')
        
        if isinstance(weapon, RangedWeapons):
            if weapon.current_ammo is not None:
                ammo_name = weapon.current_ammo.name
            else:
                ammo_name = None
            print(", MaxRange:", round(weapon.get_max_range(), 1), ", RangePower:", round(weapon.range_power, 1),
                  ", CurrentAmmo:", ammo_name)
        else:
            print("")

    @staticmethod
    def print_full_weapon(weapon):
        weapon.print_obj()

    def print_weapons_stored(self):
        print("   - Weapons stored:")
        if not self.weapons_stored:
            print("      \\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            print("      \\", end=' ')
            CharEquipments.print_weapon(weapon)
        return True

    def print_full_weapons_stored(self):
        print("   - Weapons stored:")
        if not self.weapons_stored:
            print("      \\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            print("      \\", end=' ')
            CharEquipments.print_full_weapon(weapon)
        return True
    
    def print_weapons_in_use(self):
        print("")
        print("   - Weapons used:")
        if not self.weapons_in_use:
            print("      \\No weapon used")
            return False
        for weapon in self.weapons_in_use:
            print("      \\", end=' ')
            CharEquipments.print_weapon(weapon)
        return True

    def print_full_weapons_in_use(self):
        print("")
        print("   - Weapons used:")
        if self.weapons_in_use:
            print("      \\No weapon used")
            return False
        for weapon in self.weapons_in_use:
            print("      \\", end=' ')
            CharEquipments.print_full_weapon(weapon)
        return True
    
    def print_ammo(self):
        print("   - Ammo available:")
        if not self.ammo:
            print("      \\No ammo")
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
            print("      \\", ammo_type_list[key]["number"], "arrow(s) of ...")
            print("       ", end=' ')
            ammo_type_list[key]["ammo_type"].print_obj()
        return True

    def print_equipments(self):
        print("-- EQUIPMENTS --")
        self.print_armors()
        self.print_weapons_in_use()
        self.print_weapons_stored()
        self.print_ammo()

    def print_full_equipments(self):
        print("-- EQUIPMENTS --")
        self.print_full_armors()
        self.print_full_weapons_in_use()
        self.print_full_weapons_stored()
        self.print_ammo()

    def print_obj(self):
        self.print_equipments()

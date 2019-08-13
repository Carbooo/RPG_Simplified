import copy as copy
import math as math
import random as random
import time as time
from sources.character.Equipments import Equipments, Weapons, Shields, AttackWeapons, \
    MeleeWeapons, RangedWeapons, Bows, Crossbows, Ammo, NoneWeapon, NoneAmmo
from sources.character.Bodies import Bodies
from sources.character.BodyMembers import BodyMembers


#############################################################
############# CHARACTERS INSTANCES CLASS ####################
#############################################################
class Characters:
    'Common base class for all characters'
    
    # Characters constants
    list = []
    instances_count = 0
    max_position_area = 6 # Max range for characters positions
    variance = 0.1 # Gauss variance
    max_bonus = 1.35 # Max load bonus
    load_mean = 50.0 # Load reference for characters characteristics
    bulk_mean = 6.0 # Bulk reference for characters characteristics
    use_load_mean = 15.0 # Weapons use load reference for characters
    use_bulk_mean = 3.5 # Weapons use bulk reference for characters
    min_speed = 1.0 / 6.0 # Minimum speed for char (necessary for hurt char)
    accuracy_mean = 100.0 # Accuracy reference for characters
    min_speed_run_level = 0.75 # Minimum speedrunlevel (use for starting move)
    
    # A turn is around 6 seconds
    # [Action choices, action command, time spend, stamina spend, action description]
    NoAction = ["No current action", "NOA", 0.0, 0.0, "No action"]
    Pass = ["Wait a little", "PAS", 0.1, 0.0, "Passing time"]
    Rest = ["Rest a little", "RES", 1.0, 0.0, "Resting"]
    
    Defending = ["Is defending against an attack", "DEF", 0.0, 0.0, "Defending"]
    MeleeAttack = ["Melee attack an enemy character", "MAT", 0.35, 1.0, "Melee attacking"]
    RangedAttack = ["Ranged attack an enemy character", "RAT", 0.35, 0.5, "Ranged attacking"]
    Reload = ["Reload your ranged weapon", "REL", 1.0, 0.1, "Reloading"]
    
    # Between each case, there are approximatively 2 meters
    # Normal run is around 2.7 meters --> around 1 case per second
    # Time of reflexion and other handicaps increase time per cases
    Move = ["Move to an adjacent case", "MOV", 0.15, 0.1, "Moving"]

    EquipSpec = ["Equip specific weapons", "EQS", 0.5, 0.0, "Equiping"]
    EquipAll = ["Equip all your weapons", "EQA"] + EquipSpec[2:4] + ["Equiping"]
    UnequipSpec = ["Unequip specific weapons", "UQS"] + EquipSpec[2:4] + ["Unequiping"]
    UnequipAll = ["Unequip all your weapons", "UQA"] + UnequipSpec[2:4] + ["Unequiping"]
    
    Information = ["Information on a character state", "INF", 0.0, 0.0, "Information"]
    Save = ["Save the current game state", "SAV", 0.0, 0.0, "Saving"]
    Load = ["Load a previous game state", "LOA", 0.0, 0.0, "Loading"]
    
    Actions = []
    Actions.append(Pass)
    Actions.append(Rest)
    Actions.append(MeleeAttack)
    Actions.append(RangedAttack)
    Actions.append(Reload)
    Actions.append(Move)
    Actions.append(EquipSpec)
    Actions.append(EquipAll)
    Actions.append(UnequipSpec)
    Actions.append(UnequipAll)
    Actions.append(Information)
    Actions.append(Save)
    Actions.append(Load)
    
    def __init__(self, name, constitution, force, agility, dexterity, reflex, \
    willpower, spirit, prefered_hand, head_armor, chest_armor, arms_armor, legs_armor, \
    weapon1, weapon2, weapon3, weapon4, ammo_type1, ammo_number1, ammo_type2, ammo_number2, \
    abscissa, ordinate):
        #Check name availability
        for char in Characters.list:
            if char.name == name:
                print("(Characters) Character creation failed because the name:", name, "is already used !")
                return False
            
        #Set ID
        self.ID = Characters.instances_count
        Characters.instances_count += 1
        self.original_i_d = len(Characters.list)
        Characters.list.append(self)
        
        #Set characteristics
        self.name = name
        self.constitution = float(constitution)
        self.constitution_ratio = max(1, self.constitution) / 10
        self.force = float(force)
        self.force_ratio = max(1, self.force) / 10
        self.agility = float(agility)
        self.original_agility = self.agility
        self.dexterity = float(dexterity)
        self.reflex = float(reflex)
        self.willpower = float(willpower)
        self.willpower_ratio = float(willpower) / 10
        self.spirit = float(spirit)
        self.spirit_ratio = float(spirit) / 10
        self.set_initial_position(abscissa, ordinate)
        life = max(1, float(self.constitution * 10))
        mana = max(1, float(self.spirit * 10))
        stamina = max(1, \
            (self.constitution + float(self.willpower)/3 \
            + float(self.agility)/2 + float(self.force)/2) \
            * 10 / (1 + 1.0/3 + 2.0/2))
        self.moral = max(1, float(self.willpower))
        self.body = Bodies(life, stamina, mana, prefered_hand, self.force_ratio)
        
        #Set characters parameters
        self.timeline = 0.0
        self.last_action = Characters.NoAction
        
        #Set weapons
        self.weapons_stored = []
        self.weapons_use = []
        self.ammo = []
        self.set_equipments(\
            head_armor, chest_armor, arms_armor, legs_armor, \
            weapon1, weapon2, weapon3, weapon4, \
            ammo_type1, ammo_number1, ammo_type2, ammo_number2)
        
        #Calculate character characteristics
        self.calculate_characteristic()
        
    
    def get_id(self):
        return self.ID

        
    def copy(self):
        #Copy character
        char = copy.copy(self)
        if char.ID != 0:
            char.ID = Characters.instances_count
            Characters.instances_count += 1
        
        #Save armors
        armors_list = []
        armors_list.append(char.body.head.armor.name)
        armors_list.append(char.body.chest.armor.name)
        armors_list.append(char.body.left_arm.armor.name)
        armors_list.append(char.body.left_leg.armor.name)
        
        #Save weapons
        weapons_list = []
        for weapon in self.weapons_stored:
            weapons_list.append(weapon.name)
        for weapon in self.weapons_use:
            weapons_list.append(weapon.name)
        if len(weapons_list) > 4:
            print("(Characters) Error: cannot copy all character weapons:", weapons_list)
        for _ in range(4 - len(weapons_list)):
            weapons_list.append(NoneWeapon)
        
        #Save ammo
        ammo_list = []
        for ammo in self.ammo:
            exist = False
            for ammo_type in ammo_list:
                if ammo_type[0] == ammo.name:
                    ammo_type[1] += 1
                    exist = True
                    break
            if not exist:
                ammo_list.append([ammo.name, 1])
        if len(ammo_list) > 2:
            print("(Characters) Error: cannot copy all character ammo:", ammo_list)
        for _ in range(2 - len(ammo_list)):
            ammo_list.append([NoneAmmo.name, 0])
                
        #Set copy of the equipments
        char.remove_all_equipments()
        char.set_equipments(\
            armors_list[0], armors_list[1], armors_list[2], armors_list[3], \
            weapons_list[0], weapons_list[1], weapons_list[2], weapons_list[3], \
            ammo_list[0][0], ammo_list[0][1], ammo_list[1][0], ammo_list[1][1])
        
        return char
     
        
################### RESET & STATE FUNCTIONS ######################
    def is_modifying_equipment(self):
        if self.current_action == Characters.UnequipAll or \
        self.current_action == Characters.UnequipSpec or \
        self.current_action == Characters.EquipAll or \
        self.current_action == Characters.EquipSpec:        
            return True
        return False
    
    def is_moving(self):
        if self.current_action == Characters.Move:
            return True
        return False
    
    
    def is_melee_fighting(self):
        if self.current_action == Characters.MeleeAttack:
            return True
        return False
    
    
    def is_waiting(self):
        if self.current_action == Characters.Pass or \
        self.current_action == Characters.NoAction:
            return True
        return False
    
    def calculate_state(self):
        old_state = self.body.state
        self.body.calculate_states()
        new_state = self.body.state
        
        if new_state != old_state:
            txt = "ID: " + str(self.get_id()) + ", Name: " + self.name + \
                " state is now:"
            print(txt, new_state)
            time.sleep(3)
        
        self.calculate_characteristic()


    def is_shape_k_o(self):
        if self.body.shape == "KO":
            return True
        return False


    def is_active(self):
        if self.body.state != "KO" and self.body.state != "Dead" \
        and self.body.shape != "KO":
            return True
        return False


    def is_life_active(self):
        if self.body.state != "KO" and self.body.state != "Dead":
            return True
        return False


    def is_alive(self):
        if self.body.state != "Dead":
            return True
        return False
    
    
    def spend_time(self, time_spent):
        self.spend_absolute_time(time_spent / self.speed_ratio)
    
    
    def spend_absolute_time(self, time_spent):
        self.timeline += time_spent
        
    
    def check_stamina(self, coefficient):
        return self.body.get_current_stamina() >= BodyMembers.turn_stamina * coefficient
    
    
    def spend_stamina(self, coefficient):
        self.body.spend_stamina(coefficient)
    
    
    def spend_move_stamina(self, coefficient):
        self.body.spend_move_stamina(coefficient)
            
    
    def spend_melee_attack_stamina(self, coefficient):
        self.body.spend_melee_attack_stamina(coefficient / math.pow(self.force_ratio, 2))
    
    
    def spend_ranged_attack_stamina(self, coefficient):
        self.body.spend_ranged_attack_stamina(coefficient / math.pow(self.force_ratio, 2))
            
    
    def spend_reload_stamina(self, coefficient):
        self.body.spend_reload_stamina(coefficient / math.pow(self.force_ratio, 2))
            
    
    def spend_defense_stamina(self, coefficient):
        self.body.spend_defense_stamina(coefficient / math.pow(self.force_ratio, 2))
            
    
    def spend_dodge_stamina(self, coefficient):
        self.body.spend_dodge_stamina(coefficient)
                        

    def is_none_character(self):
        if self.name == "--none--":
            return True
        return False


################## POSITIONS FUNCTIONS ######################
    def check_position(self):
        if self.abscissa not in range(Characters.max_position_area):
            print("(Characters) Abscissa must be included in [0:", \
                Characters.max_position_area, "]")
            return False
        
        if self.ordinate not in range(Characters.max_position_area):
            print("(Characters) Ordinate must be included in [0:", \
                Characters.max_position_area, "]")
            return False
        
        return True
        
        
    def set_position(self, abscissa, ordinate):
        self.abscissa = abscissa
        self.ordinate = ordinate
        
        
    def set_initial_position(self, abscissa, ordinate):
        self.abscissa = abscissa
        self.ordinate = ordinate
        
        if self.check_position():
            return True
        
        self.abscissa = -1
        self.ordinate = -1
        return False
    
    
####################### WEAPONS FUNCTIONS ######################       
    def movement_handicap_ratio(self):
        return math.sqrt( \
            (math.pow(self.load_ratio, 2) * math.pow(self.use_load_ratio, 1.0/2)) * \
            (math.pow(self.bulk_ratio, 1.0/2) * math.pow(self.use_bulk_ratio, 2)))
    
    
    def use_a_shield(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, Shields):
                return True
        return False
    
    
    def is_using_a_ranged_weapon(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons):
                return True
        return False    
            
        
    def is_using_a_melee_weapon(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, MeleeWeapons):
                return True
        if not self.weapons_use:
            #If no weapons, can melee attack with hands
            return True
        return False
    
    
    def remove_all_equipments(self):
        self.body.set_armors("--none_armor--", "--none_armor--", "--none_armor--", "--none_armor--")
        self.weapons_stored = []
        self.weapons_use = []
        self.ammo = []
        
    
    def set_equipments(self, \
    head_armor, chest_armor, arms_armor, legs_armor, \
    weapon1, weapon2, weapon3, weapon4, \
    ammo_type1, ammo_number1, ammo_type2, ammo_number2):
        #Set armors
        self.body.set_armors(head_armor, chest_armor, arms_armor, legs_armor)
        
        #Set weapons
        weapon_list = [weapon1, weapon2, weapon3, weapon4]
        for weapon in weapon_list:
            if weapon == NoneWeapon.name:
                continue
            for equip in Equipments.list:
                if isinstance(equip, Weapons) and equip.name == weapon:
                    self.weapons_stored.append(equip.copy())
                    break
                
        #Set ammo
        self.set_ammo(ammo_type1, ammo_number1)
        self.set_ammo(ammo_type2, ammo_number2)
    
    
    def set_ammo(self, ammo_type, ammo_number):
        if ammo_type == NoneAmmo.name:
            return False
        
        ammo_found = False
        for equip in Equipments.list:
            if isinstance(equip, Ammo) and equip.name == ammo_type:
                ammo_found = equip
                break
        if ammo_found:
            for _ in range(ammo_number):
                self.ammo.append(ammo_found.copy())
            return True
             
        print("(Characters) Ammo cannot be set because ammo type (", ammo_type, ") has not been found !")
        return False
    
        
    def remove_weapon_in_use(self, weapon, dropping=False):
        if self.body.remove_weapon(weapon):
            self.weapons_use.remove(weapon)
            if not dropping:
                self.weapons_stored.append(weapon)
            if isinstance(weapon, Bows) and weapon.current_reload > 0:
                self.ammo.append(weapon.current_reload)
                weapon.unload()
            return True
        return False
    

    def add_weapon_in_use(self, weapon):
        if self.body.set_weapon(weapon):
            self.weapons_stored.remove(weapon)
            self.weapons_use.append(weapon)
            return True
        return False


    def nb_of_hands_used(self):
        nb_of_hands = 0
        for weapon in self.weapons_use:
            nb_of_hands += weapon.hand
        return nb_of_hands
        
        
    def nb_of_hands_stored(self):
        nb_of_hands = 0
        for weapon in self.weapons_stored:
            nb_of_hands += weapon.hand
        return nb_of_hands
    
    
    def all_weapons_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_use:
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
        for weapon in self.weapons_use:
            if isinstance(weapon, MeleeWeapons):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)
    
    
    def all_shields_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in range(len(self.weapons_use)):
            if isinstance(weapon, Shields):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in range(len(weapons_list)):
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)
                    

    def weapon_absorbed_damage(self, weapon, damage):
        if weapon.decrease(damage) == 0:
            print("Your weapon \\ID:", weapon.get_id(), "\\Name:", weapon.name, \
                "has been broken!")
            self.weapons_use.remove(weapon)
        

######################### CALCULATE FUNCTIONS ########################
    def calculate_load_ratios(self):
        load = 0.0
        use_load = 0.0
        for weapon in self.weapons_stored:
            load += weapon.load
        for weapon in self.weapons_use:
            load += weapon.load
            use_load += weapon.load
            if isinstance(weapon, RangedWeapons) and weapon.current_ammo:
                use_load += weapon.current_ammo.load 
        for ammo in self.ammo:
            load += ammo.load
        load += self.body.armors_load()
        
        self.load_ratio =  min(Characters.max_bonus, Characters.load_mean / max(1, load) * self.force_ratio)
        self.body.load_ratio = math.pow(self.load_ratio, 0.5)
        self.use_load_ratio = min(Characters.max_bonus, Characters.use_load_mean / max(1, use_load) * self.force_ratio)

    
    def calculate_bulk_ratios(self):
        bulk = 0.0
        use_bulk = 0.0
        for weapon in self.weapons_stored:
            bulk += weapon.bulk
        for weapon in self.weapons_use:
            bulk += weapon.bulk
            use_bulk += weapon.bulk
            if isinstance(weapon, Bows) and weapon.current_ammo:
                use_bulk += weapon.current_ammo.bulk * 10 #Arrow being used is bulkier
        for ammo in self.ammo:
            bulk += ammo.load
        bulk += self.body.armors_bulk()
        
        self.bulk_ratio =  min(Characters.max_bonus, \
            Characters.load_mean / max(1, bulk) * self.force_ratio)
        self.use_bulk_ratio = min(Characters.max_bonus, \
            Characters.use_bulk_mean / max(1, use_bulk) * self.force_ratio)


    def calculate_agility(self):
        self.agility = max(1, self.original_agility * self.load_ratio * self.bulk_ratio)
     
     
    def accuracy_ratio(self, attack_type="None"):
        if attack_type == "Melee":
            return max(1, self.melee_handiness) / Characters.accuracy_mean
        elif attack_type == "Ranged":
            return max(1, self.ranged_accuracy) / Characters.accuracy_mean
        elif self.is_using_a_ranged_weapon():
            return max(1, self.ranged_accuracy) / Characters.accuracy_mean
        else:
            return max(1, self.melee_handiness) / Characters.accuracy_mean
    
     
    def calculate_accuracies(self):
        #Calculate weapons accuracies
        melee_weapons_handiness = 0.0
        ranged_weapons_accuracy = 0.0
        melee_weapons_nb = 0.0
        ranged_weapons_nb = 0.0
        for weapon in self.weapons_use:
            if isinstance(weapon, MeleeWeapons):
                melee_weapons_handiness += weapon.melee_handiness * self.body.weapon_ratio(weapon)
                melee_weapons_nb += 1
            elif isinstance(weapon, RangedWeapons):
                ranged_weapons_accuracy += weapon.accuracy * self.body.weapon_ratio(weapon)
                ranged_weapons_nb += 1
        
        #Free hands melee accuracy
        if self.body.left_arm.is_not_weapon_equiped():
            melee_weapons_handiness += 15.0 * self.body.left_arm_global_ratio()
            melee_weapons_nb += 1
        if self.body.right_arm.is_not_weapon_equiped():
            melee_weapons_handiness += 15.0 * self.body.right_arm_global_ratio()
            melee_weapons_nb += 1
            
        #Avoid 0 division
        melee_weapons_nb = max(1.0, melee_weapons_nb)
        ranged_weapons_nb = max(1.0, ranged_weapons_nb)
        
        #Calculate accuracy coefs
        melee_coef = (self.dexterity + self.agility/2 + self.force/3) / (1 + 1.0/2 + 1.0/3)
        if self.is_using_a_crossbow():
            ranged_coef = (self.dexterity + self.agility/3 + self.reflex/3) / (1 + 2.0/3)
        else:
            ranged_coef = (self.dexterity + self.force/2 + self.agility/3 + self.reflex/3) / (1 + 1.0/2 + 2.0/3)
        
        #Set accuracies
        self.melee_handiness = max(1, self.body.melee_attack_global_ratio() * \
            melee_coef * melee_weapons_handiness / melee_weapons_nb)
        self.ranged_accuracy = max(1, self.body.ranged_attack_global_ratio() * \
            ranged_coef * ranged_weapons_accuracy / ranged_weapons_nb)    
     
         
    def calculate_melee_range(self):
        #Calculate weapons melee_range
        melee_range = 0.0
        melee_weapons_nb = 0.0
        for weapon in self.weapons_use:
            if isinstance(weapon, Weapons):
                melee_range += weapon.melee_range
                melee_weapons_nb += 1
        
        #Free hands melee range
        if self.body.left_arm.is_not_weapon_equiped() and self.body.right_arm.is_not_weapon_equiped():
            melee_range = 5.0
            melee_weapons_nb = 1

        #Set range
        self.melee_range = max(1, melee_range / melee_weapons_nb)    
     
         
    def calculate_attack_power(self):
        #Calculate weapons damages
        self.melee_power = 0.0
        self.penetration_rate = 0.0
        self.resistance_dim_rate = 0.0
        self.ranged_power = 0.0
        nb_of_weapons = 0.0
        for weapon in self.weapons_use:
            nb_of_weapons += 1
            self.melee_power += weapon.melee_power * self.body.weapon_ratio(weapon)
            #Do not divide if 2 hands are used. Divide by 2 if only 1 hand is used
            self.penetration_rate += weapon.penetration_rate
            self.resistance_dim_rate += weapon.resistance_dim_rate
            if isinstance(weapon, RangedWeapons) and self.ranged_weapon_has_ammo(weapon):
                if isinstance(weapon, Crossbows):
                    self.ranged_power += weapon.range_power
                else:
                    self.ranged_power += weapon.range_power * self.body.weapon_ratio(weapon)
        
        #Free hands melee attack power
        if self.body.left_arm.is_not_weapon_equiped():
            self.melee_power += 0.75 * self.body.left_arm_global_ratio()
            #Only one hand, divide by 2
            self.penetration_rate += 0.015 / 2.0
            self.resistance_dim_rate += 0.01 / 2.0
        if self.body.right_arm.is_not_weapon_equiped():
            self.melee_power += 0.75 * self.body.right_arm_global_ratio()
            #Only one hand, divide by 2
            self.penetration_rate += 0.015 / 2.0
            self.resistance_dim_rate += 0.01 / 2.0
            
        #Calculate power coefs
        melee_coef = (self.force + self.agility/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
        ranged_coef = (self.force + self.dexterity/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
            
        #Set attack powers
        self.penetration_rate /= max(1.0, nb_of_weapons)
        self.resistance_dim_rate /= max(1.0, nb_of_weapons)
        self.melee_power = max(1.0, melee_coef * self.melee_power * self.body.melee_attack_global_ratio())
        if self.is_using_a_crossbow():
            self.ranged_power *= 10 #Default power
        else:
            self.ranged_power *= max(1.0, ranged_coef * self.body.ranged_attack_global_ratio())
        self.magic_power_ratio = self.body.global_ratio() * (self.spirit + self.willpower/2) / (1 + 1.0/2)
        self.magic_power = self.magic_power_ratio * 10
    
    def calculate_defense(self):
        #Calculate equipments defense
        melee_defense = 0.0
        ranged_defense = 0.0
        for weapon in self.weapons_use:
            if isinstance(weapon, Shields):
                melee_defense += weapon.defense * self.body.weapon_ratio(weapon)
                ranged_defense += weapon.defense * self.body.weapon_ratio(weapon)
            elif isinstance(weapon, AttackWeapons):
                melee_defense += weapon.defense * self.body.weapon_ratio(weapon)
        
        #Free hands melee defense
        if self.body.left_arm.is_not_weapon_equiped():
            melee_defense += 0.75 * self.body.left_arm_global_ratio()
        if self.body.right_arm.is_not_weapon_equiped():
            melee_defense += 0.75 * self.body.right_arm_global_ratio()
        
        #Calculate defense coefs
        melee_coef = self.body.defense_global_ratio() * \
            (self.reflex + self.agility/2 + self.force/2) / (1 + 2.0/2)
        #Skills do not really matter for ranged defense
        #The bigger you are, the harder it is to defend
        ranged_coef = math.sqrt((self.reflex + self.agility/2) / (1 + 1.0/2)) / self.constitution_ratio
        
        #Set defenses
        self.armor_resistance = self.body.armors_resistance()
        self.armor_defense = self.body.armors_defense()
        self.melee_defense = melee_defense * melee_coef
        self.ranged_defense = ranged_defense * ranged_coef
        self.magic_defense = max(1, (self.spirit + self.willpower/2 + self.constitution/3) \
             * 10 / (1 + 1.0/2 + 1.0/3))

        
    def calculate_dodging(self):
        #More equipment used, lower dodge ratio
        #The bigger you are, the harder is to dodge
        self.dodging = max(1, self.body.defense_global_ratio() * 10 * \
            (self.reflex + self.agility) / (1.0 + 1.0) / self.constitution_ratio)


    @staticmethod
    def get_speed_ratio_by_coef(coefficient):
        return max(Characters.min_speed, coefficient)
        
        
    def calculate_speed_ratio(self): 
        self.speed_ratio = Characters.get_speed_ratio_by_coef(self.body.global_ratio())


    def calculate_characteristic(self):
        self.calculate_load_ratios()
        self.calculate_bulk_ratios()
        self.calculate_agility()
        
        self.calculate_accuracies()
        self.calculate_melee_range()
        self.calculate_attack_power()

        self.calculate_defense()
        self.calculate_dodging()
        
        self.calculate_speed_ratio()
        

###################### MELEE FUNCTIONS ########################
    @staticmethod
    def get_melee_attack(melee_handiness, melee_power):
        return math.pow(melee_power * math.pow(melee_handiness, 1.0/3), 0.75)
    
    @staticmethod
    def get_melee_accuracy(melee_handiness, melee_power):
        return math.pow(melee_power * math.pow(melee_handiness, 1.0/3), 0.75)    
        
    def can_melee_attack(self, enemy):
        if enemy.is_alive() and self.is_active() and \
        enemy.abscissa in range(self.abscissa - 1, self.abscissa + 2) and \
        enemy.ordinate in range(self.ordinate - 1, self.ordinate + 2):
            if not enemy.is_moving() or ( \
            enemy.action_in_progress.old_abs in range(self.abscissa - 1, self.abscissa + 2) and \
            enemy.action_in_progress.old_ord in range(self.ordinate - 1, self.ordinate + 2)):
                return True
        return False
    
    
###################### DAMAGE FUNCTIONS ########################
    def melee_attack_received(self, enemy, attack_value, attack_coef, member):
        resistance_dim_rate = enemy.resistance_dim_rate
        penetration_rate = enemy.penetration_rate
        self.attack_received(enemy, attack_value, attack_coef, member, resistance_dim_rate, penetration_rate)
    
    def ranged_attack_received(self, enemy, attack_value, attack_coef, member, ammo_used):
        resistance_dim_rate = enemy.resistance_dim_rate * ammo_used.resistance_dim_rate
        penetration_rate = enemy.penetration_rate * ammo_used.penetration_rate
        self.attack_received(enemy, attack_value, attack_coef, member, resistance_dim_rate, penetration_rate)
    
    def magic_attack_received(self, enemy, attack_value, attack_coef, resistance_dim_rate, penetration_rate):
        print("to be defined")
        
    def attack_received(self, enemy, attack_value, attack_coef, member, resistance_dim_rate, penetration_rate):
        a = enemy.attack_characteristics(self, attack_coef, member)
        attack_value *= a[0] / attack_coef
        
        enemy.print_basic()
        print("-- has HIT --", end=' ')
        self.print_basic()
        print("-- with a power of", int(round(attack_value)), "--")
        time.sleep(2)        
        
        self.damage_received(attack_value, a[1], member, resistance_dim_rate, penetration_rate)
        
    
    def attack_characteristics(self, defender, attack_coef, member):
        #Attack&Armor ratio
        cover_ratio = defender.body.member_cover_ratio(member)
        ratio = random.gauss(1, Characters.variance) * attack_coef \
            * self.accuracy_ratio() * (1 - cover_ratio)
        
        if cover_ratio <= 0:
            print("The player has no armor!")
            time.sleep(2)
            armor_coef = 0
        elif ratio < 0.9:
            print("The hit will meet a full armor part")
            time.sleep(2)
            armor_coef = 1
        else:
            print("The hit will avoid the armor!")
            time.sleep(2)
            attack_coef *= (1 - cover_ratio / 2)
            armor_coef = 0
            
        return [attack_coef, armor_coef]
    
    
    def damage_received(self, damage, armor_coef, member, resistance_dim_rate, penetration_rate):
        damage_result = self.body.armor_damage_absorbed(damage, member, armor_coef, resistance_dim_rate, penetration_rate)
        if damage_result > 0:
            life_ratio = self.body.loose_life(damage_result, member)
            if life_ratio > 0:
                #Damages received diminish the defender
                life_ratio = math.pow(2 - life_ratio, 2) - 1
                print("The shock of the attack delays the player of", round(life_ratio,2), "turn(s)")
                time.sleep(3)
                self.spend_time(life_ratio)
                self.spend_stamina(life_ratio)
        
    
###################### RANGED FUNCTIONS ########################
    def calculate_point_distance(self, abscissa, ordinate):
        return math.sqrt( \
            math.pow(self.abscissa - abscissa, 2) + \
            math.pow(self.ordinate - ordinate, 2))
        
    
    def power_distance_ratio(self, enemy):
        return max(0.25, 1 - \
            self.calculate_point_distance(enemy.abscissa, enemy.ordinate) / self.has_range())
    
    
    def power_hit_chance_ratio(self, hit_chance):
        return min(1.0, hit_chance / min(1.0, max(0.0001, random.random() * 1.5)))
    
        
    def has_range(self):
        max_range = 10000
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons):
                max_range = min(max_range, weapon.get_max_range())
        
        if max_range == 10000:
            return 0
        else:
            return max_range
            
    
    def is_distance_reachable(self, enemy):        
        if self.calculate_point_distance(enemy.abscissa, enemy.ordinate) \
        <= self.has_range():
            return True
        return False
    
    
    def char_to_point_angle(self, abscissa, ordinate):
        return math.atan2(ordinate - self.ordinate, abscissa - self.abscissa)
    
    
    def angle_gap_to_enemy(self, enemy):
        angle = math.fabs(self.last_direction - \
            self.char_to_point_angle(enemy.abscissa, enemy.ordinate))
        #print "last_direction:", math.degrees(self.last_direction)
        #print "char_to_point_angle:", math.degrees(self.char_to_point_angle(enemy.abscissa, enemy.ordinate))
        #print "angle:", math.degrees(angle)
        #print "pi_angle:", math.degrees(2 * math.pi - angle)
        #The shorter angle between the angle and the tour minus the angle
        #print "AngleGapToEnemy:", math.degrees(min(angle, 2 * math.pi - angle))
        return min(angle, 2 * math.pi - angle)
    
    
    def angle_gap_ratio(self, enemy):
        return 1
        #1 is no angle, 0 is an attack in the back
        #print "AngleRatio:", math.degrees(self.angle_gap_to_enemy(enemy) / math.pi)
        angle_ratio = 1 - self.angle_gap_to_enemy(enemy) / math.pi
        #ratio 1 - (angle_ratio * 1.3)^3
        return max(0.0001, 1 - math.pow(angle_ratio * 1.3, 3))


    def calculate_point_to_enemy_path_cos_angle(self, enemy, abscissa, ordinate):
        u_abs = enemy.abscissa - self.abscissa
        u_ord = enemy.ordinate - self.ordinate
        v_abs = abscissa - self.abscissa
        v_ord = ordinate - self.ordinate
 
        return (u_abs*v_abs + u_ord*v_ord) / ( \
            math.sqrt(math.pow(u_abs,2) + math.pow(u_ord,2)) * \
            math.sqrt(math.pow(v_abs,2) + math.pow(v_ord,2)))


    def calculate_point_to_enemy_path_angle(self, enemy, abscissa, ordinate):
        angle = math.acos( \
            self.calculate_point_to_enemy_path_cos_angle(enemy, abscissa, ordinate))

        if ordinate < self.ordinate:
            angle = 2 * math.pi - angle
        
        return angle

    
    def calculate_point_to_enemy_path_distance(self, enemy, abscissa, ordinate):
        #Only work if abscissa & ordinate are in the segment path
        #and if abscissa and ordinate are different from char position
        ac_length = self.calculate_point_distance(abscissa, ordinate)
        ah_length = ac_length * self.calculate_point_to_enemy_path_cos_angle(enemy, abscissa, ordinate)
        return math.sqrt(max(0, math.pow(ac_length, 2) - math.pow(ah_length, 2)))
    
    
    def set_enemy_pos_variation(self, enemy, variation):
        #Calculate angle between enemy and abscissa axis
        c = copy.copy(self) #Is used for abscissa axis
        c.abscissa += 1
        angle = self.calculate_point_to_enemy_path_angle( \
            c, enemy.abscissa, enemy.ordinate)
        
        #Set the variated position
        angle += math.radians(variation)
        enemy.abscissa += int(round(self.has_range() * math.cos(angle)))
        enemy.ordinate += int(round(self.has_range() * math.sin(angle)))
    
    
    def has_ammo(self):
        for weapon in self.weapons_use:
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
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons) and not weapon.is_reloaded():
                return False
        return True
    
    
    def reload(self, weapon, ammo):
        weapon.print_obj()
        weapon.reload(ammo)
        self.ammo.remove(ammo)
    
    
    def get_current_ammo(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons):
                return weapon.current_ammo
    
    
    def use_ammo(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons):
                ammo_used = weapon.unload()
                break
        self.calculate_characteristic()
        return ammo_used
        
        
    def loose_reloaded_ammo(self):
        has_lost = False
        for weapon in self.weapons_use:
            if isinstance(weapon, Bows) and weapon.is_reloaded():
                has_lost = True
                weapon.unload()
        return has_lost
        
        
    def is_using_a_crossbow(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, Crossbows):
                return True
        return False
    
            
    def is_using_a_bow(self):
        for weapon in self.weapons_use:
            if isinstance(weapon, Bows):
                return True
        return False
        

##################### PRINTING FUNCTIONS ########################
    def print_basic(self):
        print("ID:", self.get_id(), ", Name:", self.name, end=' ')
        
        
    def print_position(self):
        print(", Abscissa:", self.abscissa, \
            ", Ordinate:", self.ordinate, end=' ')
        
        
    def print_equipments(self):
        self.body.print_full_armors()
        self.print_weapons_use()
        self.print_weapons_stored()
        self.print_ammo()
        
        
    def print_characteristics(self):
        self.print_basic()
        print(", Constitution:", int(round(self.constitution)), \
            ", Force:", int(round(self.force)), \
            ", Agility:", int(round(self.agility)), \
            ", Dexterity:", int(round(self.dexterity)), \
            ", Reflex:", int(round(self.reflex)), \
            ", Willpower:", int(round(self.willpower)), \
            ", Spirit:", int(round(self.spirit)), \
            ", Moral:", int(round(self.moral)), end=' ')
        self.print_position()
        self.print_equipments()
    
    
    def print_defense(self):
        print(",ArmorResistance:", int(round(self.armor_resistance)), \
            ",ArmorDefense:", int(round(self.armor_defense)), \
            ",Dodging:", int(round(self.dodging)), \
            ",MeleeDefense:", int(round(self.melee_defense)), \
            ",RangedDefense:", int(round(self.ranged_defense)), \
            ",MagicDefense:", int(round(self.magic_defense)), end=' ')


    def print_attack(self):
        print(",MeleeHandiness:", int(round(self.melee_handiness)), \
            ",MeleePower:", int(round(self.melee_power)), \
            ",MeleeRange:", int(round(self.melee_range)), \
            ",PenetrationRate:", int(round(self.penetration_rate, 2)), \
            ",resistance_dim_rate:", int(round(self.resistance_dim_rate, 2)), end=' ')
        if self.ranged_power > 1:
            print(",RangedAccuracy:", int(round(self.ranged_accuracy)), \
                ",RangedPower:", int(round(self.ranged_power)), end=' ')
            self.print_ranged_info()
        if self.magic_power > 1:
            print(",MagicPower:", int(round(self.magic_power)), end=' ')
            

    def print_ranged_info(self):
        use_ranged_weapon = False
        for weapon in self.weapons_use:
            if isinstance(weapon, RangedWeapons):
                use_ranged_weapon = True
                break
        if use_ranged_weapon:
            max_range = 10000
            reload_left = -10000
            for weapon in self.weapons_use:
                if isinstance(weapon, RangedWeapons):
                    max_range = min(max_range, weapon.get_max_range())
                    reload_left = max(reload_left, weapon.reload_time - weapon.current_reload)
            print(",MaxRange:", max_range, ",AmmoLeft:", len(self.ammo), \
                ",ReloadLeft:", reload_left, end=' ')
                             
                 
    def print_time_state(self):
        print(",SpeedRatio:", round(self.speed_ratio, 2), \
            ",Unconsciousness:", round(self.unconsciousness, 2), \
            ",Timeline:", round(self.timeline,2), \
            ",CurrentAction:", self.current_action[4])
                     

    def print_weapons_stored(self):
        print("Weapons stored:")
        if len(self.weapons_stored) <= 0:
            print("\\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            print("\\", end=' ')
            weapon.print_obj()
        return True


    def print_weapons_use(self):
        print("Weapons used:")
        if len(self.weapons_use) <= 0:
            print("\\No weapon used")
            return False
        for weapon in self.weapons_use:
            print("\\", end=' ')
            weapon.print_obj()
        return True
    
    
    def print_ammo(self):
        print("Ammo available:")
        if len(self.ammo) <= 0:
            print("\\No ammo")
            return False
        for weapon in self.ammo:
            print("\\", end=' ')
            weapon.print_obj()
        return True


    def print_state(self):
        self.print_basic()
        self.body.print_basic()
        self.print_defense()
        self.print_attack()
        self.print_time_state()


    def print_detailed_state(self):
        self.print_basic()
        print("")
        self.body.print_detailed_basic()
        self.print_defense()
        self.print_attack()
        self.print_time_state()


    def print_defense_state(self):
        self.print_basic()
        self.body.print_basic()
        self.print_defense()
        self.print_time_state()


    def print_attack_state(self):
        self.print_basic()
        self.body.print_basic()
        self.print_attack()
        self.print_time_state()

  
    def print_obj(self):
        self.print_detailed_state()
        self.print_equipments()
                

#############################################################
################### INITIALIZATION ##########################
#############################################################
NoneCharacter = Characters("--none--", 0, 0, 0, 0, 0, 0, 0, "ambidextrous", "--none_armor--", "--none_armor--", "--none_armor--", \
    "--none_armor--", "--none_weapon--", "--none_weapon--", "--none_weapon--", "--none_weapon--", "--none_ammo--", 0, "--none_ammo--", 0, 0, 0)
NoneCharacter.set_position(-1, -1)

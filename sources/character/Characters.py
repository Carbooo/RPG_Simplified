import copy as copy
import math as math
import random as random
import time as time
import sources.miscellaneous.global_variables as global_variables
from sources.character.Equipments import Weapons, Shields, AttackWeapons, \
    MeleeWeapons, RangedWeapons, Bows, Crossbows
from sources.character.Bodies import Bodies
from sources.character.Feelings import Feelings


#############################################################
############# CHARACTERS INSTANCES CLASS ####################
#############################################################
class Characters:
    'Common base class for all characters'
    
    # Characters constants
    list = []
    max_position_area = 6 # Max range for characters positions
    variance = 0.1 # Gauss variance
    high_variance = 0.25 # Gauss variance
    max_bonus = 1.35 # Max load bonus
    load_mean = 50.0 # Load reference for characters characteristics
    bulk_mean = 6.0 # Bulk reference for characters characteristics
    use_load_mean = 15.0 # Weapons use load reference for characters
    use_bulk_mean = 3.5 # Weapons use bulk reference for characters
    min_speed = 1.0 / 6.0 # Minimum speed for char (necessary for hurt char)
    accuracy_mean = 100.0 # Accuracy reference for characters
    critical_hit_chance = 0.083 # Chances to hit the head or other key areas (1 / 12)
    critical_hit_boost = 6.0
    max_magic_distance = 100.0  # Around 200 meters
    
    # A turn is around 6 seconds
    # [Action choices, action command, time spend, stamina spend, action description]
    Pass = ["Wait a little", "PAS", 0.1, 0.0, "Passing time"]
    Rest = ["Rest a little", "RES", 1.0, 0.0, "Resting"]
    Concentrate = ["Concentrate on your mind and feelings", "CON", 1.0, 0.0, "Concentrating"]
    
    Defending = ["Is defending against an attack", "DEF", 0.0, 0.0, "Defending"]
    MeleeAttack = ["Melee attack an enemy character", "MAT", 0.5, 1.0, "Melee attacking"]
    RangedAttack = ["Ranged attack an enemy character", "RAT", 0.5, 0.75, "Ranged attacking"]
    Reload = ["Reload your ranged weapon", "REL", 0.0, 0.1, "Reloading"]  # Reload time is defined on the weapon
    
    # Between each case, there are approximatively 2 meters
    # Normal run is around 2.7 meters --> around 1 case per second
    # Time of reflexion and other handicaps increase time per cases
    Move = ["Move to an adjacent case", "MOV", 0.15, 0.1, "Moving"]

    Equip = ["Equip / Unequip weapons", "EQP", 0.5, 0.1, "Equiping"]
    
    Information = ["Information on a character state", "INF", 0.0, 0.0, "Information"]
    Save = ["Save the current game state", "SAV", 0.0, 0.0, "Saving"]
    Load = ["Load a previous game state", "LOA", 0.0, 0.0, "Loading"]
    
    # Spells
    Spell = ["Cast a spell", "SPL", 0.0, 0.0, "Casting"]
    spells = []
    
    wrath_spells = {
        "description" : "Wrath spell",
        "code" : "WRA",
        "list" : []
    }
    spells.append(wrath_spells)
    wrath_improve_strength = {
        "description" : "Improve your strength",
        "code" : "STR",
        "type" : "wrath"
    }
    wrath_spells["list"].append(wrath_improve_strength)
    wrath_fireball = {
        "description" : "Throw a fireball",
        "code" : "FBL",
        "type" : "wrath"
    }
    wrath_spells["list"].append(wrath_fireball)
    
    Actions = []
    Actions.append(Pass)
    Actions.append(Rest)
    Actions.append(MeleeAttack)
    Actions.append(RangedAttack)
    Actions.append(Reload)
    Actions.append(Move)
    Actions.append(Equip)
    Actions.append(Information)
    Actions.append(Save)
    Actions.append(Load)
    Actions.append(Spell)
    Actions.append(Concentrate)
    
    def __init__(self, name, constitution, force, agility, dexterity, reflex, willpower, spirit, moral, empathy,
                 armor, weapon1, weapon2, weapon3, weapon4, ammo_type1, ammo_number1, ammo_type2, ammo_number2,
                 wrath_sensibility, wrath_mastering, joy_sensibility, joy_mastering, 
                 love_sensibility, love_mastering, hate_sensibility, hate_mastering, 
                 fear_sensibility, fear_mastering, sadness_sensibility, sadness_mastering,
                 abscissa, ordinate):
        # Check name availability
        for char in Characters.list:
            if char.name == name:
                print("(Characters) Character creation failed because the name:", name, "is already used !")
                exit(0)
        self.name = name
        
        # Set ID
        self.ID = len(Characters.list)
        Characters.list.append(self)
        
        # Set characteristics
        self.original_constitution = float(constitution)
        self.constitution = float(constitution)
        self.constitution_ratio = float(constitution) / 10.0
        self.original_force = float(force)
        self.force = float(force)
        self.force_ratio = float(force) / 10.0
        self.original_agility = float(agility)
        self.agility = float(agility)
        self.agility_ratio = float(agility) / 10.0
        self.original_dexterity = float(dexterity)
        self.dexterity = float(dexterity)
        self.dexterity_ratio = float(dexterity) / 10.0
        self.original_reflex = float(reflex)
        self.reflex = float(reflex)
        self.reflex_ratio = float(reflex) / 10.0
        self.original_willpower = float(willpower)
        self.willpower = float(willpower)
        self.willpower_ratio = float(willpower) / 10.0
        self.original_spirit = float(spirit)
        self.spirit = float(spirit)
        self.spirit_ratio = float(spirit) / 10.0
        self.original_moral = float(moral)
        self.moral = float(moral)
        self.moral_ratio = float(moral) / 10.0
        self.original_empathy = float(empathy)
        self.empathy = float(empathy)
        self.empathy_ratio = float(empathy) / 10.0
        self.body = Bodies(
            float(self.constitution) * 10.0, 
            (float(self.constitution) + float(self.willpower)/3 + float(self.agility)/2 + float(self.force)/2) 
            / (1.0 + 1.0/3 + 2.0/2) * 10.0
        )
        
        # Set characters parameters
        self.timeline = 0.0
        self.set_initial_position(abscissa, ordinate)
        self.last_action = None
        self.previous_attacks = []
        self.active_spells = []
        
        # Set weapons
        self.body.set_equipments(
            armor, weapon1, weapon2, weapon3, weapon4,
            ammo_type1, ammo_number1, ammo_type2, ammo_number2
        )
        
        # Set feelings
        self.nb_of_concentrate = 0
        self.feelings = {
            "wrath" : Feelings("wrath", wrath_sensibility, wrath_mastering),
            "joy": Feelings("joy", joy_sensibility, joy_mastering),
            "love": Feelings("love", love_sensibility, love_mastering),
            "hate": Feelings("hate", hate_sensibility, hate_mastering),
            "fear": Feelings("fear", fear_sensibility, fear_mastering),
            "sadness": Feelings("sadness", sadness_sensibility, sadness_mastering)
        }
        
        #Calculate character characteristics
        self.calculate_characteristic()
        
    def get_id(self):
        return self.ID

################### RESET & STATE FUNCTIONS ######################
    def exceeded_feelings_check(self):
        has_exceeded = False
        for key in self.feelings:
            if self.feelings[key].die_of_exceeded_energy(self):
                has_exceeded = True
        return has_exceeded
    
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
        if self.body.state != "KO" and self.body.state != "Dead" and self.body.shape != "KO":
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

################## POSITIONS FUNCTIONS ######################
    def check_position(self):
        if self.abscissa not in range(Characters.max_position_area):
            print("(Characters) Abscissa must be included in [0:", Characters.max_position_area, "]")
            return False
        if self.ordinate not in range(Characters.max_position_area):
            print("(Characters) Ordinate must be included in [0:", Characters.max_position_area, "]")
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
        else:
            self.abscissa = -1
            self.ordinate = -1
            return False

######################### CALCULATE FUNCTIONS ########################
    def movement_handicap_ratio(self):
        return math.sqrt(
            (math.pow(self.load_ratio, 2) * math.pow(self.use_load_ratio, 1.0/2)) * \
            (math.pow(self.bulk_ratio, 1.0/2) * math.pow(self.use_bulk_ratio, 2)))
    
    def calculate_load_ratios(self):
        load = 0.0
        use_load = 0.0
        for weapon in self.weapons_stored:
            load += weapon.load
        for weapon in self.weapons_in_use:
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
        for weapon in self.weapons_in_use:
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
     
    def calculate_accuracies(self):
        #Calculate weapons accuracies
        melee_weapons_handiness = 0.0
        ranged_weapons_accuracy = 0.0
        melee_weapons_nb = 0.0
        ranged_weapons_nb = 0.0
        for weapon in self.weapons_in_use:
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
        self.melee_handiness_ratio = self.melee_handiness / Characters.accuracy_mean
        self.ranged_accuracy = max(1, self.body.ranged_attack_global_ratio() * \
            ranged_coef * ranged_weapons_accuracy / ranged_weapons_nb)
        self.ranged_accuracy_ratio = self.ranged_accuracy / Characters.accuracy_mean
         
    def calculate_melee_range(self):
        #Calculate weapons melee_range
        melee_range = 0.0
        melee_weapons_nb = 0.0
        for weapon in self.weapons_in_use:
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
        self.pen_rate = 0.0
        self.resis_dim_rate = 0.0
        self.ranged_power = 0.0
        nb_of_weapons = 0.0
        for weapon in self.weapons_in_use:
            nb_of_weapons += 1
            self.melee_power += weapon.melee_power * self.body.weapon_ratio(weapon)
            #Do not divide if 2 hands are used. Divide by 2 if only 1 hand is used
            self.pen_rate += weapon.pen_rate
            self.resis_dim_rate += weapon.resis_dim_rate
            if isinstance(weapon, RangedWeapons) and self.ranged_weapon_has_ammo(weapon):
                if isinstance(weapon, Crossbows):
                    self.ranged_power += weapon.range_power
                else:
                    self.ranged_power += weapon.range_power * self.body.weapon_ratio(weapon)
        
        #Free hands melee attack power
        if self.body.left_arm.is_not_weapon_equiped():
            self.melee_power += 0.75 * self.body.left_arm_global_ratio()
            #Only one hand, divide by 2
            self.pen_rate += 0.015 / 2.0
            self.resis_dim_rate += 0.01 / 2.0
        if self.body.right_arm.is_not_weapon_equiped():
            self.melee_power += 0.75 * self.body.right_arm_global_ratio()
            #Only one hand, divide by 2
            self.pen_rate += 0.015 / 2.0
            self.resis_dim_rate += 0.01 / 2.0
            
        #Calculate power coefs
        melee_coef = (self.force + self.agility/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
        ranged_coef = (self.force + self.dexterity/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
            
        #Set attack powers
        self.pen_rate /= max(1.0, nb_of_weapons)
        self.resis_dim_rate /= max(1.0, nb_of_weapons)
        self.melee_power = max(1.0, melee_coef * self.melee_power * self.body.melee_attack_global_ratio())
        if self.is_using_a_crossbow():
            self.ranged_power *= 10 #Default power
        else:
            self.ranged_power *= max(1.0, ranged_coef * self.body.ranged_attack_global_ratio())
        self.magic_power_ratio = self.body.global_ratio() * (self.spirit + self.willpower/2) / (1 + 1.0/2) / 10.0
        self.magic_power = self.magic_power_ratio * 100
    
    def calculate_defense(self):
        #Calculate equipments defense
        melee_defense = 0.0
        ranged_defense = 0.0
        shield_magic_defense = 0.0  # Where shield can be used against magic attacks
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                melee_defense += weapon.defense * self.body.weapon_ratio(weapon)
                ranged_defense += weapon.defense * self.body.weapon_ratio(weapon)
                shield_magic_defense += weapon.defense * self.body.weapon_ratio(weapon)
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
             * 10 / (1 + 1.0/2 + 1.0/3) * self.body.global_ratio())
        self.magic_defense_with_shields = self.magic_defense + shield_magic_defense
        
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

    def get_fighting_availability(self, timeline):
        char_defense_time = global_variables.defense_time * self.speed_ratio
        total_time = 0
        for attack_timeline, attack in self.previous_attacks:
            time = attack_timeline + char_defense_time - timeline
            if time > 0:
                total_time += time
        return 1.0 / (1.0 + total_time / char_defense_time)
    
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
            return True
        return False
    
    
###################### DAMAGE FUNCTIONS ########################
    def get_armor_coef(self, accuracy_ratio):
        cover_ratio = self.body.member_cover_ratio(1)
        avoid_armor_chances = (1 - random.gauss(1, Characters.high_variance) * cover_ratio) * accuracy_ratio
        
        if cover_ratio <= 0:
            print("The player has no armor!")
            time.sleep(2)
            return 0
        elif random.random() < avoid_armor_chances:
            print("The hit will avoid the armor!")
            time.sleep(2)
            return 1
        else:
            print("The hit will meet a full armor part")
            time.sleep(2)
            return 0
            
    def damages_received(self, enemy, attack_value, accuracy_ratio, armor_coef, resis_dim_rate, pen_rate):
        enemy.print_basic()
        print("-- has HIT --", end=' ')
        self.print_basic()
        print("-- with a power of", int(round(attack_value)))
        time.sleep(2)        
        
        damage_result = self.body.armor_damage_absorbed(attack_value, 1, armor_coef, resis_dim_rate, pen_rate)
        
        if random.random() * accuracy_ratio < Characters.critical_hit_chance:
            print("The damages are amplified, because they hit a critical area!")
            damage_result *= Characters.critical_hit_boost
        
        if damage_result > 0:
            life_ratio = self.body.loose_life(damage_result, 1)
            # Damages received diminish the defender
            life_ratio = math.pow(2 - life_ratio, 2) - 1
            print("The shock of the attack delays the player of", round(life_ratio,2), "turn(s) and consume stamina")
            time.sleep(3)
            self.spend_time(life_ratio)
            self.spend_stamina(life_ratio * 10, ignore=True)
            
###################### RANGED FUNCTIONS ########################
    def calculate_point_distance(self, abscissa, ordinate):
        return math.sqrt( \
            math.pow(self.abscissa - abscissa, 2) + \
            math.pow(self.ordinate - ordinate, 2))
        
    
    def power_distance_ratio(self, enemy):
        return max(0.25, 1 - \
            self.calculate_point_distance(enemy.abscissa, enemy.ordinate) / self.has_range())
    
    
    def power_hit_chance_ratio(self, hit_chance):
        return math.sqrt(hit_chance / 0.5)
    
        
    def has_range(self):
        max_range = 10000
        for weapon in self.weapons_in_use:
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
    
    def is_distance_magically_reachable(self, enemy):        
        if self.calculate_point_distance(enemy.abscissa, enemy.ordinate) <= Characters.max_magic_distance:
            return True
        return False

    def get_magic_distance_ratio(self, enemy):
        return 1 - self.calculate_point_distance(enemy.abscissa, enemy.ordinate) / Characters.max_magic_distance
    
    def calculate_point_to_enemy_path_distance(self, enemy, abscissa, ordinate):
        # Only work if abscissa & ordinate are in the segment path
        # and if abscissa and ordinate are different from char position
        ac_length = self.calculate_point_distance(abscissa, ordinate)
        ah_length = ac_length * self.calculate_point_to_enemy_path_cos_angle(enemy, abscissa, ordinate)
        return math.sqrt(max(0, math.pow(ac_length, 2) - math.pow(ah_length, 2)))
    
    def has_ammo(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                if self.ranged_weapon_has_ammo(weapon):
                    return True
        return False

    def calculate_point_to_enemy_path_cos_angle(self, enemy, abscissa, ordinate):
        u_abs = enemy.abscissa - self.abscissa
        u_ord = enemy.ordinate - self.ordinate
        v_abs = abscissa - self.abscissa
        v_ord = ordinate - self.ordinate

        return (u_abs * v_abs + u_ord * v_ord) / (
                    math.sqrt(math.pow(u_abs, 2) + math.pow(u_ord, 2)) *
                    math.sqrt(math.pow(v_abs, 2) + math.pow(v_ord, 2)))

    def calculate_point_to_enemy_path_angle(self, enemy, abscissa, ordinate):
        angle = math.acos(
            self.calculate_point_to_enemy_path_cos_angle(enemy, abscissa, ordinate))

        if ordinate < self.ordinate:
            angle = 2 * math.pi - angle

        return angle

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
                ammo_used = weapon.unload()
                break
        return ammo_used
        
        
    def loose_reloaded_ammo(self):
        has_lost = False
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Bows) and weapon.is_reloaded():
                has_lost = True
                weapon.unload()
        return has_lost
        
        
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
        

##################### PRINTING FUNCTIONS ########################
    def print_basic(self):
        print("ID:", self.get_id(), ", Name:", self.name, end=' ')
        
    def print_equipments(self):
        print("")
        print("EQUIPMENTS:")
        self.body.print_full_armors()
        self.print_weapons_in_use()
        self.print_weapons_stored()
        self.print_ammo()

    def print_characteristics(self):
        print("")
        print("CHARACTERISTICS:")
        print("    Constitution:", int(round(self.constitution)),
            ", Force:", int(round(self.force)),
            ", Agility:", int(round(self.agility)),
            ", Dexterity:", int(round(self.dexterity)),
            ", Reflex:", int(round(self.reflex)),
            ", Willpower:", int(round(self.willpower)),
            ", Spirit:", int(round(self.spirit)),
            ", Moral:", int(round(self.moral)),
            ", Empathy:", int(round(self.Empathy)))

    def print_spells_and_feelings(self):
        print("")
        print("FEELINGS:")
        for key in self.feelings:
            print("-", end=' ')
            self.feelings[key].print_obj()
        print("")
        print("Active spells:", self.active_spells)

    def print_defense(self):
        print("")
        print("DEFENSE:")
        print("    ArmorResistance:", int(round(self.armor_resistance)),
            ", ArmorDefense:", int(round(self.armor_defense)),
            ", Dodging:", int(round(self.dodging)),
            ", MeleeDefense:", int(round(self.melee_defense)),
            ", RangedDefense:", int(round(self.ranged_defense)),
            ", MagicDefense:", int(round(self.magic_defense)))

    def print_attack(self):
        print("")
        print("ATTACK:")
        print("    MeleeHandiness:", int(round(self.melee_handiness)),
            ", MeleePower:", int(round(self.melee_power)),
            ", MeleeRange:", int(round(self.melee_range)),
            ", PenetrationRate:", int(round(self.pen_rate, 2)),
            ", resis_dim_rate:", int(round(self.resis_dim_rate, 2)),
            ", MagicPower:", int(round(self.magic_power)), end=' ')
        if self.ranged_power > 1:
            print(", RangedAccuracy:", int(round(self.ranged_accuracy)),
                ", RangedPower:", int(round(self.ranged_power)), end=' ')
            self.print_ranged_info()
        else:
            print("")

    def print_ranged_info(self):
        use_ranged_weapon = False
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                use_ranged_weapon = True
                break
        if use_ranged_weapon:
            max_range = 10000
            for weapon in self.weapons_in_use:
                if isinstance(weapon, RangedWeapons):
                    max_range = min(max_range, weapon.get_max_range())
            print(", MaxRange:", max_range, ", AmmoLeft:", len(self.ammo),
                ", CurrentAmmo:", weapon.current_ammo)
                 
    def print_time_state(self):
        print(", SpeedRatio:", round(self.speed_ratio, 2),
            ", Timeline:", round(self.timeline, 2),
            ", CurrentAction:", self.last_action)

    def print_weapons_stored(self):
        print("Weapons stored:")
        if len(self.weapons_stored) <= 0:
            print("\\No weapon stored")
            return False
        for weapon in self.weapons_stored:
            print("\\", end=' ')
            weapon.print_obj()
        return True

    def print_weapons_in_use(self):
        print("")
        print("Weapons used:")
        if len(self.weapons_in_use) <= 0:
            print("\\No weapon used")
            return False
        for weapon in self.weapons_in_use:
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
        self.print_time_state()
        self.print_defense()
        self.print_attack()
        self.print_spells_and_feelings()

    def print_detailed_state(self):
        self.print_basic()
        print("")
        self.body.print_detailed_basic()
        self.print_time_state()
        self.print_defense()
        self.print_attack()
        self.print_spells_and_feelings()

    def print_defense_state(self):
        self.print_basic()
        self.body.print_basic()
        self.print_time_state()
        self.print_defense()

    def print_attack_state(self):
        self.print_basic()
        self.body.print_basic()
        self.print_time_state()
        self.print_attack()
  
    def print_obj(self):
        self.print_detailed_state()
        self.print_equipments()

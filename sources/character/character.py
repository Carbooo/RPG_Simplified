import math as math
import random as random
import time as time
import copy as copy
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.character.character_body import CharBody
from sources.character.character_equipments import CharEquipments
from sources.character.feeling import Feeling


#############################################################
############# CHARACTERS INSTANCES CLASS ####################
#############################################################
class Character:
    """Common base class for all characters"""
    
    def __init__(self, name, constitution, force, agility, dexterity, reflex, willpower, spirit, morale, empathy,
                 armor, weapon1, weapon2, weapon3, weapon4, ammo_type1, ammo_number1, ammo_type2, ammo_number2,
                 wrath_sensibility, wrath_mastering, wrath_knowledge, joy_sensibility, joy_mastering, joy_knowledge,
                 love_sensibility, love_mastering, love_knowledge, hate_sensibility, hate_mastering, hate_knowledge,
                 fear_sensibility, fear_mastering, fear_knowledge, sadness_sensibility, sadness_mastering, sadness_knowledge,
                 abscissa, ordinate):
        
        # Set ID
        self.ID = len(cfg.char_list) + 1
        cfg.char_list.append(self)
        self.name = name

        # Set characteristics
        self.original_constitution = float(constitution)
        self.constitution = float(constitution)
        self.constitution_ratio = float(constitution) / 10.0
        self.original_force = float(force)
        self.force = float(force)
        self.force_ratio = float(force) / 10.0
        self.true_original_agility = float(agility)  # To handle the fact that bulk/load influences agility
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
        self.original_morale = float(morale)
        self.true_original_morale = float(morale)  # To handle team state influence
        self.morale = float(morale)
        self.morale_ratio = float(morale) / 10.0
        self.original_empathy = float(empathy)
        self.empathy = float(empathy)
        self.empathy_ratio = float(empathy) / 10.0
        
        self.body = CharBody(
            self,
            float(self.constitution) * 10.0, 
            (float(self.constitution) + float(self.willpower)/3 + float(self.agility)/2 + float(self.force)/2) 
            / (1.0 + 1.0/3 + 2.0/2) * 10.0
        )
        
        self.equipments = CharEquipments(
            self, armor, 
            weapon1, weapon2, weapon3, weapon4,
            ammo_type1, ammo_number1, ammo_type2, ammo_number2
        )
        
        # Set characters parameters
        self.timeline = 0.0
        self.set_initial_position(abscissa, ordinate)
        self.last_action = None
        self.previous_attacks = []
        self.active_spells = []
        self.team_state = 1.0
        self.is_a_zombie = False
        self.coef_speed_ratio = 1.0
        
        # Set feelings
        self.nb_of_concentrate = 0
        self.feelings = {
            "Wrath" : Feeling("Wrath", wrath_sensibility, wrath_mastering, wrath_knowledge),
            "Joy": Feeling("Joy", joy_sensibility, joy_mastering, joy_knowledge),
            "Love": Feeling("Love", love_sensibility, love_mastering, love_knowledge),
            "Hate": Feeling("Hate", hate_sensibility, hate_mastering, hate_knowledge),
            "Fear": Feeling("Fear", fear_sensibility, fear_mastering, fear_knowledge),
            "Sadness": Feeling("Sadness", sadness_sensibility, sadness_mastering, sadness_knowledge)
        }
        
        # Calculate character characteristics
        self.load_ratio = 0.0
        self.use_load_ratio = 0.0
        self.bulk_ratio = 0.0
        self.use_bulk_ratio = 0.0
        self.speed_ratio = 0.0
        self.melee_handiness = 0.0
        self.melee_handiness_ratio = 0.0
        self.ranged_accuracy = 0.0
        self.ranged_accuracy_ratio = 0.0
        self.melee_range = 0.0
        self.pen_rate = 0.0
        self.resis_dim_rate = 0.0
        self.melee_power = 0.0
        self.ranged_power = 0.0
        self.magic_power = 0.0
        self.magic_power_ratio = 0.0
        self.melee_defense = 0.0
        self.ranged_defense = 0.0
        self.magic_defense = 0.0
        self.magic_defense_with_shields = 0.0
        self.dodging = 0.0
        self.calculate_characteristic()
        
    def get_id(self):
        return self.ID

################### UPDATE STAT FUNCTIONS ######################
    def update_constitution(self, difference):
        self.constitution += difference
        self.constitution_ratio = self.constitution / 10.0

    def update_force(self, difference):
        self.force += difference
        self.force_ratio = self.force / 10.0

    def update_agility(self, difference):
        self.agility += difference
        self.agility_ratio = self.agility / 10.0

    def update_dexterity(self, difference):
        self.dexterity += difference
        self.dexterity_ratio = self.dexterity / 10.0

    def update_reflex(self, difference):
        self.reflex += difference
        self.reflex_ratio = self.reflex / 10.0

    def update_willpower(self, difference):
        self.willpower += difference
        self.willpower_ratio = self.willpower / 10.0

    def update_spirit(self, difference):
        self.spirit += difference
        self.spirit_ratio = self.spirit / 10.0

    def update_morale(self, difference):
        self.morale += difference
        self.morale_ratio = self.morale / 10.0

######################### CHARACTERISTICS FUNCTIONS ########################
    def get_global_ratio(self):
        return self.body.get_global_ratio() * self.morale_ratio

    def calculate_load_ratios(self):
        self.load_ratio = min(cfg.max_bonus,
                              cfg.load_mean
                              / max(1.0, self.equipments.get_full_load())
                              * self.force_ratio)
        
        self.use_load_ratio = min(cfg.max_bonus,
                                  cfg.use_load_mean
                                  / max(1.0, self.equipments.get_in_use_load())
                                  * self.force_ratio)

    def calculate_bulk_ratios(self):
        self.bulk_ratio = min(cfg.max_bonus,
                              cfg.bulk_mean
                              / max(1.0, self.equipments.get_full_bulk())
                              * self.force_ratio)

        self.use_bulk_ratio = min(cfg.max_bonus,
                                  cfg.use_bulk_mean
                                  / max(1.0, self.equipments.get_in_use_bulk())
                                  * self.force_ratio)
    
    def calculate_morale(self):
        previous_morale = self.original_morale
        self.original_morale = self.true_original_morale \
                * math.pow(self.team_state, cfg.team_state_effect_on_moral)
        new_morale = self.original_morale
        self.morale *= new_morale / previous_morale
    
    def calculate_agility(self):
        previous_agility = self.original_agility
        self.original_agility = self.true_original_agility \
                                * math.pow(self.load_ratio, 1.0 / 3.0) \
                                * math.pow(self.use_load_ratio, 1.0 / 2.0)
        new_agility = self.original_agility
        self.agility *= new_agility / previous_agility

    def calculate_speed_ratio(self):
        self.speed_ratio = max(cfg.min_speed, self.get_global_ratio() * self.coef_speed_ratio)

    def calculate_accuracies(self):
        weapons_accuracies = self.equipments.calculate_accuracies()
        
        # Calculate accuracy coefs
        melee_coef = (self.dexterity + self.agility/2 + self.force/3) / (1 + 1.0/2 + 1.0/3)
        if self.equipments.is_using_a_crossbow():
            ranged_coef = (self.dexterity + self.agility/3 + self.reflex/3) / (1 + 2.0/3)
        else:
            ranged_coef = (self.dexterity + self.force/2 + self.agility/3 + self.reflex/3) / (1 + 1.0/2 + 2.0/3)
        
        # Set accuracies
        self.melee_handiness = self.get_global_ratio() * melee_coef * weapons_accuracies["melee_weapons"]
        self.melee_handiness_ratio = self.melee_handiness / cfg.accuracy_mean
        self.ranged_accuracy = self.get_global_ratio() * ranged_coef * weapons_accuracies["ranged_weapons"]
        self.ranged_accuracy_ratio = self.ranged_accuracy / cfg.accuracy_mean
         
    def calculate_melee_range(self):
        self.melee_range = self.equipments.calculate_melee_range()
     
    def calculate_attack_power(self):
        attack_powers = self.equipments.calculate_attack_power()
            
        # Calculate power coefs
        melee_coef = (self.force + self.agility/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
        ranged_coef = (self.force + self.dexterity/2 + self.willpower/3) / (1 + 1.0/2 + 1.0/3)
        magical_coef = (self.spirit + self.willpower/2) / (1 + 1.0/2)
            
        # Set attack powers
        self.pen_rate = attack_powers["pen_rate"]
        self.resis_dim_rate = attack_powers["resis_dim_rate"]
        self.melee_power = self.get_global_ratio() * melee_coef * attack_powers["melee_power"]
        if self.equipments.is_using_a_crossbow():
            self.ranged_power = 10.0 * attack_powers["ranged_power"]  # Physical state doesn't influence crossbow power
        else:
            self.ranged_power = self.get_global_ratio() * ranged_coef * attack_powers["ranged_power"]
        self.magic_power = self.get_global_ratio() * magical_coef * 10.0
        self.magic_power_ratio = self.magic_power / 100.0
    
    def calculate_defense(self):
        weapons_defense = self.equipments.calculate_defense()
        
        # Calculate defense coefs
        melee_coef = (self.reflex + self.agility/2 + self.force/2) / (1 + 2.0/2)
        # Skills do not really matter for ranged defense, the bigger you are, the harder it is to defend
        ranged_coef = math.sqrt((self.reflex + self.agility/2) / (1 + 1.0/2)) / self.constitution_ratio
        magic_coef = (self.spirit + self.willpower/2 + self.constitution/3) / (1 + 1.0/2 + 1.0/3)
        
        # Set defenses
        self.melee_defense = self.get_global_ratio() * melee_coef * weapons_defense["melee_defense"]
        if weapons_defense["ranged_defense"]:
            self.ranged_defense = self.get_global_ratio() * ranged_coef * weapons_defense["ranged_defense"]
        else:
            self.ranged_defense = self.get_global_ratio() * ranged_coef  # To have some def, even without a shield
        self.magic_defense = self.get_global_ratio() * magic_coef * 10.0
        self.magic_defense_with_shields = self.magic_defense + weapons_defense["magic_defense"]
        
    def calculate_dodging(self):
        # The bigger you are, the harder is to dodge
        dodging_coef = (self.reflex + self.agility) / (1.0 + 1.0) / self.constitution_ratio
        # More bulky equipment, lower dodge ratio (load ratio already included in agility stat)
        dodging_coef *= math.sqrt(math.pow(self.bulk_ratio, 1.0 / 3) * math.pow(self.use_bulk_ratio, 1.0 / 2))
        self.dodging = self.get_global_ratio() * dodging_coef
    
    def calculate_characteristic(self):
        # Must respect the order of the 3 first items
        self.calculate_load_ratios()
        self.calculate_bulk_ratios()
        self.calculate_morale()
        self.calculate_agility()
        
        self.calculate_accuracies()
        self.calculate_melee_range()
        self.calculate_attack_power()

        self.calculate_defense()
        self.calculate_dodging()
        self.calculate_speed_ratio()

    def movement_handicap_ratio(self):
        return math.sqrt(
            (math.pow(self.load_ratio, 1.0 / 2) * math.pow(self.use_load_ratio, 1.0 / 3)) * \
            (math.pow(self.bulk_ratio, 1.0 / 3) * math.pow(self.use_bulk_ratio, 1.0 / 2)))

################### VARIOUS KEY FUNCTIONS ######################
    def exceeded_feelings_check(self):
        has_exceeded = False
        for key in self.feelings:
            if self.feelings[key].die_of_exceeded_energy(self):
                has_exceeded = True
        return has_exceeded

    def spend_time(self, time_spent):
        self.spend_absolute_time(time_spent / self.speed_ratio)

    def spend_absolute_time(self, time_spent):
        self.timeline += time_spent

    def spend_stamina(self, coefficient, ignore=False):
        self.body.spend_stamina(coefficient / self.load_ratio, ignore)

    def check_stamina(self, coefficient):
        return self.body.check_stamina(coefficient / self.load_ratio)

    def check_position(self):
        if self.abscissa not in range(cfg.max_position_area):
            func.optional_print("(Characters) Abscissa must be included in [0:", cfg.max_position_area, "]")
            return False
        if self.ordinate not in range(cfg.max_position_area):
            func.optional_print("(Characters) Ordinate must be included in [0:", cfg.max_position_area, "]")
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

###################### MELEE FUNCTIONS ########################
    def get_fighting_availability(self, timeline):
        char_defense_time = cfg.defense_time / self.speed_ratio
        total_time = 0
        
        # Calculate fighting recovery from previous attack
        for attack_timeline, attack in self.previous_attacks:
            time = attack_timeline + char_defense_time - timeline
            if time > 0:
                if attack.type == "MeleeAttack":
                    total_time += time * cfg.melee_attack_fighting_availability
                elif attack.type == "RangedAttack":
                    total_time += time * cfg.ranged_attack_fighting_availability
                elif attack.type == "Spell":
                    total_time += time * cfg.magic_attack_fighting_availability
                else:
                    print("Error: Fighting availability type (", attack.type, ") not expected!")

        # Calculate fighting readiness regarding char timeline
        readiness_time = self.timeline - timeline
        if self.last_action and self.last_action.type == "MeleeAttack":  # Do not count "counter" attack
            readiness_time = max(0.0, readiness_time - cfg.actions["melee_attack"]["duration"] / self.speed_ratio)

        total_time += readiness_time
        return 1.0 / (1.0 + total_time / char_defense_time)
    
    @staticmethod
    def get_melee_attack(melee_handiness, melee_power):
        return math.pow(melee_power * math.pow(melee_handiness, 1.0/3), 0.75)
    
    @staticmethod
    def get_melee_accuracy(melee_handiness, melee_power):
        return math.pow(melee_power * math.pow(melee_handiness, 1.0/3), 0.75)    
        
    def can_melee_attack(self, enemy):
        if enemy.body.is_alive() and \
                enemy.abscissa in range(self.abscissa - 1, self.abscissa + 2) and \
                enemy.ordinate in range(self.ordinate - 1, self.ordinate + 2):
            return True
        return False
    
###################### DAMAGE FUNCTIONS ########################
    def get_armor_coef(self, accuracy_ratio):
        cover_ratio = self.equipments.get_armor_cover_ratio()
        avoid_armor_chances = (1 - random.gauss(1, cfg.high_variance) * cover_ratio) * accuracy_ratio
        
        if cover_ratio == 0:
            func.optional_print("The player has no armor!", level=2)
            time.sleep(2)
            return 0
        elif random.random() < avoid_armor_chances:
            func.optional_print("The hit will avoid the armor!", level=2)
            time.sleep(2)
            return 0
        else:
            func.optional_print("The hit will meet a full armor part", level=2)
            time.sleep(2)
            return 1
            
    def damages_received(self, enemy, attack_value, accuracy_ratio, armor_coef, resis_dim_rate, pen_rate, flesh_dam_rate=1.0):
        enemy.print_basic()
        func.optional_print("-- has HIT --", skip_line=True, level=3)
        self.print_basic()
        func.optional_print("-- with a power of", int(round(attack_value)), level=3)
        time.sleep(2)

        if accuracy_ratio != 0 and random.random() / accuracy_ratio < cfg.critical_hit_chance:
            func.optional_print("The damages are amplified, because they hit a critical area!", level=3)
            time.sleep(2)
            attack_value *= cfg.critical_hit_boost

        damage_result = self.equipments.armor_damage_absorbed(attack_value, armor_coef, resis_dim_rate, pen_rate, flesh_dam_rate)
        
        if damage_result > 0:
            life_ratio = self.body.loose_life(damage_result)
            # Damages received diminish the defender
            if self.body.is_alive():
                life_ratio = math.pow(2 - life_ratio, 2) - 1
                func.optional_print("The shock of the attack delays the player of", round(life_ratio, 2),
                                    "turn(s) and consume stamina", level=3)
                time.sleep(3)
                self.spend_time(life_ratio)
                self.spend_stamina(life_ratio * 10, ignore=True)
        
        return max(0.0, damage_result)
            
###################### RANGED FUNCTIONS ########################
    def calculate_point_distance(self, abscissa, ordinate):
        return math.sqrt(math.pow(self.abscissa - abscissa, 2) + math.pow(self.ordinate - ordinate, 2))
        
    def is_distance_reachable(self, enemy):        
        if self.calculate_point_distance(enemy.abscissa, enemy.ordinate) <= self.equipments.get_range():
            return True
        return False
    
    def is_distance_magically_reachable(self, abscissa, ordinate):        
        if self.calculate_point_distance(abscissa, ordinate) <= cfg.max_magic_distance:
            return True
        return False

    def is_enemy_magically_reachable(self, enemy):        
        if self.calculate_point_distance(enemy.abscissa, enemy.ordinate) <= cfg.max_magic_distance:
            return True
        return False

    def get_magic_distance_ratio(self, enemy):
        return 1 - self.calculate_point_distance(enemy.abscissa, enemy.ordinate) / cfg.max_magic_distance
    
    def calculate_point_to_enemy_path_distance(self, target_abs, target_ord, abscissa, ordinate):
        # Only work if abscissa & ordinate are in the segment path
        # and if abscissa and ordinate are different from char position
        ac_length = self.calculate_point_distance(abscissa, ordinate)
        ah_length = ac_length * self.calculate_point_to_enemy_path_cos_angle(target_abs, target_ord, abscissa, ordinate)
        return math.sqrt(max(0, math.pow(ac_length, 2) - math.pow(ah_length, 2)))

    def calculate_point_to_enemy_path_cos_angle(self, target_abs, target_ord, abscissa, ordinate):
        u_abs = target_abs - self.abscissa
        u_ord = target_ord - self.ordinate
        v_abs = abscissa - self.abscissa
        v_ord = ordinate - self.ordinate

        return (u_abs * v_abs + u_ord * v_ord) / (
                    math.sqrt(math.pow(u_abs, 2) + math.pow(u_ord, 2)) *
                    math.sqrt(math.pow(v_abs, 2) + math.pow(v_ord, 2)))

    def calculate_point_to_enemy_path_angle(self, enemy, abscissa, ordinate):
        angle = math.acos(
            self.calculate_point_to_enemy_path_cos_angle(enemy.abscissa, enemy.ordinate, abscissa, ordinate))

        if ordinate < self.ordinate:
            angle = 2 * math.pi - angle

        return angle

    def set_target_pos_variation(self, enemy, variation):
        # Calculate angle between enemy and abscissa axis
        c = copy.copy(self)  # Is used for abscissa axis
        c.abscissa += 1
        angle = self.calculate_point_to_enemy_path_angle(c, enemy.abscissa, enemy.ordinate)

        # Set the variated position
        angle += math.radians(variation)
        enemy.abscissa += int(round(self.equipments.get_range() * math.cos(angle)))
        enemy.ordinate += int(round(self.equipments.get_range() * math.sin(angle)))

##################### PRINTING FUNCTIONS ########################
    def print_basic(self):
        func.optional_print("ID:", self.get_id(), ", Name:", self.name, skip_line=True)

    def print_characteristics(self):
        func.optional_print("-- CHARACTERISTICS --", skip_line=True)
        func.optional_print("Constitution:", int(round(self.constitution)),
              ", Force:", int(round(self.force)),
              ", Agility:", int(round(self.agility)),
              ", Dexterity:", int(round(self.dexterity)),
              ", Reflex:", int(round(self.reflex)),
              ", Willpower:", int(round(self.willpower)),
              ", Spirit:", int(round(self.spirit)),
              ", Empathy:", int(round(self.empathy)))

    def print_spells_and_feelings(self):
        func.optional_print("--  FEELINGS  --")
        for key in self.feelings:
            func.optional_print("   -", skip_line=True)
            self.feelings[key].print_obj()
        func.optional_print("--  ACTIVE SPELLS --")
        for spell in self.active_spells:
            func.optional_print("   -", spell.surname)

    def print_defense(self):
        func.optional_print("--   DEFENSE  --", skip_line=True)
        func.optional_print("Dodging:", int(round(self.dodging)),
            ", MeleeDefense:", int(round(self.melee_defense)),
            ", RangedDefense:", int(round(self.ranged_defense)),
            ", MagicDefense:", int(round(self.magic_defense)))

    def print_attack(self):
        func.optional_print("--   ATTACK   --", skip_line=True)
        func.optional_print("MeleeHandiness:", int(round(self.melee_handiness)),
            ", MeleePower:", int(round(self.melee_power)),
            ", MeleeRange:", int(round(self.melee_range)),
            ", PenetrationRate:", int(round(self.pen_rate, 2)),
            ", resis_dim_rate:", int(round(self.resis_dim_rate, 2)),
            ", MagicPower:", int(round(self.magic_power)), skip_line=True)
        if self.ranged_power > 1:
            func.optional_print(", RangedAccuracy:", int(round(self.ranged_accuracy)),
                ", RangedPower:", int(round(self.ranged_power)),
                ", RangedRange:", int(round(self.equipments.get_range())))
        else:
            func.optional_print("")
                 
    def print_time_state(self):
        func.optional_print(", Morale:", round(self.morale, 1), skip_line=True)
        if self.last_action:
            last_action = self.last_action.name
        else:
            last_action = None

        func.optional_print(", SpeedRatio:", round(self.speed_ratio, 2),
            ", Timeline:", round(self.timeline, 2),
            ", CurrentAction:", last_action)

    def print_state(self):
        self.print_basic()
        self.body.print_obj()
        self.print_time_state()

    def print_detailed_state(self):
        func.optional_print("-- BASIC INFO --", skip_line=True)
        self.print_basic()
        self.body.print_obj()
        self.print_time_state()
        self.print_defense()
        self.print_attack()
        self.equipments.print_obj()
        self.print_spells_and_feelings()

    def print_defense_state(self):
        self.print_basic()
        self.body.print_obj()
        self.print_time_state()
        self.print_defense()

    def print_attack_state(self):
        self.print_basic()
        self.body.print_obj()
        self.print_time_state()
        self.print_attack()
  
    def print_obj(self):
        self.print_detailed_state()
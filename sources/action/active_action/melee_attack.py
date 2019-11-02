import math as math
import random as random
import copy as copy
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions


#############################################################
################### MELEE ATTACK CHAR CLASS #################
#############################################################
class MeleeAttack(ActiveActions):
    """Class to melee attack a character"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Melee attacking"
        self.type = "MeleeAttack"
        self.target = None
        self.actual_defense = "None"  # Can be "Dodge", "Defense" or "No defense"
        self.real_end_timeline = 0  # To use the right timeline for get fight availability
        self.is_a_success = self.start()

    def start(self):
        if not self.initiator.check_stamina(cfg.actions["melee_attack"]["stamina"]):
            func.optional_print("You do not have enough stamina (", round(self.initiator.body.stamina, 2), ") for a melee attack")
            return False
        elif not self.choose_target():
            return False

        return True
        
    def choose_target(self):
        if not self.can_melee_attack():
            func.optional_print("No enemy can be reached by a melee attack")
            func.optional_sleep(3)
            return False

        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        func.optional_print("--------- ATTACKER -----------")
        self.initiator.print_attack_state()
        func.optional_print("")

        func.optional_print("--------- TARGETS -----------")
        func.optional_print("Choose one of the following enemies:")
        enemy_list = []
        for char in team.characters_list:
            self.target = char
            if self.initiator.can_melee_attack(self.target):
                func.optional_print("-----------------------------------------")
                self.target.print_defense_state()
                enemy_list.append(self.target)

        while 1:
            try:
                func.optional_print("")
                read = int(func.optional_input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False
            except:
                func.optional_print("The input is not an ID")
                continue

            for char in enemy_list:
                self.target = char
                if self.target.get_id() == read:
                    self.end_update(cfg.actions["melee_attack"]["stamina"], cfg.actions["melee_attack"]["duration"])
                    self.timeline += cfg.actions["melee_attack"]["duration"] * 0.9  # To execute the attack before char get their turn
                    self.real_end_timeline = self.initiator.timeline
                    self.fight.scheduler.append(self)
                    return True

            func.optional_print("ID:", read, "is not available")

    def execute(self):
        self.fight.scheduler.remove(self)

        if not self.initiator.can_melee_attack(self.target):
            func.optional_print("")
            func.optional_print("*********************************************************************")
            func.optional_print("The target (", skip_line=True)
            self.target.print_basic()
            func.optional_print(") is no longer reachable by a melee attack")
            func.optional_print("The attack of (", skip_line=True)
            self.initiator.print_basic()
            func.optional_print(") has been cancelled !")
            func.optional_print("*********************************************************************")
            func.optional_print("")
            func.optional_sleep(5)
            return False

        func.optional_print("")
        func.optional_print("*********************************************************************")
        self.initiator.print_basic()
        func.optional_print("is melee attacking (", skip_line=True)
        self.target.print_basic()
        func.optional_print(")")
        func.optional_print("Initiator fighting availability:", round(
                            self.initiator.get_fighting_availability(self.real_end_timeline), 2),
                            level=3)
        func.optional_print("Target fighting availability:", round(
                            self.target.get_fighting_availability(self.real_end_timeline), 2),
                            level=3)
        func.optional_print("*********************************************************************")
        func.optional_print("")
        func.optional_sleep(3)

        self.initiator.last_action = None  # To avoid looping on this action
        self.fight.stop_action(self.target, self.real_end_timeline)
        attack_result = self.melee_defense_result()
        self.melee_attack_type(attack_result)
        
        # Update availability after computed the result
        self.target.previous_attacks.append((self.real_end_timeline, self))
        self.initiator.previous_attacks.append((self.real_end_timeline, self))
        
        abscissa = self.target.abscissa
        ordinate = self.target.ordinate
        if self.actual_defense == "Dodge" and \
           self.fight.field.random_move(self.target, cfg.random_defenser_move_probability * 2):
                func.optional_print("The fight made the defenser move from their position!")
                func.optional_sleep(2)
                if random.random() < cfg.random_attacker_move_probability:
                    self.fight.field.move_character(self.initiator, abscissa, ordinate)
                    func.optional_print("And the attacker took the initial position of the defender!")
                    func.optional_sleep(2)
                
        elif self.actual_defense == "Defense" and \
             self.fight.field.random_move(self.target, cfg.random_defenser_move_probability):
                func.optional_print("The fight made the defenser move from their position!")
                func.optional_sleep(2)
                if random.random() < cfg.random_attacker_move_probability:
                    self.fight.field.move_character(self.initiator, abscissa, ordinate)
                    func.optional_print("And the attacker took the initial position of the defender!")
                    func.optional_sleep(2)
                
        return True

    def melee_defense_result(self):
        # Calculate attack
        attack_accuracy = self.initiator.melee_handiness * ActiveActions.get_attack_coef(self.initiator, self.real_end_timeline)
        attack_power = self.initiator.melee_power * ActiveActions.get_attack_coef(self.initiator, self.real_end_timeline)
        func.optional_print("attack_accuracy", attack_accuracy, level=3, debug=True)
        func.optional_print("attack_power", attack_power, level=3, debug=True)

        # Choose between dodge and def
        dodge_result = attack_accuracy - self.target.dodging
        defense_result = attack_power - self.target.melee_defense
        if not self.target.check_stamina(cfg.actions["melee_attack"]["stamina"]):
            func.optional_print("The defender does not have enough stamina (", round(self.target.body.stamina, 2),
                                ") to defend", level=3)
            self.actual_defense = "No defense"
        elif dodge_result < defense_result:
            func.optional_print("The defender is trying to dodge the attack.", level=3)
            self.actual_defense = "Dodge"
        else:
            func.optional_print("The defender is trying to block the attack.", level=3)
            self.actual_defense = "Defense"

        # Calculate real defense
        dodge_level = self.target.dodging * ActiveActions.get_attack_coef(self.target, self.real_end_timeline)
        defense_level = self.target.melee_defense * ActiveActions.get_attack_coef(self.target, self.real_end_timeline)
        func.optional_print("dodge_level", dodge_level, level=3, debug=True)
        func.optional_print("defense_level", defense_level, level=3, debug=True)

        # Calculate final result
        coef = max(self.initiator.get_fighting_availability(self.real_end_timeline),
                   self.target.get_fighting_availability(self.real_end_timeline))  # To be fair in case of mutual attack
        dodge_result = (attack_accuracy - dodge_level) / coef
        defense_result = (attack_power - defense_level) / coef

        if self.actual_defense == "Dodge":
            attack_result = dodge_result + defense_result / cfg.def_type_ratio
            self.target.spend_stamina(cfg.actions["melee_attack"]["stamina"])
            self.target.equipments.all_weapons_absorbed_damage(min(attack_power, defense_level) / cfg.def_type_ratio, self.initiator.resis_dim_rate)
        elif self.actual_defense == "Defense":
            attack_result = defense_result + dodge_result / cfg.def_type_ratio
            self.target.spend_stamina(cfg.actions["melee_attack"]["stamina"])
            self.target.equipments.all_weapons_absorbed_damage(min(attack_power, defense_level), self.initiator.resis_dim_rate)
        else:
            attack_result = attack_power + attack_accuracy/ cfg.def_type_ratio
            
        return attack_result

    def melee_attack_type(self, attack_value):
        func.optional_print("attack_result", attack_value, level=3, debug=True)
        if attack_value < cfg.melee_attack_stage[0]:
            # Block for very weak attack
            self.block()
            func.optional_sleep(3)
        elif attack_value < cfg.melee_attack_stage[1]:
            # Delay or small hit for weak attack
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
            else:
                func.optional_print("The attack is a small hit", level=3)
                power_ratio = random.uniform(0.2, 0.66)
                area_ratio = math.pow(1 - power_ratio, 2.0)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)
            func.optional_sleep(3)
        elif attack_value < cfg.melee_attack_stage[2]:
            # Big delay or normal hit for medium attack
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
                func.optional_sleep(3)
            else:
                func.optional_print("The attack is a normal hit", level=3)
                power_ratio = random.uniform(0.66, 1.0)
                area_ratio = math.pow(1.85 - power_ratio, 2.5)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)
        elif attack_value < cfg.melee_attack_stage[3]:
            # Big hit or hit + small delay for strong attack
            r = random.random()
            if r < 0.33:
                func.optional_print("The attack will hit and slightly delay the player!", level=3)
                func.optional_sleep(2)
                power_ratio = random.uniform(0.66, 1.0)
                area_ratio = math.pow(1.85 - power_ratio, 2.5)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.delay(attack_value / 3)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)
            elif r < 0.66:
                func.optional_print("The attack is a strong hit!", level=3)
                power_ratio = random.uniform(0.85, 1.25)
                area_ratio = math.pow(2.35 - power_ratio, 2.0)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)
        else:
            # Gigantic hit or big hit + delay for massive attack
            r = random.random()
            if r < 0.5:
                func.optional_print("The attack will strongly hit AND delay the player!", level=3)
                func.optional_sleep(2)
                power_ratio = random.uniform(0.85, 1.25)
                area_ratio = math.pow(2.35 - power_ratio, 2.0)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.delay(attack_value / 2)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)
            else:
                func.optional_print("The attack is a HUGE HIT!", level=3)
                func.optional_sleep(2)
                power_ratio = random.uniform(1.0, 1.66)
                area_ratio = math.pow(3.0 - power_ratio, 2.0)
                func.optional_print("power_ratio", power_ratio, level=3, debug=True)
                func.optional_print("area_ratio", area_ratio, level=3, debug=True)
                self.melee_attack_received(self.initiator.melee_power * power_ratio, area_ratio)

    def block(self):
        self.target.print_basic(level=3)
        func.optional_print("-- has SUCCESSFULLY DEFENDED against the attack of --", skip_line=True, level=3)
        self.initiator.print_basic(level=3)
        func.optional_print("", level=3)

    def delay(self, attack_value):
        attack_value /= cfg.melee_attack_stage[3] / 2
        attack_value = math.sqrt(attack_value)
        self.target.spend_time(attack_value)
        self.initiator.print_basic(level=3)
        func.optional_print("-- has DELAYED --", skip_line=True, level=3)
        self.target.print_basic(level=3)
        func.optional_print("-- of", round(attack_value, 2), "TURN(S) --", level=3)
    
    def melee_attack_received(self, attack_value, damages_coef):
        ### Choose which weapon has hit the target ###
        # List all weapons
        weapons = copy.copy(self.initiator.equipments.weapons_in_use)
        for i in range(self.initiator.equipments.free_hands):
            weapons.append("free_hand")

        # Find the "best" weapon
        best_weapon = "free_hand"
        melee_power = cfg.free_hand_melee_power
        for weapon in weapons:
            if weapon != "free_hand" and weapon.melee_power > melee_power:
                best_weapon = weapon
                melee_power = weapon.melee_power

        # Select the weapon (higher attack value = higher chance of better weapon)
        ratio = attack_value / cfg.melee_attack_stage[3]
        hitting_weapon = best_weapon
        if random.random() > ratio:  # Choose the worst weapon
            for weapon in weapons:
                if weapon != best_weapon:
                    hitting_weapon = weapon
                    break

        # Print weapon name
        if hitting_weapon == "free_hand":
            weapon_name = "his/her free hand"
        else:
            weapon_name = hitting_weapon.name
        self.initiator.print_basic(level=3)
        func.optional_print("-- is hitting with --", weapon_name.upper(), level=3)

        ### Calculate weapon stats ###
        if hitting_weapon == "free_hand":
            handiness_ratio = cfg.free_hand_melee_handiness / cfg.accuracy_mean
            life_rate = cfg.free_hand_life_rate
            ignoring_armor_rate = cfg.free_hand_ignoring_armor_rate
            pen_rate = cfg.free_hand_pen_rate
            resis_dim_rate = cfg.free_hand_resis_dim_rate
        else:
            handiness_ratio = hitting_weapon.melee_handiness / cfg.accuracy_mean
            life_rate = hitting_weapon.life_rate
            ignoring_armor_rate = hitting_weapon.ignoring_armor_rate
            pen_rate = hitting_weapon.pen_rate
            resis_dim_rate = hitting_weapon.resis_dim_rate

        ### Hitting result ###
        armor_coef = self.target.get_armor_coef(handiness_ratio * math.sqrt(damages_coef))
        if armor_coef == 0:
            attack_value /= cfg.no_armor_power_ratio
        self.target.damages_received(
            self.initiator, 
            attack_value,
            armor_coef, 
            damages_coef,
            life_rate,
            ignoring_armor_rate,
            pen_rate,
            resis_dim_rate
        )

    def can_melee_attack(self):
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        for char in team.characters_list:
            if self.initiator.can_melee_attack(char):
                return True
        return False

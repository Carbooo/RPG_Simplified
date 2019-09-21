import copy as copy
import math as math
import time as time
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions
from sources.action.active_action.move import Move


#############################################################
################### RANGED ATTACK CHAR CLASS ################
#############################################################
class RangedAttack(ActiveActions):
    """Class to ranged attack a character"""

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Ranged attacking"
        self.target = None
        self.ammo_used = self.initiator.equipments.get_current_ammo()
        self.shooting_time = 1
        self.is_a_success = self.start()

    def start(self):  # Choose ranged target and shoot mode
        if self.initiator.check_stamina(cfg.actions["ranged_attack"]["stamina"]) is False:
            func.optional_print("You do not have enough stamina (",
                  self.initiator.body.get_current_stamina(), ") for a ranged attack")
            return False
        elif self.initiator.equipments.is_using_a_ranged_weapon() is False:
            func.optional_print("You are not using a ranged weapon")
            return False
        elif self.initiator.equipments.has_ammo() is False:
            func.optional_print("No ammo for a ranged attack")
            return False
        elif self.initiator.equipments.has_reloaded() is False:
            func.optional_print("Ranged weapons are not reloaded")
            return False
        elif self.can_ranged_attack() is False:
            func.optional_print("No enemy can be reached by a ranged attack")
            time.sleep(2)
            return False

        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        func.optional_print("--------- ATTACKER -----------")
        self.initiator.print_attack_state()
        func.optional_print("")

        func.optional_print("--------- TARGETS -----------")
        func.optional_print("Choose one of the reachable enemies:")
        
        enemy_list = []
        hit_chance_list = []
        for char in team.characters_list:
            self.target = char
            if self.fight.field.is_target_reachable(self.initiator, self.target):
                enemy_list.append(self.target)
                hit_chance_list.append(self.shoot_hit_chance())

        # Print in hit chance order
        enemy_list_bis = copy.copy(enemy_list)
        hit_chance_list_bis = copy.copy(hit_chance_list)
        while len(hit_chance_list_bis) > 0:
            hit_number = -1
            hit_chance = 0
            for j in range(len(hit_chance_list_bis)):
                if hit_chance_list_bis[j] > hit_chance:
                    hit_chance = hit_chance_list_bis[j]
                    hit_number = j
            self.target = enemy_list_bis.pop(hit_number)
            hit_chance_list_bis.pop(hit_number)
            func.optional_print("--------------------------------------------------------------------")
            self.target.print_defense_state()
            func.optional_print("----   HIT CHANCE:", round(hit_chance, 2),
                                "---- RANGE POWER:", int(round(self.get_range_power(hit_chance))),
                                "----")

        while 1:
            try:
                func.optional_print("")
                read = int(func.optional_input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False
            except:
                func.optional_print("The input is not an ID")
                continue

            for i in range(len(enemy_list)):
                if enemy_list[i].get_id() == read:
                    self.target = enemy_list[i]
                    hit_chance = hit_chance_list[i]
                    self.shooting_time *= self.shoot_speed(hit_chance)
                    
                    if self.initiator.equipments.is_using_a_crossbow():
                        stamina = cfg.actions["ranged_attack"]["stamina"] * self.shooting_time / 10
                    else:
                        stamina = cfg.actions["ranged_attack"]["stamina"] * self.shooting_time
                    self.end_update(stamina, cfg.actions["ranged_attack"]["duration"] * self.shooting_time)
                    return True

            func.optional_print("ID:", read, "is not available")

    def shoot_speed(self, hit_chance):
        # Harder is the target to hit, longer it takes to aim and shoot (between 0.66 to 2)
        return 0.66 + 1.34 * (1 - hit_chance)

    def execute(self):
        if not self.fight.field.is_target_reachable(self.initiator, self.target):
            func.optional_print("")
            func.optional_print("*********************************************************************")
            func.optional_print("The target (", skip_line=True)
            self.target.print_basic()
            func.optional_print(") is no longer reachable by a ranged attack")
            func.optional_print("The attack of (", skip_line=True)
            self.initiator.print_basic()
            func.optional_print(") has been cancelled !")
            func.optional_print("*********************************************************************")
            func.optional_print("")
            time.sleep(5)
            return False
        
        self.initiator.last_action = None  # To avoid looping on this action
        func.optional_print("")
        func.optional_print("*********************************************************************")
        self.initiator.print_basic()
        func.optional_print("is trying to ranged shoot (", skip_line=True)
        self.target.print_basic()
        func.optional_print(")")
        hit_chance = self.shoot_hit_chance()
        func.optional_print("Current hit chance:", round(hit_chance, 2), level=2)
        func.optional_print("Range power:", int(round(self.get_range_power(hit_chance))), level=2)
        func.optional_print("Fighting availability:", round(self.target.get_fighting_availability(self.initiator.timeline), 2),
                            level=2)
        func.optional_print("*********************************************************************")
        func.optional_print("")
        time.sleep(3)
        
        target = self.fight.field.shoot_has_hit_another_target(self.initiator, self.target, hit_chance)
        if not target:
            func.optional_print("The shoot has missed its target!", level=2)
            func.optional_print("No damage has been made.")
            time.sleep(4)

        elif target is True:
            func.optional_print("The shoot has hit its target!", level=2)
            time.sleep(3)
            self.range_defend(hit_chance)

        else:
            func.optional_print("The shoot has hit the WRONG target! It has hit:", level=2)
            target.print_basic()
            target.print_position()
            self.target = target
            time.sleep(3)
            self.range_defend(math.sqrt(1 - hit_chance))

        self.initiator.equipments.use_ammo()
        return True

    def range_defend(self, hit_chance):
        self.fight.stop_action(self.target, self.initiator.timeline)

        # Range defense result
        attack_power = self.get_range_power(hit_chance) * self.get_attack_coef(self.initiator)
        defense_level = self.target.ranged_defense * self.get_attack_coef(self.target)
        attack_result = attack_power - defense_level

        # Update availability after computed the result
        self.target.previous_attacks.append((self.initiator.timeline, self))
        
        # Attack result --> Either block or be hit
        if attack_result <= cfg.ranged_attack_stage[0]:
            self.target.equipments.all_shields_absorbed_damage(attack_power, self.ammo_used.resis_dim_rate)
            func.optional_print("The attack has been fully blocked / avoided by the defender", level=2)
            time.sleep(5)
        else:
            accuracy_ratio = 0.5 + hit_chance  # Between 0,5 and 1,5, similar to melee handiness_ratio
            armor_coef = self.target.get_armor_coef(accuracy_ratio)
            self.target.damages_received(self.initiator, attack_result, accuracy_ratio, armor_coef,
                                         self.ammo_used.resis_dim_rate, self.ammo_used.pen_rate,
                                         self.ammo_used.flesh_damage)

    def shoot_hit_chance(self):
        # Distance = -a*(x-1) + b --> distance min = 1.0, distance max = 0.0
        h_dist = max(cfg.min_distance_ratio,
                     1.0 -
                     (self.initiator.calculate_point_distance(self.target.abscissa, self.target.ordinate) - 1.0)
                     * cfg.decrease_hit_chance_per_case / self.initiator.ranged_accuracy_ratio)
        h_obs = self.fight.field.calculate_ranged_obstacle_ratio(self.initiator, self.target.abscissa, self.target.ordinate)
        h_action = self.get_ranged_action_ratio()
        return h_dist * h_obs * h_action

    def get_ranged_action_ratio(self):
        nb_of_attacks = 0
        for attack_timeline, attack in self.target.previous_attacks:
            if self.timeline < attack_timeline + cfg.defense_time / self.target.speed_ratio:
                nb_of_attacks += 1

        if nb_of_attacks > 0:
            coef = math.pow(cfg.melee_fighter_shooting_handicap, nb_of_attacks)
        else:
            coef = 1

        if isinstance(self.target.last_action, Move):
            coef *= cfg.moving_char_shooting_handicap

        return coef
    
    @staticmethod
    def range_power_hit_chance_ratio(hit_chance):
        return math.pow(hit_chance / 0.5, 1.0/3.0)
    
    def range_power_distance_ratio(self):
        return max(cfg.min_range_power_ratio,
                   1 - self.initiator.calculate_point_distance(self.target.abscissa, self.target.ordinate)
                   / self.initiator.equipments.get_range())

    def get_range_power(self, hit_chance):
        return self.initiator.ranged_power \
                * self.range_power_distance_ratio() \
                * RangedAttack.range_power_hit_chance_ratio(hit_chance) \

    def can_ranged_attack(self):
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        for char in team.characters_list:
            if self.fight.field.is_target_reachable(self.initiator, char):
                return True
        return False

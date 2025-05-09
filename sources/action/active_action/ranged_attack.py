import copy as copy
import math as math
import random as random
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions


#############################################################
################### RANGED ATTACK CHAR CLASS ################
#############################################################
class RangedAttack(ActiveActions):
    """Class to ranged attack a character"""

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Ranged attacking"
        self.type = "RangedAttack"
        self.target = None
        self.ammo_used = self.initiator.equipments.get_current_ammo()
        self.shooting_time = 1
        self.is_a_success = self.start()

    def start(self):  # Choose ranged target and shoot mode
        if not super().start():
            return False
        if self.initiator.check_stamina(cfg.actions["ranged_attack"]["stamina"]) is False:
            func.optional_print("You do not have enough stamina (",
                  round(self.initiator.body.stamina, 2), ") for a ranged attack")
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
            func.optional_sleep(2)
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
                                "---- RANGE POWER:", int(round(self.get_range_power())),
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

                    self.target.add_previous_attack(self.start_timeline, self.initiator.timeline, self)
                    return True

            func.optional_print("ID:", read, "is not available")

    def shoot_speed(self, hit_chance):
        # Harder is the target to hit, longer it takes to aim and shoot (between 0.75 to 2)
        return 0.75 + 1.34 * (1 - hit_chance)

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
            func.optional_sleep(5)
            return False

        func.optional_print("")
        func.optional_print("*********************************************************************")
        self.initiator.print_basic()
        func.optional_print("is trying to ranged shoot (", skip_line=True)
        self.target.print_basic()
        func.optional_print(")")
        hit_chance = self.shoot_hit_chance()
        func.optional_print("Current hit chance:", round(hit_chance, 2), level=3)
        func.optional_print("Range power:", int(round(self.get_range_power())), level=2)
        func.optional_print("Initiator fighting availability:", round(
            self.initiator.get_fighting_availability(self.start_timeline, self.initiator.timeline, self), 2),
                            level=3)
        func.optional_print("Target fighting availability:", round(
            self.target.get_fighting_availability(self.start_timeline, self.initiator.timeline, self), 2),
                            level=3)
        func.optional_print("*********************************************************************")
        func.optional_print("")
        func.optional_sleep(3)

        target = self.fight.field.shoot_has_hit_another_target(self.initiator, self.target, hit_chance)
        if not target:
            func.optional_print("The shoot has missed its target!", level=3)
            func.optional_print("No damage has been made.")
            func.optional_sleep(4)

        elif target is True:
            func.optional_print("The shoot has hit its target!", level=2)
            func.optional_sleep(3)
            self.range_defend(hit_chance)

        else:
            func.optional_print("The shoot has hit the WRONG target! It has hit:", level=3)
            target.print_basic()
            target.print_position()
            self.target = target
            func.optional_sleep(3)
            self.range_defend(math.sqrt(1 - hit_chance))

        self.initiator.last_action = None  # To avoid looping on this action
        self.initiator.equipments.use_ammo()
        return True

    def range_defend(self, hit_chance):
        # Range defense result
        # The higher the shoot is precised, the more chance it is to hurt the target
        # The further the target is, the easiest it is to anticipate and defend
        accuracy_ratio = RangedAttack.range_hit_chance_ratio(hit_chance)
        attack_power = self.initiator.ranged_accuracy * accuracy_ratio \
                       * self.get_attack_coef(self.initiator, self.initiator.timeline)
        defense_level = self.target.ranged_defense * self.range_defense_ratio() \
                       * self.get_attack_coef(self.target, self.initiator.timeline)
        attack_result = attack_power - defense_level
        range_power = self.get_range_power() * random.gauss(cfg.mean, cfg.variance)
        damages_ratio = attack_result / defense_level
        func.optional_print("attack_power", attack_power, level=3, debug=True)
        func.optional_print("defense_level", defense_level, level=3, debug=True)
        func.optional_print("attack_result", attack_result, level=3, debug=True)
        func.optional_print("range_power", range_power, level=3, debug=True)
        func.optional_print("damages_ratio", damages_ratio, level=3, debug=True)

        self.stop_action(self.target, self.initiator.timeline)
        # Attack result --> Either block or be hit
        if attack_result <= cfg.ranged_attack_stage[0]:
            self.target.equipments.all_shields_absorbed_damage(range_power, self.ammo_used.resis_dim_rate)
            func.optional_print("The attack has been fully blocked / avoided by the defender", level=3)
            func.optional_sleep(5)
        else:
            self.target.damages_received(self.initiator, range_power, 1.0, damages_ratio,
                                         self.ammo_used.life_rate, self.ammo_used.ignoring_armor_rate,
                                         self.ammo_used.pen_rate, self.ammo_used.resis_dim_rate)

    def shoot_hit_chance(self):
        # Estimate the distance difficulty
        # Distance = -a*(x-1) + b --> distance min = 1.0, distance max = 0.0
        h_dist = 1.0 - \
                 (self.initiator.calculate_point_distance(self.target.abscissa, self.target.ordinate) - 1.0) \
                 * cfg.decrease_hit_chance_per_case

        # Estimate the obstacle handicap
        h_obs = self.fight.field.calculate_ranged_obstacle_ratio(self.initiator, self.target.abscissa,
                                                                 self.target.ordinate)

        func.optional_print("h_dist: ", h_dist, level=3, debug=True)
        func.optional_print("h_obs: ", h_obs, level=3, debug=True)
        func.optional_print("self.get_ranged_action_ratio(): ", self.get_ranged_action_ratio(), level=3, debug=True)
        func.optional_print("self.initiator.ranged_accuracy_ratio: ", self.initiator.ranged_accuracy_ratio, level=3, debug=True)
        return min(cfg.max_range_hit_chance,
                   max(cfg.min_range_hit_chance,
                       h_dist * h_obs
                       * self.get_ranged_action_ratio()  # Estimate the target action handicap
                       * self.initiator.ranged_accuracy_ratio  # Take in account the skills of the attacker
                       )
                   )

    def get_ranged_action_ratio(self):
        # Estimate the melee fight handicap
        total_time = 0
        for attack in self.target.previous_attacks:
            if attack["action"].type == "MeleeAttack":
                if self.fight.current_timeline == self.start_timeline:
                    total_time += 1
                else:
                    real_start_time = max(attack["start_time"], self.start_timeline)
                    real_end_time = min(attack["end_time"], self.initiator.timeline)
                    time = (real_end_time - real_start_time) / (attack["end_time"] - attack["start_time"])
                    total_time += time
        coef = max(0.0, 1.0 - cfg.melee_fighter_shooting_handicap * math.sqrt(total_time))

        # Estimate movement handicap
        action = self.target.last_action
        if action and action.type == "Move":
            # Handicap is at its maximum for square angles
            angle = self.target.calculate_point_to_enemy_path_cos_angle(action.target_abs, action.target_ord,
                                                                        self.initiator.abscissa, self.initiator.ordinate)
            coef *= 1.0 - cfg.moving_char_shooting_handicap * abs(abs(angle) - 1)

        return coef

    @staticmethod
    def range_hit_chance_ratio(hit_chance):
        return math.sqrt(0.5 + hit_chance)  # Between 0,7 and 1,2

    def range_defense_ratio(self):
        return 1.0 + math.pow(self.range_distance_ratio(), 4) * 10  # Great bonus if you are really far away

    def range_distance_ratio(self):
        return self.initiator.calculate_point_distance(self.target.abscissa, self.target.ordinate) \
               / self.initiator.equipments.get_range()

    def get_range_power(self):
        return self.initiator.ranged_power * (1 - self.range_distance_ratio())

    def can_ranged_attack(self):
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        for char in team.characters_list:
            if self.fight.field.is_target_reachable(self.initiator, char):
                return True
        return False

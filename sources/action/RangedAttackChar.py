import copy as copy
import math as math
import random as random
import time as time
import sources.miscellaneous.global_variables as global_variables
from sources.character.Characters import Characters
from sources.action.Actions import ActiveActions
from sources.action.MoveChar import MoveChar


#############################################################
################### RANGED ATTACK CHAR CLASS ################
#############################################################
class RangedAttackChar(ActiveActions):
    """Class to ranged attack a character"""

    attack_effect = [25, 50]  # [Blocked", "Hit", "Hit & stopped"]
    move_char_handicap = 0.66
    melee_fight_handicap = 0.75

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Ranged attacking"
        self.target = None
        self.ammo_used = self.initiator.get_current_ammo()
        self.shooting_time = 1
        self.is_a_success = self.start()

    def start(self):  # Choose ranged target and shoot mode
        if self.initiator.check_stamina(Characters.RangedAttack[3]) is False:
            print("You do not have enough stamina (",
                  self.initiator.body.get_current_stamina(), ") for a ranged attack")
            return False
        elif self.initiator.is_using_a_ranged_weapon() is False:
            print("You are not using a ranged weapon")
            return False
        elif self.can_ranged_attack() is False:
            print("No enemy can be reached by a ranged attack")
            time.sleep(2)
            return False

        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        print("--------- ATTACKER -----------")
        self.initiator.print_attack_state()
        print("")

        print("--------- TARGETS -----------")
        print("Choose one of the following enemies:")
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
            print("----- HIT CHANCE:", round(hit_chance_list_bis.pop(hit_number), 2))
            print("----- Fighting availability: ",
                  self.target.get_fighting_availability(self.timeline),
                  " -----")
            self.target.print_state()

        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if self.fight.cancel_action(read):
                    return False
            except:
                print("The input is not an ID")
                continue

            for i in range(len(enemy_list)):
                if enemy_list[i].get_id() == read:
                    self.target = enemy_list[i]
                    hit_chance = hit_chance_list[i]
                    self.shooting_time *= self.shoot_speed(hit_chance)
                    return self.result()

            print("ID:", read, "is not available")

    def shoot_speed(self, hit_chance):
        # Harder is the target to hit, longer it takes to aim and shoot (between 0.66 to 2)
        return 0.66 + 1.34 * (1 - hit_chance)

    def result(self):
        print("")
        print("*********************************************************************")
        self.initiator.print_basic()
        print("is trying to ranged shoot (", end=' ')
        self.target.print_basic()
        print(")")
        hit_chance = self.shoot_hit_chance()
        print("Current hit chance:", round(hit_chance, 2))
        print("*********************************************************************")
        print("")
        time.sleep(5)

        self.fight.stop_action(self.target, self.timeline)

        target = self.fight.field.shoot_has_hit_another_target(self.initiator, self.target, hit_chance)
        if not target:
            print("The shoot has missed its target!")
            print("No damage has been made")
            time.sleep(3)

        elif target is True:
            print("The shoot has hit its target!")
            self.range_defend(hit_chance)
            self.fight.field.calculate_state(self.target)

        else:
            print("The shoot has hit the WRONG target! It has hit:")
            target.print_basic()
            target.print_position()
            self.target = target
            time.sleep(3)
            self.range_defend(math.sqrt(1 - hit_chance))
            self.fight.field.calculate_state(self.target)

        self.initiator.use_ammo()
        if self.initiator.is_using_a_crossbow():
            stamina = Characters.RangedAttack[3] * self.shooting_time / 10
        else:
            stamina = Characters.RangedAttack[3] * self.shooting_time
        self.end_update([self.initiator, self.target], stamina, Characters.RangedAttack[2] * self.shooting_time)
        return True

    def range_defend(self, hit_chance):
        # Calculate att coef
        att_coef = self.initiator.power_distance_ratio(self.target) \
                   * self.initiator.power_hit_chance_ratio(hit_chance) \
                   * self.get_attack_coef(self.initiator)
        print("ranged_att_coef:", att_coef)

        # Range defense result
        attack_power = self.initiator.ranged_power * att_coef
        defense_level = self.target.ranged_defense * self.get_attack_coef(self.target)
        attack_result = attack_power - defense_level
        print("attack_power:", attack_power)
        print("attack_result:", attack_result)

        # Attack result --> Either block or be fully hit
        if attack_result <= RangedAttackChar.attack_effect[0]:
            self.target.all_shields_absorbed_damage(attack_power)
            print("The attack has been fully blocked / avoided by the defender")
            time.sleep(5)
        else:
            accuracy_ratio = 0.5 + hit_chance  # Between 0,5 and 1,5, similar to melee handiness_ratio
            armor_coef = self.target.get_armor_coef(accuracy_ratio)
            resis_dim_rate = self.initiator.resis_dim_rate * self.ammo_used.resis_dim_rate
            pen_rate = self.initiator.pen_rate * self.ammo_used.pen_rate
            self.target.damages_received(self.initiator, attack_result, accuracy_ratio, armor_coef, resis_dim_rate,
                                         pen_rate)

    def shoot_hit_chance(self):
        # Distance = -a*(x-1) + b --> distance min = 1.0, distance max = 0.0
        h_dist = max(0, (self.initiator.calculate_point_distance(self.target.abscissa,
                                                                 self.target.ordinate) - 1) / self.initiator.has_range() * -1 + 1)

        h_obs = self.fight.field.calculate_ranged_obstacle_ratio(self.initiator, self.target)

        h_action = self.get_ranged_action_ratio()

        return self.initiator.ranged_accuracy_ratio * h_dist * h_obs * h_action

    def get_ranged_action_ratio(self):
        nb_of_attacks = 0
        for attack_timeline, attack in self.target.previous_attacks:
            if self.timeline < attack_timeline + global_variables.defense_time / self.target.speed_ratio:
                nb_of_attacks += 1

        if nb_of_attacks > 0:
            coef = math.pow(RangedAttackChar.melee_fight_handicap, nb_of_attacks)
        else:
            coef = 1

        if isinstance(self.target.last_action, MoveChar):
            coef *= RangedAttackChar.move_char_handicap

        return coef

    def can_ranged_attack(self):
        if self.initiator.has_ammo() is False:
            print("No ammo for a ranged attack")
            return False

        if self.initiator.has_reloaded() is False:
            print("Ranged weapons are not reloaded")
            return False

        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        for char in team.characters_list:
            if self.fight.field.is_target_reachable(self.initiator, char):
                return True
        return False

import copy as copy
import math as math
import random as random
import time as time
from sources.character.Characters import Characters, NoneCharacter
from sources.action.Actions import Actions


#############################################################
################### RANGED ATTACK CHAR CLASS ################
#############################################################
class RangedAttackChar:
    'Class to ranged attack a character'
    
    attack_effect = [25, 50]  # [Blocked", "Hit", "Hit & stopped"]
    variance = 0.25  # Gauss variance

    def __init__(self, fight, character):
        Actions.__init__(self, fight)
        self.attacker = character
        self.defender = NoneCharacter
        self.ammo_used = self.attacker.get_current_ammo()
        self.shooting_time = 1
        self.is_a_success = self.start()

    def start(self):  # Choose ranged target and shoot mode
        Actions.start(self)
        if self.attacker.check_stamina(Characters.RangedAttack[3]) is False:
            print("You do not have enough stamina (",
                self.attacker.body.get_current_stamina(), ") for a ranged attack")
            return False
        elif self.attacker.is_using_a_ranged_weapon() is False:
            print("You are not using a ranged weapon")
            return False
        elif self.can_ranged_attack() is False:
            print("No enemy can be reached by a ranged attack")
            time.sleep(2)
            return False
        
        if self.fight.belong_to_team(self.attacker) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1
        
        print("--------- ATTACKER -----------")
        self.attacker.print_attack_state()
        print("")

        print("--------- TARGETS -----------")
        print("Choose one of the following enemies:")
        enemy_list = []
        hit_chance_list = []
        for char in team.characters_list:
            self.defender = char
            if self.fight.field.is_target_reachable(self.attacker, self.defender):
                enemy_list.append(self.defender)
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
            self.defender = enemy_list_bis.pop(hit_number)
            print("----- HIT CHANCE:", round(hit_chance_list_bis.pop(hit_number),2))
            self.defender.print_state()
        
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
                    self.defender = enemy_list[i]
                    hit_chance = hit_chance_list[i]
                    self.shooting_time *= self.shoot_speed(hit_chance)
                    self.attacker.spend_time(Characters.RangedAttack[2] * self.shooting_time)
                    return self.result()
                
            print("ID:", read, "is not available")
    
    def shoot_speed(self, hit_chance):
        # Harder is the target to hit, longer it takes to aim and shoot (between 0.66 to 2)
        return 0.66 + 1.34 * (1 - hit_chance)

    def result(self):
        print("")
        print("*********************************************************************")
        self.attacker.print_basic()
        print("is trying to ranged shoot (", end=' ')
        self.defender.print_basic()
        print(")")
        hit_chance = self.shoot_hit_chance()
        print("Current hit chance:", round(hit_chance,2))
        print("*********************************************************************")
        print("")
        time.sleep(5)
        
        if self.attacker.is_using_a_crossbow():
            self.attacker.spend_stamina(Characters.RangedAttack[3] * self.shooting_time / 10)
        else:
            self.attacker.spend_ranged_attack_stamina(Characters.RangedAttack[3] * self.shooting_time)
        self.attacker.calculate_characteristic()

        target = self.fight.field.shoot_has_hit_another_target(self.attacker, self.defender, hit_chance)
        if not target:
            print("The shoot has missed its target!")
            print("No damage has been made")
            time.sleep(3)
        
        elif target is True:
            print("The shoot has hit its target!")
            self.range_defend(hit_chance, self.attack_type)
            self.fight.field.calculate_state(self.defender)
        
        else:
            print("The shoot has hit the WRONG target! It has hit:")
            target.print_basic()
            target.print_position()
            self.defender = target
            time.sleep(3)
            self.range_defend(math.sqrt(1 - hit_chance))
            self.fight.field.calculate_state(self.defender)
        
        self.attacker.use_ammo()  # Contains a attacker.calculate_characteristic()
        return True

    def range_defend(self, hit_chance):
        # Calculate att coef
        att_coef = self.attacker.power_distance_ratio(self.defender) * \
            self.attacker.power_hit_chance_ratio(hit_chance)
        print("ranged_att_coef:", att_coef)
        
        # Range defense result
        attack_power = random.gauss(1.0, RangedAttackChar.variance) * att_coef * \
            self.attacker.ranged_power
        defense_level = random.gauss(1.0, RangedAttackChar.variance) * \
            self.defender.ranged_defense
        attack_result = attack_power - defense_level
        print("attack_power:", attack_power)
        print("attack_result:", attack_result)
        
        # Attack result --> Either block or be fully hit
        if attack_result <= RangedAttackChar.attack_effect[0]:
            self.defender.all_shields_absorbed_damage(attack_power)
            print("The attack has been fully blocked / avoided by the defender")
            time.sleep(5)
        else:
            self.defender.ranged_attack_received(self.attacker, attack_power, hit_chance, self.ammo_used)

    def shoot_hit_chance(self):
        # Distance = -a*(x-1) + b --> distance min = 1.0, distance max = 0.0
        h_dist = max(0, (self.attacker.calculate_point_distance(self.defender.abscissa,
            self.defender.ordinate) - 1) / self.attacker.has_range() * -1 + 1)
        
        h_obs = self.fight.field.calculate_ranged_obstacle_ratio(self.attacker, self.defender)
        
        return min(1, self.attacker.ranged_accuracy_ratio
            * (1 - self.defender.chances_to_be_ranged_missed(self.fight.current_timeline)) \
            * h_dist * h_obs)
        
    def can_ranged_attack(self):
        if self.attacker.has_ammo() is False:
            print("No ammo for a ranged attack")
            return False
        
        if self.attacker.has_reloaded() is False:
            print("Ranged weapons are not reloaded")
            return False
        
        if self.fight.belong_to_team(self.attacker) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1
        
        for char in team.characters_list:
            if self.fight.field.is_target_reachable(self.attacker, char):
                return True
        return False

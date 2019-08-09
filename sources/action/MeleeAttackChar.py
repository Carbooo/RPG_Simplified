import math as math
import random as random
import time as time
from sources.character.Characters import Characters
from sources.action.Actions import Actions


#############################################################
################### MELEE ATTACK CHAR CLASS #################
#############################################################
class MeleeAttackChar:
    """Class to melee attack a character"""

    attack_effect = [0, 25, 50, 75]  # ["Blocked" < "Delay" < "Hit" < "Strong hit" < "Huge hit"]
    medium = 1.0  # Gauss expected value
    variance = 0.25  # Gauss variance

    def __init__(self, fight, character, target):
        Actions.__init__(self, fight)
        self.attacker = character
        self.defender = target
        self.actual_defense = "None"  # Can be "Dodge", "Defense" or "No defense"
        self.is_a_success = self.start()

    def start(self):
        Actions.start(self)
        if not self.attacker.check_stamina(Characters.MeleeAttack[3]):
            print("You do not have enough stamina (", self.attacker.body.get_current_stamina(), ") for a melee attack")
            return False
        elif not self.choose_target():
            return False

        return self.result()

    def choose_target(self):
        if not self.can_melee_attack():
            print("No enemy can be reached by a melee attack")
            time.sleep(3)
            return False

        if self.fight.belong_to_team(self.attacker) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        print("--------- self.attacker -----------")
        self.attacker.print_attack_state()
        print("")

        print("--------- TARGETS -----------")
        print("Choose one of the following enemies:")
        enemy_list = []
        for char in team.characters_list:
            self.defender = char
            if self.attacker.can_melee_attack(self.defender):
                print("----------------------------")
                self.defender.print_state()
                enemy_list.append(self.defender)

        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if self.fight.cancel_action(read):
                    return False
            except:
                print("The input is not an ID")
                continue

            for char in enemy_list:
                self.defender = char
                if self.defender.get_id() == read:
                    return True

            print("ID:", read, "is not available")

        return True

    def result(self):
        # Result of the fight
        attack_result = self.melee_defense_result()
        print("attack_result:", attack_result)
        self.melee_attack_type(attack_result)

        self.attacker.spend_time(Characters.MeleeAttack[2])
        self.attacker.spend_melee_attack_stamina(Characters.MeleeAttack[3])

        if self.actual_defense == "Dodge":
            self.defender.spend_dodge_stamina(3.0 / 4.0)
            self.defender.spend_defense_stamina( 1.0 / 4.0)
        elif self.actual_defense == "Defense":
            self.defender.spend_dodge_stamina(1.0 / 4.0)
            self.defender.spend_defense_stamina(3.0 / 4.0)

        # State result
        self.fight.field.calculate_state(self.defender)
        self.fight.field.calculate_state(self.attacker)
        return True

    def melee_defense_result(self):
        # Choose between dodge and def
        dodge_result = self.attacker.melee_handiness - self.defender.dodging
        defense_result = Characters.get_melee_attack(self.attacker.melee_handiness, self.attacker.melee_power) \
                        - self.defender.melee_defense
        if not self.defender.check_stamina(Characters.MeleeAttack[3]):
            print("Defender does not have enough stamina (", self.defender.body.get_current_stamina(), ") to defend")
            self.actual_defense = "No defense"
        elif defense_result < dodge_result:
            self.actual_defense = "Dodge"
        else:
            self.actual_defense = "Defense"

        # Calculate attack and defend values
        attack_accuracy = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) * math.pow(
                                        self.attacker.melee_handiness * math.pow(self.attacker.melee_range, 1.0 / 3), 
                                        0.75)
        attack_power = Characters.get_melee_attack(attack_accuracy,
                                                   random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance)
                                                   * self.attacker.melee_power)

        dodge_level = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) * self.defender.dodging
        defense_level = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) * self.defender.melee_defense

        dodge_result = attack_accuracy - dodge_level
        defense_result = attack_power - defense_level

        # Calculate final result
        if self.actual_defense == "Dodge":
            attack_result = dodge_result + defense_result / 3
            self.defender.all_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
            self.attacker.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 9)
        elif self.actual_defense == "Defense":
            attack_result = defense_result + dodge_result / 3
            self.defender.all_weapons_absorbed_damage(min(attack_power, defense_level))
            self.attacker.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
        else:
            attack_result = attack_power
            self.attacker.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)

        return attack_result

    def melee_attack_type(self, attack_value):
        # Member hit ratio & attack_coef
        ratio = (attack_value / MeleeAttackChar.attack_effect[2] - 1) * self.attacker.accuracy_ratio()

        if attack_value < MeleeAttackChar.attack_effect[0]:
            # Only block for very low damages
            self.block()
            time.sleep(3)
        elif attack_value < MeleeAttackChar.attack_effect[1]:
            # Block or delay for low damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
            else:
                self.block()
            time.sleep(3)
        elif attack_value < MeleeAttackChar.attack_effect[2]:
            # Hit or delay for medium damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
                time.sleep(3)
            else:
                print("The attack is a normal hit")
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value, ratio, member)
        elif attack_value < MeleeAttackChar.attack_effect[3]:
            # Hit or hit + delay for high damages
            r = random.random()
            if r < 0.5:
                print("The attack will hit and slightly delay the player!")
                time.sleep(2)
                self.delay(attack_value / 2)
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value * 3 / 4, ratio, member)
            else:
                print("The attack is a strong hit!")
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value * 4 / 3, ratio, member)
        else:
            # Hit, hit + delay, big hit or double hit
            r = random.random()
            if r < 0.5:
                print("The attack will hit AND delay the player!")
                time.sleep(2)
                self.delay(attack_value * 2 / 3)
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value, ratio, member)
            else:
                print("The attack is a HUGE HIT!")
                time.sleep(2)
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value * 3 / 2, ratio, member)

    def block(self):
        self.defender.print_basic()
        print("-- has BLOCKED the attack of --", end=' ')
        self.attacker.print_basic()
        time.sleep(2)

    def delay(self, attack_value):
        attack_value /= MeleeAttackChar.attack_effect[3] / 2
        self.defender.spend_time(attack_value)
        self.attacker.print_basic()
        print("-- has DELAYED --", end=' ')
        self.defender.print_basic()
        print("-- of", round(attack_value, 2), "TURN(S) --")
        time.sleep(2)

    def can_melee_attack(self):
        if self.fight.belong_to_team(self.attacker) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        for char in team.characters_list:
            if self.attacker.can_melee_attack(char):
                return True
        return False

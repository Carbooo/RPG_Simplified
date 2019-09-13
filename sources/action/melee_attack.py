import math as math
import random as random
import time as time
import sources.miscellaneous.configuration as cfg
from sources.character.character import Character
from sources.action.actions import Actions, ActiveActions


#############################################################
################### MELEE ATTACK CHAR CLASS #################
#############################################################
class MeleeAttack(ActiveActions):
    """Class to melee attack a character"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Melee attacking"
        self.target = None
        self.actual_defense = "None"  # Can be "Dodge", "Defense" or "No defense"
        self.is_a_success = self.start()

    def start(self):
        if not self.initiator.check_stamina(cfg.actions["melee_attack"]["stamina"]):
            print("You do not have enough stamina (", self.initiator.body.get_current_stamina(), ") for a melee attack")
            return False
        elif not self.choose_target():
            return False

        return True
        
    def choose_target(self):
        if not self.can_melee_attack():
            print("No enemy can be reached by a melee attack")
            time.sleep(3)
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
        for char in team.characters_list:
            self.target = char
            if self.initiator.can_melee_attack(self.target):
                print("----------------------------")
                print("----- FIGHTING AVAILABILITY: ",
                    self.target.get_fighting_availability(self.timeline),
                    " -----")
                self.target.print_defense_state()
                enemy_list.append(self.target)

        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False
            except:
                print("The input is not an ID")
                continue

            for char in enemy_list:
                self.target = char
                if self.target.get_id() == read:
                    return True

            print("ID:", read, "is not available")

        self.end_update([],
                        cfg.actions["melee_attack"]["stamina"],
                        cfg.actions["melee_attack"]["duration"])
        return True

    def execute(self):
        if not self.initiator.can_melee_attack(self.target):
            print("")
            print("*********************************************************************")
            print("The target (", end=' ')
            self.target.print_basic()
            print(") is no longer reachable by a melee attack")
            print("The attack of (", end=' ')
            self.initiator.print_basic()
            print(") has been cancelled !")
            print("*********************************************************************")
            print("")
            time.sleep(5)
            return False
            
        self.fight.stop_action(self.target, self.initiator.timeline)
        self.initiator.last_action = None  # To avoid looping on this action
        
        attack_result = self.melee_defense_result()
        self.melee_attack_type(attack_result)
        
        # Update availability after computed the result
        self.target.previous_attacks.append((self.initiator.timeline, self))
        self.initiator.previous_attacks.append((self.initiator.timeline, self))
        
        abscissa = self.target.abscissa
        ordinate = self.target.ordinate
        if self.actual_defense == "Dodge" and \
           self.fight.field.random_move(self.target, cfg.random_defenser_move_probability * 2):
                print("The fight made the defenser move from their position!")
                time.sleep(2)
                if random.random() < cfg.random_attacker_move_probability:
                    self.fight.field.move_character(self.initiator, abscissa, ordinate)
                    print("And the attacker took the initial position of the defender!")
                    time.sleep(2)
                
        elif self.actual_defense == "Defense" and \
             self.fight.field.random_move(self.target, cfg.random_defenser_move_probability):
                print("The fight made the defenser move from their position!")
                time.sleep(2)
                if random.random() < cfg.random_attacker_move_probability:
                    self.fight.field.move_character(self.initiator, abscissa, ordinate)
                    print("And the attacker took the initial position of the defender!")
                    time.sleep(2)
                
        return True

    def melee_defense_result(self):
        # Choose between dodge and def
        dodge_result = self.initiator.melee_handiness - self.target.dodging
        defense_result = Character.get_melee_attack(self.initiator.melee_handiness, self.initiator.melee_power) \
                         - self.target.melee_defense
        if not self.target.check_stamina(cfg.actions["melee_attack"]["stamina"]):
            print("Defender does not have enough stamina (", self.target.body.get_current_stamina(), ") to defend")
            self.actual_defense = "No defense"
        elif defense_result < dodge_result:
            self.actual_defense = "Dodge"
        else:
            self.actual_defense = "Defense"

        # Calculate attack and defend values
        attack_accuracy = math.pow(self.initiator.melee_handiness * math.pow(self.initiator.melee_range, 1.0 / 3), 0.75) \
                        * self.get_attack_coef(self.initiator)
        attack_power = Character.get_melee_attack(attack_accuracy, self.initiator.melee_power) \
                       * self.get_attack_coef(self.initiator)
                     
        dodge_level = self.target.dodging * self.get_attack_coef(self.target)
        defense_level = self.target.melee_defense * self.get_attack_coef(self.target)
                      
        dodge_result = attack_accuracy - dodge_level
        defense_result = attack_power - defense_level

        # Calculate final result
        if self.actual_defense == "Dodge":
            attack_result = dodge_result + defense_result / 3
            self.target.equipments.all_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
            self.initiator.equipments.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 9)
        elif self.actual_defense == "Defense":
            attack_result = defense_result + dodge_result / 3
            self.target.equipments.all_weapons_absorbed_damage(min(attack_power, defense_level))
            self.initiator.equipments.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
        else:
            attack_result = attack_power
            self.initiator.equipments.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)

        return attack_result

    def melee_attack_type(self, attack_value):
        if attack_value < cfg.melee_attack_stage[0]:
            # Only block for very low damages
            self.block()
            time.sleep(3)
        elif attack_value < cfg.melee_attack_stage[1]:
            # Block or delay for low damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
            else:
                self.block()
            time.sleep(3)
        elif attack_value < cfg.melee_attack_stage[2]:
            # Hit or delay for medium damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
                time.sleep(3)
            else:
                print("The attack is a normal hit")
                self.melee_attack_received(attack_value)
        elif attack_value < cfg.melee_attack_stage[3]:
            # Big hit or hit + delay for high damages
            r = random.random()
            if r < 0.5:
                print("The attack will hit and slightly delay the player!")
                time.sleep(2)
                self.delay(attack_value / 2)
                self.melee_attack_received(attack_value * 3 / 4)
            else:
                print("The attack is a strong hit!")
                self.melee_attack_received(attack_value * 4 / 3)
        else:
            # Big hit + delay or huge hit
            r = random.random()
            if r < 0.5:
                print("The attack will hit AND delay the player!")
                time.sleep(2)
                self.delay(attack_value * 2 / 3)
                self.melee_attack_received(attack_value)
            else:
                print("The attack is a HUGE HIT!")
                time.sleep(2)
                self.melee_attack_received(attack_value * 3 / 2)

    def block(self):
        self.target.print_basic()
        print("-- has BLOCKED the attack of --", end=' ')
        self.initiator.print_basic()
        time.sleep(2)

    def delay(self, attack_value):
        attack_value /= cfg.melee_attack_stage[3] / 2
        self.target.spend_time(attack_value)
        self.initiator.print_basic()
        print("-- has DELAYED --", end=' ')
        self.target.print_basic()
        print("-- of", round(attack_value, 2), "TURN(S) --")
        time.sleep(2)
    
    def melee_attack_received(self, attack_value):
        armor_coef = self.target.get_armor_coef(self.initiator.melee_handiness_ratio)
        self.target.damages_received(
            self.initiator, 
            attack_value, 
            self.initiator.melee_handiness_ratio, 
            armor_coef, 
            self.initiator.resis_dim_rate, 
            self.initiator.pen_rate
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

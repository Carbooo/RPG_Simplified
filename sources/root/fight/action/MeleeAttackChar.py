import math as math
import random as random
import time as time
from sources.root.character.Characters import Characters, NoneCharacter
from sources.root.fight.action.Actions import Actions


#############################################################
################### MELEE ATTACK CHAR CLASS #################
#############################################################
class MeleeAttackChar:
    """Class to melee attack a character"""
    
    #[Description, command, melee power coef, melee handiness coef, risk coef, stamina coef, time coef]
    NormalBlow = {
        'description': "Normal blow",
        'command': "NOR",
        'power': 1.0,
        'handiness': 1.0,
        'risk': 1.0,
        'stamina': 1.0,
        'time': 1.0
    }

    NormalRisk = {
        'description': "Medium risks with a normal attack",
        'command': "MED", 
        'attack': 1.0, 
        'risk': 1.0, 
        'stamina': 1.0, 
        'post_description': "Medium risk attack"
    }

    Defense = {
        'description': "Defend with all your means",
        'command': "DFE", 
        'stamina': 1.0, 
        'defense': 1.0, 
        'post_description': "Fully defending"
    }

    LowInvolvement = {
        'description': "Not defending",
        'command': "BAR",
        'defense': 0.0,
        'stamina': 0.0,
        'post_description': "Not defending for various reasons"
    }
    HighInvolvement = {
        'description': "Fully defend, but spend all your time in this fight",
        'command': "FUL",
        'defense': 1.0,
        'stamina': 1.0,
        'post_description': "High defense involvement"
    }

    actual_defense = ["Full dodge", "Dodge", "Defense"]
    attack_effect = [0, 25, 50, 75] #["Blocked" < "Delay" < "Hit" < "Strong hit" < "Huge hit"]
    time_ratio = 0.85 #Ratio when the hit will occur
    medium = 1.0 #Gauss expected value
    variance = 0.25 #Gauss variance


    def __init__(self, fight, character, target):
        Actions.__init__(self, fight)
        self.attacker = character
        self.attack_type = NormalBlow
        self.attack_risk = NormalRisk
        self.attack_handicap = 0.0
        self.attack_unconsciousness_period = []
        self.defender = target
        self.defense_type = MeleeAttackChar.Defense
        self.defense_involvement = MeleeAttackChar.HighInvolvement
        self.defense_handicap = 0.0
        self.defense_unconsciousness_period = []
        self.actual_defense = "None"
        self.attack_begin_time = self.fight.current_timeline
        self.attack_end_time = self.fight.current_timeline + Characters.MeleeAttack[2] #Temp attack end time
        self.timeline = self.fight.current_timeline + Characters.MeleeAttack[2] * MeleeAttackChar.time_ratio #Temp timeline
        self.is_a_success = self.start()
        
        
    def start(self):
        Actions.start(self)
        if not self.attacker.check_stamina(Characters.MeleeAttack[3]):
            print("You do not have enough stamina (", \
                self.attacker.body.get_current_stamina(), ") for a melee attack")
            return False
        elif not self.choose_target():
            return False

        self.attacker.last_direction = self.attacker.char_to_point_angle( \
            self.defender.abscissa, self.defender.ordinate)
        self.defense_handicap += 1 - self.defender.get_readiness()
                        
        time_spent = Characters.MeleeAttack[2] * self.attack_type['time'] * random.gauss(1, MeleeAttackChar.variance)
        self.attack_end_time = self.fight.current_timeline + time_spent
        self.timeline = self.fight.current_timeline + time_spent * MeleeAttackChar.time_ratio
        if self.attacker.is_waiting() or self.attacker.timeline < self.attack_end_time: #Waiting may occur during a counter attack
            self.attacker.timeline = self.attack_end_time
        
        self.choose_defense_type()
        
        self.attacker.action_in_progress = self
        self.attacker.current_melee_attacks.append(self)
        self.defender.current_melee_attacks.append(self)
        self.fight.scheduler.append(self)
        
        return True
    
    
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
                print("Planned fighting ratio:", round(self.get_planned_fighting_ratio(self.defender),2))
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


    def choose_defense_type(self):
        print("")
        print("--------- self.attacker -----------")
        self.attacker.print_attack_state()
        print("--------- self.defender -----------")
        self.defender.print_defense_state()
        print("Planned fighting ratio:", round(self.get_planned_fighting_ratio(self.defender),2))
        print("")
        
        #Is KO / unconscious and cannot defend
        if self.defender.unconsciousness >= self.timeline - self.attack_begin_time:
            print("Character (", end=' ')
            self.defender.print_basic()
            print(") is unconscious and cannot defend")
            print("The result of the attack will be displayed in a few time")
            time.sleep(3)
            self.defense_involvement = MeleeAttackChar.LowInvolvement


    def check_stamina_defense_requirement(self, def_type):
        if not self.defender.check_stamina(def_type['stamina']):
            print("Character (")
            self.defender.print_basic()
            print(") does not have enough stamina (", \
                self.defender.body.get_current_stamina(), \
                ") to choose this defense (", def_type['post_description'], ")")
            time.sleep(3)
            return False
        return True    
        
        
    def set_defend_action(self):
        if not (self.defender.is_waiting() or self.defender.is_melee_fighting()):
            print("")
            print("Do you want to start defending now or finish your action first? (current action:", \
                  self.defender.current_action[4], ")")
            while 1:
                read = input('--> Yes, defending now (Y) / No, finish current action first (N): ')
                if read == "Y":
                    #Save defense mode
                    self.fight.stop_action(self.defender)
                    self.defender.current_action = Characters.Defending
                    
                    #Defense angle
                    self.defender.last_direction = self.defender.char_to_point_angle( \
                        self.attacker.abscissa, self.attacker.ordinate)
                    break
                elif read == "N":
                    break
                else:
                    print("Answer:", read, "is not recognized")
        else:
            self.defender.current_action = Characters.Defending
        
        if self.defender.is_waiting() or self.defender.timeline < self.attack_end_time:
            self.defender.timeline = self.attack_end_time
            
    
    def result(self):
        Actions.result(self)
        
        print("")
        print("*******************************************************************************************************************")
        print("Timeline: ", self.timeline)
        self.attacker.print_basic()
        print("is trying to melee attack (", end=' ')
        self.defender.print_basic()
        print(")")
        print("--- Attack ratio:", round(self.get_fighting_ratio(self.attacker),2))
        print("--- Defense ratio:", round(self.get_fighting_ratio(self.defender),2))
        print("*******************************************************************************************************************")
        print("")
        time.sleep(5)
        
        #Action is spent even if the target is no longer available
        self.attacker.action_in_progress = False
        
        if not self.attacker.can_melee_attack(self.defender):
            print("The target (", end=' ')
            self.defender.print_basic()
            print(") is no longer reachable by a melee attack")
            print("Previous attack is cancelled!")
            time.sleep(3)
            return False
        
        #Result of the fight
        if not self.defender.is_melee_fighting():
            self.fight.stop_action(self.defender)
        self.melee_defend()
                
        #Stamina spent
        self.attacker.spend_melee_attack_stamina(Characters.MeleeAttack[3] * \
            self.get_fighting_ratio(self.attacker) * \
            self.attack_type['stamina'] * self.attack_risk['stamina'])
        
        coef = self.get_fighting_ratio(self.defender) * self.defense_type['stamina'] * self.defense_involvement['stamina']
        if self.actual_defense == MeleeAttackChar.actual_defense[0]: #Full dodge
            self.defender.spend_dodge_stamina(coef)
        elif self.actual_defense == MeleeAttackChar.actual_defense[1]: #Dodge
            self.defender.spend_dodge_stamina(coef * 3.0 / 4.0)
            self.defender.spend_defense_stamina(coef * 1.0 / 4.0)
        else: #Defense
            self.defender.spend_dodge_stamina(coef * 1.0 / 4.0)
            self.defender.spend_defense_stamina(coef * 3.0 / 4.0)
        
        #State result
        self.fight.field.calculate_state(self.defender)
        self.fight.field.calculate_state(self.attacker)
        return True
        
        
    def melee_defend(self):
        attack_result = self.melee_defense_result()
        print("attack_result:", attack_result)
        self.melee_attack_type(attack_result)
                        
    
    def melee_defense_result(self):
        #Choose between dodge and def
        attacker_melee_power = self.attacker.melee_power * self.attack_risk['attack'] * self.attack_type['power']
        attacker_melee_handiness = self.attacker.melee_handiness * self.attack_risk['attack'] * self.attack_type['handiness']
        defender_dodging = self.defender.dodging * self.defense_type['defense'] * self.defense_involvement['defense']
        defender_melee_defense = self.defender.melee_defense * self.defense_type['defense'] * self.defense_involvement['defense']
        
        dodge_result = attacker_melee_handiness - defender_dodging
        defense_result = Characters.get_melee_attack(attacker_melee_handiness, attacker_melee_power) - defender_melee_defense
        if defense_result < dodge_result:
            defending = True
        else:
            defending = False
        
        #Calculate attack and defend values
        att_coef = self.get_fighting_ratio(self.attacker)
        attack_accuracy = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) * att_coef *\
            math.pow(attacker_melee_handiness * math.pow(self.attacker.melee_range, 1.0/3), 0.75)
        attack_power = Characters.get_melee_attack(attack_accuracy, \
            random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) \
            * attacker_melee_power * att_coef)

        def_coef = self.get_fighting_ratio(self.defender)
        dodge_level = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) \
            * defender_dodging * def_coef
        defense_level = random.gauss(MeleeAttackChar.medium, MeleeAttackChar.variance) \
            * defender_melee_defense * def_coef
        
        dodge_result = attack_accuracy - dodge_level
        defense_result = attack_power - defense_level
        
        #Calculate final result
        if self.defense_type == MeleeAttackChar.Dodge:
            self.actual_defense = MeleeAttackChar.actual_defense[0] #Only Dodge
            attack_result = dodge_result + attack_power/3 #No defense in this mode
        elif not defending:
            self.actual_defense = MeleeAttackChar.actual_defense[1] #Mostly dodge
            attack_result = dodge_result + defense_result/3
            self.defender.all_weapons_absorbed_damage(min(attack_power, defense_level))
            self.attacker.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
        else:
            self.actual_defense = MeleeAttackChar.actual_defense[2] #Mostly defend
            attack_result = defense_result + dodge_result/3
            self.defender.all_weapons_absorbed_damage(min(attack_power, defense_level))
            self.attacker.all_melee_weapons_absorbed_damage(min(attack_power, defense_level) / 3)
            
        return attack_result


    def melee_attack_type(self, attack_value):
        #Member hit ratio & attack_coef
        ratio = (attack_value / MeleeAttackChar.attack_effect[2] - 1) \
            * self.attacker.accuracy_ratio()
        
        if attack_value < MeleeAttackChar.attack_effect[0]:
            #Only block for very low damages
            self.block()
            time.sleep(3)
        elif attack_value < MeleeAttackChar.attack_effect[1]:
            #Block or delay for low damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
            else:
                self.block()
            time.sleep(3)
        elif attack_value < MeleeAttackChar.attack_effect[2]:
            #Hit or delay for medium damages
            r = random.random()
            if r < 0.5:
                self.delay(attack_value)
                time.sleep(3)
            else:
                print("The attack is a normal hit")
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value, ratio, member)
        elif attack_value < MeleeAttackChar.attack_effect[3]:
            #Hit or hit + delay for high damages
            r = random.random()
            if r < 0.5:
                print("The attack will hit and slightly delay the player!")
                time.sleep(2)
                self.delay(random.gauss(1, Characters.variance) * attack_value / 2)
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, random.gauss(1, Characters.variance) \
                    * attack_value * 3 / 4, ratio, member)
            else:
                print("The attack is a strong hit!")
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, attack_value * 4 / 3, ratio, member)
        else:
            #Hit, hit + delay, big hit or double hit
            r = random.random()
            if r < 0.5:
                print("The attack will hit AND delay the player!")
                time.sleep(2)
                self.delay(random.gauss(1, Characters.variance) * attack_value * 2 / 3)
                member = self.defender.body.melee_choose_member(ratio)
                self.defender.melee_attack_received(self.attacker, random.gauss(1, Characters.variance) \
                    * attack_value, ratio, member)
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
        attack_value /= MeleeAttackChar.attack_effect[3]
        self.defender.spend_time(attack_value, "suffer")
        self.attacker.print_basic()
        print("-- has DELAYED --", end=' ')
        self.defender.print_basic()
        print("-- of", round(attack_value,2), "TURN(S) --")
        time.sleep(2)
        
        
    def get_real_melee_period(self, character, begin_time, end_time):
        if character == self.attacker:
            unconscious_list = self.attack_unconsciousness_period
        else:
            unconscious_list = self.defense_unconsciousness_period
        
        time_spent = end_time - begin_time
        for period in unconscious_list:
            if period[0] >= end_time:
                continue
            elif period[1] <= begin_time:
                continue
            elif period[0] <= begin_time:
                if period[1] <= end_time:
                    time_spent -= period[1] - begin_time
                else:
                    time_spent -= end_time - begin_time
            else:
                if period[1] <= end_time:
                    time_spent -= period[1] - period[0]
                else:
                    time_spent -= end_time - period[0]
        
        return max(0, time_spent)
    
    
    def get_involvement(self, character):
        if character == self.defender:
            involvment = self.defense_type['defense'] * self.defense_involvement['defense']
        else:
            involvment = self.attack_risk['risk'] * self.attack_type['risk']
        return involvment
                
        
    def get_fighting_ratio(self, character):
        attack_count = 0
        for att in character.current_melee_attacks:
            if att == self:
                #The current attack does not count in availability
                pass
            
            elif att.attack_end_time <= self.attack_begin_time:
                #Do not count old attacks
                pass
            
            elif att.attack_end_time <= self.timeline:
                #Attack end before the current attack occurs
                if att.attack_begin_time <= self.attack_begin_time:
                    #Attack started before the current attack
                    attack_count += att.get_involvement(character) * self.get_real_melee_period(character, self.attack_begin_time, att.attack_end_time)
                else:
                    #Attack started after the current attack
                    attack_count += att.get_involvement(character) * self.get_real_melee_period(character, att.attack_begin_time, att.attack_end_time)
            
            else:
                #Attack occurs after the current attack
                if att.attack_begin_time <= self.attack_begin_time:
                    #Attack started before the current attack
                    attack_count += att.get_involvement(character) * self.get_real_melee_period(character, self.attack_begin_time, self.timeline)
                else:
                    #Attack started after the current attack
                    attack_count += att.get_involvement(character) * self.get_real_melee_period(character, att.attack_begin_time, self.timeline)
        
        return 1.0 / (1.0 + attack_count / (self.timeline - self.attack_begin_time))
        
     
    def get_planned_fighting_ratio(self, character):
        return max(0, self.defender.get_readiness() * self.get_fighting_ratio(character) - character.unconsciousness)


    def can_melee_attack(self):
        if self.fight.belong_to_team(self.attacker) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1
        
        for char in team.characters_list:
            if self.attacker.can_melee_attack(char):
                return True
        return False
    

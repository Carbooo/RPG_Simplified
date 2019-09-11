import math as math
import time as time
import random as random
from sources.action.actions import Actions, ActiveActions
import sources.miscellaneous.configuration as cfg


#############################################################
######################### SPELL CLASS #######################
#############################################################
class Spells(ActiveActions):
    """Super class for all spells"""

    def __init__(self, fight, initiator, type, spell_code):
        super().__init__(fight, initiator)
        self.name = "Generic spell action"
        self.surname = "Generic spell name"
        self.target = None
        self.type = type
        self.spell_code = spell_code
        self.magical_coef = 0
        self.spell_stamina = 0
        self.spell_time = 0
        self.spell_energy = 0
        self.spell_hands = 0
        self.spell_power = {}

######################### BASE FUNCTIONS #######################
    def start(self):
        pass  # Only for inheritance

    def execute(self):
        self.initiator.last_action = None

    def end(self, is_canceled):
        pass  # Only for inheritance

    def set_magical_coef(self):
        self.magical_coef = random.gauss(1, cfg.high_variance) \
                            * self.initiator.feelings[self.type].use_energy(self.spell_energy)

    def get_stamina_with_coef(self):
        return self.spell_stamina / math.pow(self.magical_coef, 1.0 / 4.0)

    def get_time_with_coef(self):
        return self.spell_time / math.pow(self.magical_coef, 1.0 / 4.0)

    def is_able_to_cast(self):
        if not self.initiator.feelings[self.type].check_energy(self.spell_energy):
            print("You don't have enough energy (", self.spell_energy, ") to cast this spell")
            return False

        if not self.initiator.check_stamina(self.spell_stamina):
            print("You don't have enough stamina (", self.spell_stamina, ") to cast this spell")
            return False

        if self.initiator.equipments.free_hands < self.spell_hands:
            print("You don't have enough free hands (", self.spell_hands, ") to cast this spell")
            return False

        return True

######################### CHOOSE FUNCTIONS #######################
    @staticmethod
    def choose_spell():
        print("You have decided to cast a spell")
        print("")
        print("Which type of spell?")
        for spell_type in cfg.spells:
            print("-", spell_type["description"], "(" + spell_type["code"] + ")")

        while 1:
            read = input('--> Spell type (0 for cancel) : ')
            if Actions.cancel_action(read):
                return False

            for spell_type in cfg.spells:
                if read == spell_type["code"]:
                    print("You chose to cast a " + spell_type["description"])
                    print("")
                    print("Which spell do you want to cast?")

                    for spell in spell_type["list"]:
                        print("- ", spell["description"] + " (" + spell["code"] + ")")

                    while 1:
                        read = input('--> Spell (0 for cancel) : ')
                        if Actions.cancel_action(read):
                            return False

                        for spell in spell_type["list"]:
                            if read == spell["code"]:
                                return spell_type["code"], spell["code"]

                        print("Spell:", read, "is not recognized")

            print("Spell type:", read, "is not recognized")

    def choose_pos_target(self):
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            team = self.fight.team2
        else:
            team = self.fight.team1

        while 1:
            try:
                print("Where do you want to throw your spell?")
                read = int(input('--> Abscissa (-1 = Cancel): '))
                if read == -1:
                    Actions.cancel_action(0)
                    return False
                else:
                    abscissa = read

                read = int(input('--> Ordinate (-1 = Cancel): '))
                if read == -1:
                    Actions.cancel_action(0)
                    return False
                else:
                    ordinate = read

            except:
                print("The input is not an integer")

            if not self.fight.field.is_pos_magically_reachable(self.initiator, abscissa, ordinate):
                print("Target is not magically reachable")
                continue

            target = {
                "abscissa": abscissa,
                "ordinate": ordinate
            }
            return target

    def choose_target_from_list(self, char_list):
        print("---------- CASTER -----------")
        self.initiator.print_attack_state()
        print("")
        print("--------- TARGETS -----------")
        print("Choose one of the available targets:")
        for char in char_list:
            char.print_defense_state()

        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False

                for char in char_list:
                    if char.get_id() == read:
                        return char

                print("ID:", read, "is not available")

            except:
                print("The input is not an ID")

    def choose_target(self, include_enemies, include_allied, include_deads):
        team_list = []
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            if include_enemies:
                team_list.extend(self.fight.team2.characters_list)
            if include_allied:
                team_list.extend(self.fight.team1.characters_list)
        else:
            if include_enemies:
                team_list.extend(self.fight.team1.characters_list)
            if include_allied:
                team_list.extend(self.fight.team2.characters_list)

        char_list = []
        for char in team_list:
            if self.fight.field.is_target_magically_reachable(self.initiator, char) and \
                    (include_deads or char.body.is_alive()):
                char_list.append(char)

        self.target = self.choose_target_from_list(char_list)
        if not self.target:
            return False
        else:
            return True

    def rechoose_target_if_necessary(self, include_enemies, include_allied, include_deads):
        if not self.fight.field.is_target_magically_reachable(self.initiator, self.target):
            if include_deads or not self.target.body.is_alive():
                print("Your initial target is no longer reachable!")
                print("Please choose a new one or cancel the attack.")
                self.target = self.choose_target(include_enemies, include_allied, include_deads)
                if not self.target:
                    print("Spell cancelled, the magic and stamina spent is lost")
                    return False
        return True

######################### EXECUTING FUNCTIONS #######################
    def get_all_spread_targets(self, spread_distance, target_abs, target_ord):
        max_distance = spread_distance + 1
        round_distance = int(math.ceil(spread_distance))
        char_list = []
        for x in range(- round_distance, round_distance + 1):
            for y in range(- round_distance, round_distance + 1):
                abscissa = target_abs + x
                ordinate = target_ord + y
                char = self.fight.field.get_character_from_pos(abscissa, ordinate)
                if char:
                    distance_ratio = (max_distance - char.calculate_point_distance(target_abs, target_ord)) \
                                     / max_distance
                    if distance_ratio > 0.1:  # Min distance ratio to be touched by a spell
                        char_list.append((char, distance_ratio))

        # Put the initiator in last, so the self damages made are not influencing the damages made to others
        initiator_found = False
        for char, distance in char_list:
            if char == self.initiator:
                initiator_found = (char, distance)
        if initiator_found:
            char_list.remove(initiator_found)
            char_list.append(initiator_found)

        return char_list

    def magical_attack_received(self, attack_value, is_localized, can_use_shield, resis_dim_rate, pen_rate):
        if self.target != self.initiator:
            self.fight.stop_action(self.target, self.initiator.timeline)

        if can_use_shield:
            attack_value -= self.target.magic_defense_with_shields * self.get_attack_coef(self.target)
            self.target.equipments.all_shields_absorbed_damage(attack_value)
        else:
            attack_value -= self.target.magic_defense * self.get_attack_coef(self.target)

        if attack_value <= 0:
            self.target.print_basic()
            print("-- has BLOCKED the attack of --", end=' ')
            self.initiator.print_basic()
            print("")
            time.sleep(4)
        else:
            if is_localized:
                accuracy_ratio = self.fight.field.get_magical_accuracy(self.initiator, self.target)
                armor_coef = self.target.get_armor_coef(accuracy_ratio)
                attack_value = self.target.damages_received(self.initiator, attack_value, accuracy_ratio, armor_coef,
                                                           resis_dim_rate, pen_rate)
            else:
                # Non localized attack cannot avoid armor (use cover ratio instead) or do critical hit
                attack_value = self.target.damages_received(self.initiator, attack_value, 0,
                                                           self.target.equipments.get_armor_cover_ratio(),
                                                           resis_dim_rate, pen_rate)

        self.target.previous_attacks.append((self.initiator.timeline, self))
        return max(0.0, attack_value)

######################### ACTIVE SPELLS FUNCTIONS #######################
    def add_active_spell(self):
        self.target.active_spells.append(self)

    def end_active_spell(self):
        self.target.active_spells.remove(self)

    def add_lasting_spell(self, surname, duration, is_target_a_user=True):
        self.surname = surname
        self.timeline = self.timeline + duration
        self.fight.scheduler.append(self)
        if is_target_a_user:
            self.add_active_spell()
    
    def end_lasting_spell(self, is_target_a_user=True):
        self.fight.scheduler.remove(self)
        if is_target_a_user:
            self.end_active_spell()
        
    def identical_active_spell(self):
        for spell in self.target.active_spells:
            if spell.type == self.type and spell.spell_code == self.spell_code:
                return spell
        return False

    def remove_identical_active_spell(self):
        spell = self.identical_active_spell()
        if spell:
            spell.end(is_canceled=True)

######################### PRINTING FUNCTIONS #######################
    def print_spell(self, txt, state, self_spell):
        print("")
        print("*********************************************************************")
        if state == "executing":
            print("************************ SPELL BEING CAST ***************************")
        elif state == "ending":
            print("*********************** ACTIVE SPELL ENDING *************************")
        elif state == "choosing":
            print("********************** CHOOSING TARGET SPELL ************************")
        print("*********************************************************************")
        self.initiator.print_basic()
        print(txt, end=' ')
        if not self_spell:
            self.target.print_basic()
        print("")
        print("*********************************************************************")
        print("")
        time.sleep(3)

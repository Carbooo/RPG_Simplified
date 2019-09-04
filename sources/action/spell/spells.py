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
        self.spell_power = {}

    def execute(self):
        pass  # Only for inheritance

    def end(self):
        pass  # Only for inheritance

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

    def set_magical_coef(self):
        self.magical_coef = random.gauss(1, cfg.high_variance) \
                            * self.initiator.feelings[self.type].use_energy(self.spell_energy)

    def get_stamina_with_coef(self):
        return self.spell_stamina / math.pow(self.magical_coef, 1.0 / 4.0)

    def get_time_with_coef(self):
        return self.spell_time / math.pow(self.magical_coef, 1.0 / 4.0)

    def is_able_to_cast(self, free_hands_required=0):
        if not self.initiator.feelings[self.type].check_energy(self.spell_energy):
            print("You don't have enough energy (", self.spell_energy, ") to cast this spell")
            return False

        if not self.initiator.check_stamina(self.spell_stamina):
            print("You don't have enough stamina (", self.spell_stamina, ") to cast this spell")
            return False

        if self.initiator.equipments.free_hands < free_hands_required:
            print("You don't have enough free hands (", free_hands_required, ") to cast this spell")
            return False

        return True

    def get_all_spread_targets(self, spread_distance):
        max_distance = spread_distance + 1
        round_distance = int(math.ceil(spread_distance))
        char_list = []
        for x in range(- round_distance, round_distance + 1):
            for y in range(- round_distance, round_distance + 1):
                abscissa = self.target.abscissa + x
                ordinate = self.target.ordinate + y
                char = self.fight.field.get_character_from_pos(abscissa, ordinate)
                if char:
                    distance_ratio = (max_distance - char.calculate_point_distance(abscissa, ordinate)) / max_distance
                    if distance_ratio > 0:
                        char_list.append((char, distance_ratio))

        if self.initiator in char_list:
            # Put the initiator in last, so the self damages made are not influencing the damages made to others
            char_list.remove(self.initiator)
            char_list.append(self.initiator)

        return char_list

    def magical_attack_received(self, target, attack_value, accuracy_ratio, is_localized, can_use_shield, 
                                resis_dim_rate, pen_rate):
        if target != self.initiator:
            self.fight.stop_action(target, self.initiator.timeline)

        if can_use_shield:
            attack_value -= target.magic_defense_with_shields * self.get_attack_coef(target)
            target.equipments.all_shields_absorbed_damage(attack_value)
        else:
            attack_value -= target.magic_defense * self.get_attack_coef(target)

        if attack_value <= 0:
            target.print_basic()
            print("-- has BLOCKED the attack of --", end=' ')
            self.initiator.print_basic()
            time.sleep(4)
        else:
            if is_localized:
                armor_coef = target.get_armor_coef(accuracy_ratio)
                attack_value = target.damages_received(self.initiator, attack_value, accuracy_ratio, armor_coef, 
                                                       resis_dim_rate, pen_rate)
            else:
                # Non localized attack cannot avoid armor (use cover ratio instead) or do critical hit
                attack_value = target.damages_received(self.initiator, attack_value, 0,
                                                       target.equipments.get_armor_cover_ratio(),
                                                       resis_dim_rate, pen_rate)

        target.previous_attacks.append((self.initiator.timeline, self))
        return max(0.0, attack_value)
        
    def choose_enemy_target(self):
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
            if self.fight.field.is_target_magically_reachable(self.initiator, char):
                enemy_list.append(char)
                char.print_defense_state()

        while 1:
            try:
                print("")
                read = int(input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False

                for enemy in enemy_list:
                    if enemy.get_id() == read:
                        return enemy

                print("ID:", read, "is not available")

            except:
                print("The input is not an ID")

    def add_active_spell(self, char, duration, surname):
        self.surname = surname
        self.timeline = self.initiator.timeline + duration
        self.fight.scheduler.append(self)
        char.active_spells.append(self)

    def end_active_spell(self, char):
        self.fight.scheduler.remove(self)
        char.active_spells.remove(self)
        self.end()

    def identical_active_spell(self, char):
        for spell in char.active_spells:
            if spell.type == self.type and spell.spell_code == self.spell_code:
                return spell
        return False

    def remove_identical_active_spell(self, char):
        spell = self.identical_active_spell(char)
        if spell:
            spell.end_active_spell(char)

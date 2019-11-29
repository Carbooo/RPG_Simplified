import math as math
import random as random
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func


#############################################################
######################### SPELL CLASS #######################
#############################################################
class Spells(ActiveActions):
    """Super class for all spells"""

    def __init__(self, fight, initiator, spell_code):
        super().__init__(fight, initiator)
        self.name = "Generic spell action"
        self.surname = "Generic spell name"
        self.type = "Spell"
        self.stage = "Initialization"
        self.target = None
        self.feeling_type = None
        self.spell_code = spell_code
        self.magical_coef = 0
        self.spell_stamina = 0
        self.spell_time = 0
        self.spell_energy = 0
        self.spell_hands = 0
        self.spell_knowledge = 0
        self.spell_power = {}

######################### BASE FUNCTIONS #######################
    def start(self):
        if not super().start():
            return False
        self.stage = "Charging"
        self.initiator.charged_spell = self
        return True

    def cast(self):
        self.stage = "Casting"
        self.start_timeline = self.initiator.timeline

    def execute(self):
        self.stage = "Executing"
        self.initiator.last_action = None  # To avoid looping on the spell

    def end(self, is_canceled=False):
        self.stage = "Ending"

    def set_magical_coef(self):
        self.magical_coef = random.gauss(cfg.mean, cfg.high_variance) \
                            * self.initiator.feelings[self.feeling_type].use_energy(self.spell_energy)

    def get_stamina_with_coef(self):
        return self.spell_stamina / math.sqrt(self.magical_coef)

    def get_time_with_coef(self):
        return self.spell_time / self.magical_coef

    def is_able_to_cast(self):
        if not self.initiator.feelings[self.feeling_type].check_energy(self.spell_energy):
            func.optional_print("You don't have enough energy (", self.spell_energy, ") to cast this spell")
            return False

        if not self.initiator.check_stamina(self.spell_stamina):
            func.optional_print("You don't have enough stamina (", self.spell_stamina, ") to cast this spell")
            return False

        if self.initiator.equipments.free_hands < self.spell_hands:
            func.optional_print("You don't have enough free hands (", self.spell_hands, ") to cast this spell")
            return False

        if self.initiator.feelings[self.feeling_type].knowledge < self.spell_knowledge:
            func.optional_print("You don't have the required knowledge (", self.spell_knowledge, ") to cast this spell")
            return False

        return True

######################### CHOOSE FUNCTIONS #######################
    @staticmethod
    def choose_spell(character):
        if character.charged_spell:
            func.optional_print("You already have a charged spell!")
            return False

        func.optional_print("You have decided to cast a spell")
        func.optional_print("")
        func.optional_print("Which type of spell?")
        for spell_type in cfg.spells:
            func.optional_print("-", spell_type["description"], "(" + spell_type["code"] + ")")

        while 1:
            read = func.optional_input('--> Spell type (0 for cancel) : ')
            if Actions.cancel_action(read):
                return False

            for spell_type in cfg.spells:
                if read == spell_type["code"]:
                    func.optional_print("You chose to cast a " + spell_type["description"])
                    func.optional_print("")
                    func.optional_print("Which spell do you want to cast?")

                    for spell in spell_type["list"]:
                        func.optional_print("- ", spell["description"] + " (" + spell["code"] + ")")

                    while 1:
                        read = func.optional_input('--> Spell (0 for cancel) : ')
                        if Actions.cancel_action(read):
                            return False

                        for spell in spell_type["list"]:
                            if read == spell["code"]:
                                return spell_type["code"], spell["code"]

                        func.optional_print("Spell:", read, "is not recognized")

            func.optional_print("Spell type:", read, "is not recognized")

    def choose_pos_target(self, is_obstacle_free=False):
        while 1:
            try:
                func.optional_print("Where do you want to throw your spell?")
                read = int(func.optional_input('--> Abscissa (-1 = Cancel): '))
                if read == -1:
                    Actions.cancel_action(0)
                    return False
                else:
                    abscissa = read

                read = int(func.optional_input('--> Ordinate (-1 = Cancel): '))
                if read == -1:
                    Actions.cancel_action(0)
                    return False
                else:
                    ordinate = read

            except:
                func.optional_print("The input is not an integer")

            if is_obstacle_free:
                if not self.initiator.is_distance_magically_reachable(abscissa, ordinate):
                    func.optional_print("Target is not magically reachable")
                    continue
            else:
                if not self.fight.field.is_pos_magically_reachable(self.initiator, abscissa, ordinate):
                    func.optional_print("Target is not magically reachable")
                    continue

            self.target = {
                "abscissa": abscissa,
                "ordinate": ordinate
            }
            return True

    def choose_target(self, include_enemies, include_allied, include_deads):
        team_list = []
        if self.fight.belong_to_team(self.initiator) == self.fight.team1:
            if include_enemies:
                enemy_team = self.fight.team2.characters_list
                team_list.extend(self.fight.team2.characters_list)
            if include_allied:
                team_list.extend(self.fight.team1.characters_list)
        else:
            if include_enemies:
                enemy_team = self.fight.team1.characters_list
                team_list.extend(self.fight.team1.characters_list)
            if include_allied:
                team_list.extend(self.fight.team2.characters_list)

        char_list = []
        for char in team_list:
            if self.fight.field.is_target_magically_reachable(self.initiator, char) and \
                    (include_deads or char.body.is_alive()):
                char_list.append(char)

        func.optional_print("---------- CASTER -----------")
        self.initiator.print_attack_state()
        func.optional_print("")
        func.optional_print("--------- TARGETS -----------")
        func.optional_print("Choose one of the available targets:")
        for char in char_list:
            char.print_defense_state()

        while 1:
            try:
                func.optional_print("")
                read = int(func.optional_input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False

                for char in char_list:
                    if char.get_id() == read:
                        self.target = char
                        if include_enemies and char in enemy_team:
                            char.add_previous_attack(self.start_timeline, self.initiator.timeline, self)
                        return True

                func.optional_print("ID:", read, "is not available")

            except:
                func.optional_print("The input is not an ID")

    def is_target_still_reachable(self, include_deads, is_obstacle_free):
        reachable = True
        if isinstance(self.target, dict):  # Target is a position, not a character
            if is_obstacle_free:
                if not self.initiator.is_distance_magically_reachable(self.target["abscissa"], self.target["ordinate"]):
                    reachable = False
            else:
                if not self.fight.field.is_pos_magically_reachable(self.initiator, self.target["abscissa"], self.target["ordinate"]):
                    reachable = False
        else:
            if not self.fight.field.is_target_magically_reachable(self.initiator, self.target):
                reachable = False
            elif not include_deads and not self.target.body.is_alive():
                reachable = False

        if not reachable:
            func.optional_print("Your initial target is no longer reachable!")
            func.optional_print("Spell cancelled, the magic and stamina spent is lost")
            return False
        return True

######################### EXECUTING FUNCTIONS #######################
    def get_all_spread_targets(self, spread_distance, target_abs, target_ord):
        max_distance = spread_distance + 1.0
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
                    if distance_ratio >= cfg.min_dist_ratio:
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

    def magical_attack_received(self, attack_value, is_localized, can_use_shield, life_rate,
                                ignoring_armor_rate, pen_rate, resis_dim_rate):
        func.optional_print("Initiator fighting availability:", round(
            self.initiator.get_fighting_availability(self.start_timeline, self.initiator.timeline, self), 2), level=3)
        func.optional_print("Target fighting availability:", round(
            self.target.get_fighting_availability(self.start_timeline, self.initiator.timeline, self), 2), level=3)

        attack_value *= self.initiator.get_fighting_availability(self.start_timeline, self.initiator.timeline, self)
        func.optional_print("attack_value1", attack_value, level=3, debug=True)
        if can_use_shield:
            attack_value -= self.target.magic_defense_with_shields \
                            * self.get_attack_coef(self.target, self.initiator.timeline)
            self.target.equipments.all_shields_absorbed_damage(attack_value, resis_dim_rate)
        else:
            attack_value -= self.target.magic_defense \
                            * self.get_attack_coef(self.target, self.initiator.timeline)
        func.optional_print("attack_value2", attack_value, level=3, debug=True)

        if self.target != self.initiator:
            self.stop_action(self.target, self.initiator.timeline)

        if attack_value <= 0:
            self.target.print_basic()
            func.optional_print("-- has BLOCKED the attack of --", skip_line=True, level=3)
            self.initiator.print_basic()
            func.optional_print("")
            func.optional_sleep(4)
        else:
            if is_localized:
                accuracy_ratio = self.fight.field.get_magical_accuracy(self.initiator, self.target)
                armor_coef = self.target.get_armor_coef(accuracy_ratio)
                if armor_coef == 0:
                    attack_value /= cfg.no_armor_power_ratio
                attack_value = self.target.damages_received(self.initiator, attack_value, armor_coef, 1.0,
                                                            life_rate, ignoring_armor_rate, pen_rate,
                                                            resis_dim_rate)
            else:
                # Non localized attack cannot avoid armor (use cover ratio instead) or do critical hit
                attack_value = self.target.damages_received(self.initiator, attack_value,
                                                            self.target.equipments.get_armor_cover_ratio(), 1.0,
                                                            life_rate, ignoring_armor_rate, pen_rate,
                                                            resis_dim_rate)

        return max(0.0, attack_value)

######################### ACTIVE SPELLS FUNCTIONS #######################
    def add_active_spell(self):
        self.target.active_spells.append(self)

    def end_active_spell(self):
        self.target.active_spells.remove(self)

    def add_lasting_spell(self, surname, duration, is_target_a_user=True):
        self.surname = surname
        self.timeline = self.initiator.timeline + duration
        self.fight.scheduler.append(self)
        if is_target_a_user:
            self.add_active_spell()
    
    def end_lasting_spell(self, is_target_a_user=True):
        self.fight.scheduler.remove(self)
        if is_target_a_user:
            self.end_active_spell()
        
    def identical_active_spell(self):
        for spell in self.target.active_spells:
            if spell.type == self.feeling_type and spell.spell_code == self.spell_code:
                return spell
        return False

    def remove_identical_active_spell(self):
        spell = self.identical_active_spell()
        if spell:
            spell.end(is_canceled=True)

######################### PRINTING FUNCTIONS #######################
    def print_spell(self, txt, state, self_spell):
        func.optional_print("")
        func.optional_print("*********************************************************************")
        if state == "executing":
            func.optional_print("************************* SPELL OCCURRING ***************************")
        elif state == "affecting":
            func.optional_print("********************** ACTIVE SPELL AFFECTING ***********************")
        elif state == "ending":
            func.optional_print("*********************** ACTIVE SPELL ENDING *************************")
        elif state == "choosing":
            func.optional_print("********************** CHOOSING TARGET SPELL ************************")
        func.optional_print("*********************************************************************")
        self.initiator.print_basic()
        func.optional_print(txt, skip_line=True)
        if isinstance(self.target, dict):  # Is not a character, but a field position
            func.optional_print(self.target)
        elif not self_spell:
            self.target.print_basic()
        func.optional_print("")
        func.optional_print("*********************************************************************")
        func.optional_print("")
        func.optional_sleep(2)

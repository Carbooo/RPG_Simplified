import copy as copy
import math as math
import random as random
import time as time
from sources.root.character.BodyMembers import BodyMembers
from sources.root.character.Equipments import Equipments, Shields, \
    Bows, MeleeWeapons, Crossbows


#############################################################
###################### BODIES CLASS #########################
#############################################################
class Bodies:
    """Common base class for all body of characters"""
    life_distribution = [20.0, 40.0, 80.0, 80.0, 80.0, 80.0]
    ranged_shoot_type = [["Assured shoot", "AS"], ["Specific shoot", "SS"], ["Rapid shoot", "RS"]]

    # For ranged shoot probability
    member_size = [0.08, 0.4, 0.11, 0.11, 0.15, 0.15]  # Normal ratio for non-specific target
    member_size_high_per_member = [  # High hit ratio for body members
        [0.85, 0.12, 0.013, 0.013, 0.002, 0.002],
        [0.003, 0.98, 0.004, 0.004, 0.0045, 0.0045],
        [0.013, 0.27, 0.7, 0.002, 0.013, 0.002],
        [0.013, 0.27, 0.002, 0.7, 0.013, 0.002],
        [0.002, 0.05, 0.016, 0.002, 0.75, 0.18],
        [0.002, 0.05, 0.002, 0.016, 0.18, 0.75]]
    member_size_low_per_member = [  # Low hit ratio for body members
        [0.5, 0.33, 0.08, 0.08, 0.005, 0.005],
        [0.06, 0.65, 0.06, 0.06, 0.085, 0.085],
        [0.05, 0.45, 0.35, 0.005, 0.14, 0.005],
        [0.05, 0.45, 0.005, 0.35, 0.005, 0.14],
        [0.005, 0.19, 0.05, 0.005, 0.4, 0.35],
        [0.005, 0.19, 0.005, 0.05, 0.35, 0.4]]

    def __init__(self, life, stamina, mana, prefered_hand, force_ratio):
        self.original_stamina = float(stamina)
        self.stamina = float(stamina)
        self.original_mana = float(mana)
        self.mana = float(mana)
        self.force_ratio = force_ratio
        self.load_ratio = 0
        self.state = "OK"
        self.shape = "OK"

        self.head = BodyMembers(self, BodyMembers.types[0], float(life) / 100 * Bodies.life_distribution[0],
                                float(stamina) / 1.5, 5)
        self.chest = BodyMembers(self, BodyMembers.types[1],
                                 float(life) / 100 * Bodies.life_distribution[1],
                                 float(stamina) / 1.5, 15)
        self.left_arm = BodyMembers(self, BodyMembers.types[2],
                                   float(life) / 100 * Bodies.life_distribution[2],
                                   float(stamina) / 1.5, 20)
        self.right_arm = BodyMembers(self, BodyMembers.types[3],
                                    float(life) / 100 * Bodies.life_distribution[3],
                                    float(stamina) / 1.5, 20)
        self.left_leg = BodyMembers(self, BodyMembers.types[4],
                                   float(life) / 100 * Bodies.life_distribution[4],
                                   float(stamina) / 1.5, 10)
        self.right_leg = BodyMembers(self, BodyMembers.types[5],
                                    float(life) / 100 * Bodies.life_distribution[5],
                                    float(stamina) / 1.5, 10)

        self.free_hands = 2
        if prefered_hand == "ambidextrous":
            self.suitable_hand_low_bonus = 1.0  # Advantage when using suitable hand
            self.suitable_hand_high_bonus = 1.0  # Advantage when using suitable hand
            self.main_hand = self.right_arm
            self.second_hand = self.left_arm
        else:
            self.suitable_hand_low_bonus = 1.35  # Advantage when using suitable hand
            self.suitable_hand_high_bonus = 2.0  # Advantage when using suitable hand
            if prefered_hand == "left_handed":
                self.main_hand = self.left_arm
                self.second_hand = self.right_arm
            elif prefered_hand == "right_handed":
                self.main_hand = self.right_arm
                self.second_hand = self.left_arm

        self.body_members = []
        self.body_members.append(self.head)
        self.body_members.append(self.chest)
        self.body_members.append(self.left_arm)
        self.body_members.append(self.right_arm)
        self.body_members.append(self.left_leg)
        self.body_members.append(self.right_leg)

    ########################### EQUIPMENT FUNCTIONS ########################
    def set_armors(self, head_armor, chest_armor, arms_armor, legs_armor):
        # Members armor
        self.head.set_armor(head_armor)
        self.chest.set_armor(chest_armor)
        self.left_arm.set_armor(arms_armor)
        self.right_arm.set_armor(arms_armor)
        self.left_leg.set_armor(legs_armor)
        self.right_leg.set_armor(legs_armor)

        # Diminish load for double members
        self.left_arm.armor.load /= 2
        self.right_arm.armor.load /= 2
        self.left_leg.armor.load /= 2
        self.right_leg.armor.load /= 2

        # List of all body armors
        self.armors = []
        self.armors.append(self.head.armor)
        self.armors.append(self.chest.armor)
        self.armors.append(self.left_arm.armor)
        self.armors.append(self.right_arm.armor)
        self.armors.append(self.left_leg.armor)
        self.armors.append(self.right_leg.armor)

    def armors_load(self):
        load = 0
        for armor in self.armors:
            load += armor.load
        return load

    def armors_bulk(self):
        bulk = 0
        for armor in self.armors:
            bulk += armor.bulk
        return bulk

    def armors_defense(self):
        defense = 0
        for armor in self.armors:
            defense += armor.defense
        return defense / len(self.body_members)

    def armors_resistance(self):
        resistance = 0
        for armor in self.armors:
            resistance += armor.resistance
        return resistance / len(self.body_members)

    def member_resistance(self, member):
        return self.body_members[member].armor.resistance

    def member_cover_ratio(self, member):
        return self.body_members[member].armor.cover_ratio()

    def armor_damage_absorbed(self, damage, member, armor_coef, resistance_dim_rate, penetration_rate):
        armor = self.body_members[member].armor
        result = armor.damage_absorbed(damage, armor_coef, resistance_dim_rate, penetration_rate)

        if not armor.is_none_armor() and result[0] <= 0:
            print("Your armor \\ID:", armor.get_id(), "\\Name:", armor.name, "has been broken!")
            self.body_members[member].remove_armor()

        return result[1]

    def weapon_ratio(self, weapon):
        if weapon.hand == 2:
            if isinstance(weapon, Bows):
                return self.bow_hands_used()[2]
            elif isinstance(weapon, Crossbows):
                return self.crossbow_hands_used()[2]
            elif isinstance(weapon, MeleeWeapons):
                return self.melee_weapon_hands_used()[2]
            else:
                print("(Bodies) Weapon ratio used default ratio, because the weapon (", weapon.name,
                      ") type could not be bound")
                return self.main_hand_global_ratio() * self.second_hand_global_ratio()
        elif self.right_arm.is_using_the_weapon(weapon):
            return self.weapon_ratio_hand(weapon, self.right_arm)
        elif self.left_arm.is_using_the_weapon(weapon):
            return self.weapon_ratio_hand(weapon, self.left_arm)

        else:
            print("(Bodies) Weapon ratio (", weapon.name, ") cannot be bound to an arm")
            return False

    def weapon_ratio_hand(self, weapon, hand):
        if hand == self.main_hand:
            if isinstance(weapon, MeleeWeapons):
                return self.main_hand_global_ratio() * math.pow(self.suitable_hand_high_bonus, 1.0 / 3)
            elif isinstance(weapon, Shields):
                return self.main_hand_global_ratio() / self.suitable_hand_low_bonus
            else:
                print("(Bodies) Weapon ratio hand used default ratio, because the weapon (", weapon.name,
                      ") type could not be bound")
                return self.main_hand_global_ratio()
        else:
            if isinstance(weapon, MeleeWeapons):
                return self.second_hand_global_ratio() / self.suitable_hand_high_bonus
            elif isinstance(weapon, Shields):
                return self.second_hand_global_ratio() * math.pow(self.suitable_hand_low_bonus, 1.0 / 3)
            else:
                print("(Bodies) Weapon ratio hand used default ratio, because the weapon (", weapon.name,
                      ") type could not be bound")
                return self.second_hand_global_ratio()

    def two_hands_used(self, main_hand_r, low_hand_r, general_r):  # Return [main hand, second hand, weapon ratio]
        main_hand_ratio = math.pow(self.main_hand_global_ratio(), 1.0 / main_hand_r) * \
                        math.pow(self.second_hand_global_ratio(), 1.0 / low_hand_r) * math.pow(general_r, 1.0 / 3)
        second_hand_ratio = math.pow(self.second_hand_global_ratio(), 1.0 / main_hand_r) * \
                          math.pow(self.main_hand_global_ratio(), 1.0 / low_hand_r) / general_r
        if main_hand_ratio > second_hand_ratio:
            return [self.main_hand, self.second_hand, main_hand_ratio]
        else:
            return [self.second_hand, self.main_hand, second_hand_ratio]

    def bow_hands_used(self):
        return self.two_hands_used(1.0, self.suitable_hand_high_bonus, self.suitable_hand_high_bonus)

    def crossbow_hands_used(self):
        return self.two_hands_used(self.suitable_hand_low_bonus, self.suitable_hand_high_bonus, self.suitable_hand_low_bonus)

    def melee_weapon_hands_used(self):
        return self.two_hands_used(self.suitable_hand_low_bonus, self.suitable_hand_high_bonus, self.suitable_hand_high_bonus)

    def remove_weapon(self, weapon):
        self.free_hands += weapon.hand
        if self.right_arm.weapon == weapon and self.left_arm.weapon == weapon:
            self.right_arm.remove_weapon()
            self.left_arm.remove_weapon()
            return True
        elif self.right_arm.weapon == weapon:
            self.right_arm.remove_weapon()
            if not self.left_arm.is_not_weapon_equiped():
                self.reset_weapon_hand(self.left_arm)
            return True
        elif self.left_arm.weapon == weapon:
            self.left_arm.remove_weapon()
            if not self.right_arm.is_not_weapon_equiped():
                self.reset_weapon_hand(self.right_arm)
            return True
        else:
            self.free_hands -= weapon.hand
            print("(Bodies) Error, cannot remove the weapon (", weapon.name, ") because it is not equipped")
            return False

    def reset_weapon_hand(self, hand):
        if hand.is_not_weapon_equiped():
            print("(Bodies) Error, cannot reset weapon hand because it is unequipped")
            return False
        else:
            weapon = hand.weapon
            hand.remove_weapon()
            return self.set_weapon(weapon)

    def set_weapon(self, weapon):
        self.free_hands -= weapon.hand

        if self.right_arm.is_not_weapon_equiped() and self.left_arm.is_not_weapon_equiped():
            if weapon.hand == 2:
                if self.right_arm.set_weapon(weapon):
                    return self.left_arm.set_weapon(weapon)

            elif isinstance(weapon, Shields):
                if self.second_hand_global_ratio() * self.suitable_hand_low_bonus >= self.main_hand_global_ratio():
                    return self.left_arm.set_weapon(weapon)
                else:
                    return self.right_arm.set_weapon(weapon)

            elif isinstance(weapon, MeleeWeapons):
                if self.main_hand_global_ratio() * self.suitable_hand_high_bonus >= self.second_hand_global_ratio():
                    return self.right_arm.set_weapon(weapon)
                else:
                    return self.left_arm.set_weapon(weapon)

            else:
                print("(Bodies) Set weapon used default hand, because the weapon (", weapon.name,
                      ") type could not be bound")
                return self.right_arm.set_weapon(weapon)

        elif self.left_arm.is_not_weapon_equiped():
            return self.set_weapons_on_best_hands(weapon, self.right_arm.weapon)

        elif self.right_arm.is_not_weapon_equiped():
            return self.set_weapons_on_best_hands(weapon, self.left_arm.weapon)

        else:
            self.free_hands += weapon.hand
            print("(Bodies) Cannot equip weapons, because there are not enough free hands:", weapon.hand, ">",
                  self.free_hands)
            return False

    def set_weapons_on_best_hands(self, weapon1, weapon2):
        if weapon1.hand + weapon2.hand > 2:
            print("(Bodies) Error, weapons to set require too many hands")
            return False

        ratio1 = self.weapon_ratio_hand(weapon1, self.left_arm) + self.weapon_ratio_hand(weapon2, self.right_arm)
        ratio2 = self.weapon_ratio_hand(weapon1, self.right_arm) + self.weapon_ratio_hand(weapon2, self.left_arm)
        if ratio1 > ratio2:
            self.left_arm.set_weapon(weapon1)
            self.right_arm.set_weapon(weapon2)
        else:
            self.right_arm.set_weapon(weapon1)
            self.left_arm.set_weapon(weapon2)
        return True

    ############################# LIFE FUNCTIONS ##########################
    def get_current_life(self):
        return ( \
                           self.head.life * 100 / Bodies.life_distribution[0] + \
                           self.chest.life * 100 / Bodies.life_distribution[1] + \
                           self.left_arm.life * 100 / Bodies.life_distribution[2] + \
                           self.right_arm.life * 100 / Bodies.life_distribution[3] + \
                           self.left_leg.life * 100 / Bodies.life_distribution[4] + \
                           self.right_leg.life * 100 / Bodies.life_distribution[5]) \
               / len(self.body_members) * self.life_ratio()

    def life_ratio(self):
        return self.head.life_ratio() * self.chest.life_ratio() * \
               self.left_arm.life_ratio() * self.right_arm.life_ratio() * \
               self.left_leg.life_ratio() * self.right_leg.life_ratio()

    def global_life_ratio(self):
        return self.life_ratio_adjustment(self.life_ratio())

    def left_arm_life_ratio(self):
        return self.life_ratio_adjustment(self.left_arm.life_ratio())

    def right_arm_life_ratio(self):
        return self.life_ratio_adjustment(self.right_arm.life_ratio())

    def move_life_ratio(self):
        return self.life_ratio_adjustment( \
            self.left_leg.life_ratio() * self.right_leg.life_ratio() * \
            math.pow(self.chest.life_ratio(), 1.0 / 2) * \
            math.pow(self.left_arm.life_ratio(), 1.0 / 3) * \
            math.pow(self.right_arm.life_ratio(), 1.0 / 3) * \
            math.pow(self.head.life_ratio(), 1.0 / 3))

    def melee_attack_life_ratio(self):
        # Contains no hand life ratio, because it is already in the weapon_ratio function
        return self.life_ratio_adjustment( \
            math.pow(self.left_leg.life_ratio(), 1.0 / 2) * \
            math.pow(self.right_leg.life_ratio(), 1.0 / 2) * \
            math.pow(self.chest.life_ratio(), 1.0 / 3) * \
            math.pow(self.head.life_ratio(), 1.0 / 3))

    def ranged_attack_life_ratio(self):
        # Contains no hand life ratio, because it is already in the weapon_ratio function
        return self.life_ratio_adjustment( \
            math.pow(self.head.life_ratio(), 1.0 / 2) * \
            math.pow(self.chest.life_ratio(), 1.0 / 3) * \
            math.pow(self.left_leg.life_ratio(), 1.0 / 3) * \
            math.pow(self.right_leg.life_ratio(), 1.0 / 3))

    def reload_life_ratio(self):
        return self.life_ratio_adjustment( \
            self.left_arm.life_ratio() * self.right_arm.life_ratio() * \
            math.pow(self.left_leg.life_ratio(), 1.0 / 3) * \
            math.pow(self.right_leg.life_ratio(), 1.0 / 3) * \
            math.pow(self.head.life_ratio(), 1.0 / 4) * \
            math.pow(self.chest.life_ratio(), 1.0 / 4))

    def defense_life_ratio(self):
        # Contains no hand life ratio, because it is already in the weapon_ratio function
        return self.life_ratio_adjustment( \
            math.pow(self.left_leg.life_ratio(), 1.0 / 2) * \
            math.pow(self.right_leg.life_ratio(), 1.0 / 2) * \
            math.pow(self.chest.life_ratio(), 1.0 / 3) * \
            math.pow(self.head.life_ratio(), 1.0 / 3))

    def dodge_life_ratio(self):
        return self.life_ratio_adjustment( \
            self.left_leg.life_ratio() * self.right_leg.life_ratio() * \
            math.pow(self.chest.life_ratio(), 1.0 / 3) * \
            math.pow(self.head.life_ratio(), 1.0 / 3))

    def life_ratio_adjustment(self, coefficient):
        if coefficient <= 0:
            # Keep a track of the real value of the dead
            return 1
        elif coefficient >= 1:
            return 1
        elif coefficient >= 0.5:
            return 1 - math.pow((1 - coefficient) * 1.26, 1.5)
        else:
            return math.pow(coefficient * 1.26, 1.5)

    def life_rest(self, coefficient):
        for member in self.body_members:
            member.life_rest(coefficient)

    def loose_life(self, damage, member):
        cr_life = self.body_members[member].life
        damage_ratio = damage / self.body_members[member].life
        if damage_ratio < 0.1:
            print("The attack has only made a flesh wound")
        elif damage_ratio < 0.2:
            print("The attack has made weak damages")
        elif damage_ratio < 0.4:
            print("The attack has made medium damages")
        elif damage_ratio < 0.7:
            print("The attack has made serious damages")
        elif damage_ratio < 0.9:
            print("The attack has made tremendous damages")
        else:
            print("The attack has made deadly damages!")
        time.sleep(2)

        self.body_members[member].life -= damage
        print("The attack has made", int(round(damage)), "life damages")
        time.sleep(2)

        # Used for spend_time & spend_stamina resulting of the hit
        return self.body_members[member].life / cr_life

    ########################### STAMINA FUNCTIONS ##########################
    def spend_stamina(self, value):
        self.stamina = max(0, self.stamina - float(value) * BodyMembers.turn_stamina / self.load_ratio)

    def spend_move_stamina(self, value):
        self.spend_stamina(value)
        self.left_arm.spend_stamina(float(value) / 4)
        self.right_arm.spend_stamina(float(value) / 4)
        self.left_leg.spend_stamina(value * 1.5)
        self.right_leg.spend_stamina(value * 1.5)

    def spend_melee_attack_stamina(self, value):
        self.spend_stamina(value)
        self.chest.spend_stamina(float(value) / 4)
        self.left_arm.spend_stamina(value * 1.5)
        self.right_arm.spend_stamina(value * 1.5)
        self.left_leg.spend_stamina(float(value) / 4)
        self.right_leg.spend_stamina(float(value) / 4)

    def spend_ranged_attack_stamina(self, value):
        self.spend_stamina(value)
        bow_hands = self.bow_handsUsed()
        bow_hands[0].spend_stamina(value * 2)
        bow_hands[1].spend_stamina(value * 0.5)

    def spend_reload_stamina(self, value):
        self.spend_stamina(value)
        self.chest.spend_stamina(float(value) / 4)
        self.left_arm.spend_stamina(value * 1.5)
        self.right_arm.spend_stamina(value * 1.5)
        self.left_leg.spend_stamina(float(value) / 4)
        self.right_leg.spend_stamina(float(value) / 4)

    def spend_defense_stamina(self, value):
        self.spend_stamina(value)
        self.chest.spend_stamina(float(value) / 3)
        self.left_arm.spend_stamina(float(value) / 1.5)
        self.right_arm.spend_stamina(float(value) / 1.5)
        self.left_leg.spend_stamina(float(value) / 2)
        self.right_leg.spend_stamina(float(value) / 2)

    def spend_dodge_stamina(self, value):
        self.spend_stamina(value)
        self.chest.spend_stamina(float(value) / 2)
        self.left_arm.spend_stamina(float(value) / 4)
        self.right_arm.spend_stamina(float(value) / 4)
        self.left_leg.spend_stamina(value)
        self.right_leg.spend_stamina(value)

    def get_current_stamina(self):
        return self.stamina

    def stamina_ratio(self):
        return float(self.stamina) / self.original_stamina

    def global_stamina_ratio(self):
        return self.stamina_ratio_adjustment(self.stamina_ratio())

    def left_arm_stamina_ratio(self):
        return self.stamina_ratio_adjustment(self.left_arm.stamina_ratio())

    def right_arm_stamina_ratio(self):
        return self.stamina_ratio_adjustment(self.right_arm.stamina_ratio())

    def move_stamina_ratio(self):
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio() * \
                                                    math.pow(self.left_arm.stamina_ratio(), 1.0 / 4.0) * \
                                                    math.pow(self.right_arm.stamina_ratio(), 1.0 / 4.0) * \
                                                    math.pow(self.left_leg.stamina_ratio(), 1.0 / 2.0) * \
                                                    math.pow(self.right_leg.stamina_ratio(), 1.0 / 2.0), \
                                                    1.0 / 3.0))

    def melee_attack_stamina_ratio(self):  # Hands ratio are in weapon ratio
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio() * \
                                                    math.pow(self.left_leg.stamina_ratio(), 1.0 / 4.0) * \
                                                    math.pow(self.right_leg.stamina_ratio(), 1.0 / 4.0), \
                                                    1.0 / 3.0))

    def ranged_attack_stamina_ratio(self):  # Hands ratio are in weapon ratio
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio(), 1.0 / 2.0))

    def reload_stamina_ratio(self):
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio() * \
                                                    math.pow(self.left_arm.stamina_ratio(), 1.0 / 2.0) * \
                                                    math.pow(self.right_arm.stamina_ratio(), 1.0 / 2.0) * \
                                                    math.pow(self.left_leg.stamina_ratio(), 1.0 / 7.0) * \
                                                    math.pow(self.right_leg.stamina_ratio(), 1.0 / 7.0), \
                                                    1.0 / 3.0))

    def defense_stamina_ratio(self):  # Hands ratio are in weapon ratio
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio() * \
                                                    math.pow(self.left_leg.stamina_ratio(), 1.0 / 7.0) * \
                                                    math.pow(self.right_leg.stamina_ratio(), 1.0 / 7.0), \
                                                    1.0 / 3.0))

    def dodge_stamina_ratio(self):
        return self.stamina_ratio_adjustment(math.pow(self.stamina_ratio() * \
                                                    math.pow(self.left_leg.stamina_ratio(), 1.0 / 2.0) * \
                                                    math.pow(self.right_leg.stamina_ratio(), 1.0 / 2.0), \
                                                    1.0 / 2.0))

    def stamina_ratio_adjustment(self, coefficient):
        if self.get_current_life() <= 0:
            # Keep a track of the real value of the dead
            return 1
        elif coefficient >= 1:
            return 1
        else:
            return 1 - math.pow(1 - coefficient, 1.7)

    def stamina_rest(self, coefficient):
        # Full in 20 min of rest
        self.stamina = max(0, min(self.original_stamina, \
                                  self.stamina + self.original_stamina * coefficient / BodyMembers.stamina_resting_coef))

        for member in self.body_members:
            member.stamina_rest(coefficient)

    ############################# MANA FUNCTIONS ##########################
    def mana_ratio(self):
        return float(self.mana) / self.original_mana

    def get_current_mana(self):
        return self.mana

    def mana_ratio_adjustment(self, coefficient):
        if self.get_current_life() <= 0:
            # Keep a track of the real value of the dead
            return 1
        elif coefficient >= 1:
            return 1
        else:
            return 1 - math.pow(1 - coefficient, 1.7)

    def mana_ratio_adjusted(self):
        return self.mana_ratio_adjustment(self.mana_ratio())

    def mana_rest(self, coefficient):
        # Full in 1 hour of rest
        self.mana = max(0, min(self.original_mana, \
                               self.mana + self.original_mana * coefficient / 600))

    ############################# GLOBAL FUNCTIONS ##########################
    def left_arm_global_ratio(self):
        return self.left_arm_life_ratio() * self.left_arm_stamina_ratio()

    def right_arm_global_ratio(self):
        return self.right_arm_life_ratio() * self.right_arm_stamina_ratio()

    def main_hand_global_ratio(self):
        if self.main_hand == self.right_arm:
            return self.right_arm_global_ratio()
        else:
            return self.left_arm_global_ratio()

    def second_hand_global_ratio(self):
        if self.second_hand == self.right_arm:
            return self.right_arm_global_ratio()
        else:
            return self.left_arm_global_ratio()

    def move_global_ratio(self):
        return self.move_life_ratio() * self.move_stamina_ratio()

    def melee_attack_global_ratio(self):
        return self.melee_attack_life_ratio() * self.melee_attack_stamina_ratio()

    def ranged_attack_global_ratio(self):
        return self.ranged_attack_life_ratio() * self.ranged_attack_stamina_ratio()

    def reload_global_ratio(self):
        return self.reload_life_ratio() * self.reload_stamina_ratio()

    def defense_global_ratio(self):
        return self.defense_life_ratio() * self.defense_stamina_ratio()

    def global_ratio(self):
        return self.global_life_ratio() * self.global_stamina_ratio()

    def global_rest(self, coefficient):
        self.life_rest(coefficient)
        self.stamina_rest(coefficient)
        self.mana_rest(coefficient)

    def turn_rest(self, time_spent):
        # The more life you have, the better the resting is
        # If char is injured, loose energy instead of gaining
        # The more stamina you have, the better it is for other energies
        # Loose energy faster than you gain it
        # You recover mana and stamina faster when their rate is lower
        life_r = self.life_ratio() - 0.5
        stamina_r = self.stamina_ratio()

        if life_r > 0:
            final_life_rest = life_r * stamina_r * 2
            final_stamina_rest = life_r * (1 - stamina_r) * 2
            final_mana_rest = life_r * stamina_r * (1 - self.mana_ratio()) * 2

        else:
            final_life_rest = math.pow(life_r, 3) * 2000 * (1.5 - stamina_r)
            final_stamina_rest = math.pow(life_r, 3) * 5
            final_mana_rest = math.pow(life_r, 3) * 5 * (1.5 - stamina_r)

        self.life_rest(final_life_rest * time_spent)
        self.stamina_rest(final_stamina_rest * time_spent)
        self.mana_rest(final_mana_rest * time_spent)

    def get_life_state(self, life_r):
        if life_r > 0.85:
            return "OK"
        elif life_r > 0.65:
            return "Scratch"
        elif life_r > 0.35:
            return "Injured"
        elif life_r > 0.15:
            return "Deeply injured"
        elif life_r > 0:
            return "KO"
        else:
            return "Dead"

    def calculate_states(self):
        # Global life state
        life_r = self.life_ratio()
        self.state = self.get_life_state(life_r)

        # Stamina state
        stamina_r = self.stamina_ratio()
        if life_r <= 0:
            # Keep trace of normal value if dead
            self.shape = "OK"
        elif stamina_r > 0.85:
            self.shape = "OK"
        elif stamina_r > 0.65:
            self.shape = "Breathless"
        elif stamina_r > 0.35:
            self.shape = "Tired"
        elif stamina_r > 0.15:
            self.shape = "Exhausted"
        elif stamina_r > 0:
            self.shape = "Empty"
        else:
            self.shape = "KO"

    ########################## CHOOSE MEMBER FUNCTIONS #####################
    def melee_choose_member(self, coefficient):
        # Coefficient must be an integer between 0 and 5 (6 members)
        # The higher is the coefficient, the better target it will be
        coefficient = int(min(5, max(0, math.floor(
            coefficient * len(self.body_members) * random.random()))))

        members_list = self.list_all_members_resistance()
        ordered_list = self.list_all_members_resistance_ordered(members_list)

        for i in range(len(members_list)):
            if members_list[i][0] == ordered_list[coefficient][0]:
                self.print_member_hit(i)
                return i

    def list_all_members_resistance(self):
        members_list = [ \
            [BodyMembers.types[0], self.head.life + \
             self.head.armor.defense * self.head.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate], \
            [BodyMembers.types[1], self.chest.life + \
             self.chest.armor.defense * self.chest.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate], \
            [BodyMembers.types[2], self.left_arm.life + \
             self.left_arm.armor.defense * self.left_arm.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate], \
            [BodyMembers.types[3], self.right_arm.life + \
             self.right_arm.armor.defense * self.right_arm.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate], \
            [BodyMembers.types[4], self.left_leg.life + \
             self.left_leg.armor.defense * self.left_leg.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate], \
            [BodyMembers.types[5], self.right_leg.life + \
             self.right_leg.armor.defense * self.right_leg.armor.resistance_ratio() \
             / Equipments.armor_def_malus_rate]]

        return members_list

    def list_all_members_resistance_ordered(self, members_list):
        # The weakest member is the latest member of the list
        ordered_list = []
        ordered_list.append(members_list[0])
        for member in members_list[1::]:
            for j in range(len(ordered_list)):
                if member[1] > ordered_list[j][1]:
                    ordered_list.insert(j, member)
                    break
                elif member[1] == ordered_list[j][1] and \
                        random.choice([0, 1]) == 1:
                    # To be fair in case of equal timeline
                    ordered_list.insert(j, member)
                    break
                elif j == len(ordered_list) - 1:
                    ordered_list.append(member)

        return ordered_list

    def ranged_choose_member(self, coefficient, shoot_type):
        # Coefficient = HitRatio
        if shoot_type == Bodies.ranged_shoot_type[1]:
            # Specific shoot, aim the weakest part of the body
            members_list = self.list_all_members_resistance()
            ordered_list = self.list_all_members_resistance_ordered(members_list)
            member = ordered_list[len(ordered_list) - 1][0]
            for i in range(len(BodyMembers.types)):
                if member == BodyMembers.types[i]:
                    coefficient /= self.weakest_member_size_ratio()  # Reestablish old hit ratio
                    member_ratio_list = self.member_size_adjusted(coefficient, i)
                    break
        else:
            # Other shoots, aim the center of the body (i.e. the chest)
            member_ratio_list = self.member_size_adjusted(coefficient, 1)  # 1 for chest

        # Calculate member hit
        ratio = random.random()
        limit = 0
        for i in range(len(member_ratio_list)):
            if ratio < limit + member_ratio_list[i]:
                self.print_member_hit(i)
                return i
            else:
                limit += member_ratio_list[i]

    def member_size_adjusted(self, coefficient, member):
        members_list = copy.copy(Bodies.member_size_high_per_member[member][0::])
        for i in range(len(members_list)):
            members_list[i] += (Bodies.member_size_low_per_member[member][i] - \
                               Bodies.member_size_high_per_member[member][i]) * \
                              (1 - coefficient)
        return members_list

    def weakest_member_size_ratio(self):
        members_list = self.list_all_members_resistance()
        ordered_list = self.list_all_members_resistance_ordered(members_list)
        for i in range(len(members_list)):
            if members_list[i][0] == ordered_list[len(ordered_list) - 1][0]:
                return (1.0 + Bodies.member_size[i] / max(Bodies.member_size)) / 2

    ########################## PRINTING FUNCTIONS #########################
    def print_life(self):
        print(",Life:", int(round(self.get_current_life())), end=' ')

    def print_detailed_life(self):
        print(",Life:", int(round(self.get_current_life())))
        for i in range(len(self.body_members)):
            print("\\", BodyMembers.types[i], "life ratio", "\t:", \
                  round(self.body_members[i].life_ratio(), 2))

    def print_stamina(self):
        print(",Stamina:", int(round(self.get_current_stamina())), end=' ')

    def print_detailed_stamina(self):
        print(",Stamina:", int(round(self.get_current_stamina())))
        for i in range(len(self.body_members)):
            print("\\", BodyMembers.types[i], "stamina ratio", "\t:", \
                  round(self.body_members[i].stamina_ratio(), 2))

    def print_mana(self):
        print(",Mana:", int(round(self.get_current_mana())), end=' ')

    def print_states(self):
        print(",State:", self.state, ",Shape:", self.shape, end=' ')

    def print_basic(self):
        self.print_life()
        self.print_stamina()
        self.print_mana()
        self.print_states()

    def print_detailed_basic(self):
        self.print_detailed_life()
        self.print_detailed_stamina()
        self.print_mana()
        self.print_states()

    def print_armors(self):
        self.head.print_armor()
        self.chest.print_armor()
        self.left_arm.print_armor()
        self.right_arm.print_armor()
        self.left_leg.print_armor()
        self.right_leg.print_armor()

    def print_full_armors(self):
        for i in range(len(self.body_members)):
            print("\\", BodyMembers.types[i], " \t:", end=' ')
            self.body_members[i].print_full_armor()

    def print_obj(self):
        self.print_basic()
        self.print_armors()

    def print_member_hit(self, member):
        print("The attack has hit the", BodyMembers.types[member])
        time.sleep(1)

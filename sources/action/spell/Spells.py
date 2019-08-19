from sources.action.Actions import ActiveActions
import sources.miscellaneous.global_variables as global_variables

#############################################################
######################### SPELL CLASS #######################
#############################################################
class Spells(ActiveActions):
    """Super class for all spells"""

    def __init__(self, fight, initiator, type, spell_code):
        super().__init__(self, fight, initiator)
        self.target = None
        self.type = type
        self.spell_code = spell_code

    def get_all_spread_targets(self, spread_distance):
        max_distance = spread_distance + 1.0
        char_list = []
        for x in range(-1, max_distance):
            for y in range(-1, max_distance):
                abscissa = self.target abscissa + x
                ordinate = self.target.ordinate + y                               
                char = self.fight.field.get_character_from_pos(abscissa, ordinate)
                if char:
                    distance_ratio = (max_distance - char.calculate_point_distance(abscissa, ordinate)) / max_distance
                    if distance_ratio > 0:
                        char_list.append((char, distance_ratio))
        
        return char_list
        
    def magical_attack_received(self, attack_value, accuracy_ratio, is_localized, can_use_shield, resis_dim_rate, pen_rate):
        if can_use_shield:
            attack_value -= self.target.magic_defense_with_shields \
                          * random.gauss(1, global_variables.high_variance) \
                          * self.target.get_fighting_availability(self.initiator.timeline)
            self.target.all_shields_absorbed_damage(attack_value)
        else:
            attack_value -= self.target.magic_defense \
                          * random.gauss(1, global_variables.high_variance)
                          * self.target.get_fighting_availability(self.initiator.timeline)
        
        if attack_value <= 0:
            self.target.print_basic()
            print("-- has BLOCKED the attack of --", end=' ')
            self.initiator.print_basic()
            time.sleep(4)
        else:
            if is_localized:
                armor_coef = self.target.get_armor_coef(accuracy_ratio)
            else:
                armor_coef = self.target.body.member_cover_ratio(1)
            self.target.damages_received(self.initiator, attack_value, accuracy_ratio, armor_coef, resis_dim_rate, pen_rate)
        
        self.target.previous_attacks.append((self.initiator.timeline, self))
    
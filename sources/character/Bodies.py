import math as math
import time as time
from sources.character.Equipments import Equipments, Armors, Weapons, MeleeWeapons, Shields, RangedWeapons, Bows, Ammo


#############################################################
###################### BODIES CLASS #########################
#############################################################
class Bodies:
    """Common base class for all body of characters"""

    life_resting_coef = 14400.0  # Rest coefficient
    stamina_resting_coef = 200.0  # Rest coefficient
    turn_stamina = 1.0  # Stamina reference used

    def __init__(self, life, stamina):
        self.original_life = float(life)
        self.life = float(life)
        self.life_ratio = 0.0
        self.life_ratio_adjusted = 0.0  # Use for global ratio
        self.update_life(0)
        self.original_stamina = float(stamina)
        self.stamina = float(stamina)
        self.stamina_ratio = 0.0
        self.stamina_ratio_adjusted = 0.0
        self.update_stamina(0)
        self.state = "OK"
        self.shape = "OK"

        self.armor = None
        self.weapons_stored = []
        self.weapons_in_use = []
        self.ammo = []
        self.free_hands = 2

    ############################# BODY FUNCTIONS ##########################
    def update_life(self, life):
        self.life = max(0.0, self.life + life)
        self.life_ratio = self.life / 100
        self.life_ratio_adjusted = Bodies.life_ratio_adjustment(self.life_ratio)
    
    @staticmethod
    def life_ratio_adjustment(coefficient):
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
        self.life = max(0.0,
                        min(self.original_life,
                            self.life +
                            self.original_life *
                            self.get_rest_coef(coefficient) /
                            Bodies.life_resting_coef)
                        )
        
    def loose_life(self, damage):
        previous_life = self.life
        damage_ratio = damage / self.life
        self.update_life(- damage)

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
        print("The attack has made", int(round(damage)), "life damages")
        time.sleep(2)

        return self.life / previous_life  # Used for spend_time & stamina resulting of the hit
    
    def update_stamina(self, stamina):
        self.stamina = max(0.0, self.stamina + stamina)
        self.stamina_ratio = self.stamina / 100
        self.stamina_ratio_adjusted = Bodies.stamina_ratio_adjustment(self.stamina_ratio)

    @staticmethod
    def stamina_ratio_adjustment(coefficient):
        if coefficient >= 1:
            return 1
        else:
            return 1 - math.pow(1 - coefficient, 1.7)

    def spend_stamina(self, coefficient, ignore=False):
        if not ignore and not self.check_stamina(coefficient):
            print("Error: Stamina below 0")
        self.update_stamina(coefficient * Bodies.turn_stamina)

    def check_stamina(self, coefficient):
        if self.stamina >= Bodies.turn_stamina * coefficient:
            return True
        return False

    def stamina_rest(self, coefficient):
        self.stamina = max(0.0,
                           min(self.original_stamina,
                               self.stamina +
                               self.original_stamina *
                               self.get_rest_coef(coefficient) /
                               Bodies.stamina_resting_coef)
                           )

    def get_rest_coef(self, coefficient):
        if coefficient > 0:
            return coefficient * math.pow(self.life_ratio * self.stamina_ratio, 1.0 / 3.0)
        else:
            return coefficient * (1 - math.pow(self.life_ratio * self.stamina_ratio, 3))

    def global_rest(self, coefficient):
        self.life_rest(coefficient)
        self.stamina_rest(coefficient)

    def turn_rest(self, time_spent):
        # The more life you have, the better the resting is
        # If char is injured, loose energy instead of gaining
        # The more stamina you have, the better it is for all energies
        # Loose energies faster than you gain it
        # You recover stamina faster when their rate is lower
        life_r = self.life_ratio - 0.5

        if life_r > 0:
            final_life_rest = life_r * self.stamina_ratio * 2
            final_stamina_rest = life_r * (1 - self.stamina_ratio) * 2

        else:
            final_life_rest = math.pow(life_r, 3) * 2000 * (1.5 - self.stamina_ratio)
            final_stamina_rest = math.pow(life_r, 3) * 5

        self.life_rest(final_life_rest * time_spent)
        self.stamina_rest(final_stamina_rest * time_spent)

    def global_ratio(self):
        return self.life_ratio_adjusted * self.stamina_ratio_adjusted

    def calculate_states(self):
        # Life state
        if self.life_ratio > 0.85:
            self.state = "OK"
        elif self.life_ratio > 0.65:
            self.state = "Scratch"
        elif self.life_ratio > 0.35:
            self.state = "Injured"
        elif self.life_ratio > 0.15:
            self.state = "Deeply injured"
        elif self.life_ratio > 0:
            self.state = "KO"
        else:
            self.state = "Dead"

        # Stamina shape
        if self.stamina_ratio > 0.85:
            self.shape = "OK"
        elif self.stamina_ratio > 0.65:
            self.shape = "Breathless"
        elif self.stamina_ratio > 0.35:
            self.shape = "Tired"
        elif self.stamina_ratio > 0.15:
            self.shape = "Exhausted"
        elif self.stamina_ratio > 0:
            self.shape = "Empty"
        else:
            self.shape = "KO"
            
    ############################### EQUIP FUNCTIONS ###############################
    def set_armor(self, armor_name):
        # Find armor
        armor_found = False
        for equip in Equipments.list:
            if isinstance(equip, Armors) and equip.name == armor_name:
                armor_found = equip.copy()
                break

        # Set armor
        if armor_found is False:
            print("(Bodies) Armor (", armor_name, ") has not been found and therefore cannot be set")
            return False
        else:
            self.armor = armor_found
            return True

    def remove_armor(self):
        self.armor = None
        return True

    def set_weapon_in_stored(self, weapon_name):
        # Find weapon
        weapon_found = False
        for equip in Equipments.list:
            if isinstance(equip, Weapons) and equip.name == weapon_name:
                weapon_found = equip.copy()
                break

        # Check prerequisites
        if not weapon_found:
            print("(Bodies) Weapon (", weapon_name, ") has not been found and therefore cannot be set")
            return False

        # Set weapon
        self.weapons_stored.append(weapon_found)
        return True
    
    def set_weapon_in_use(self, weapon):
        if self.free_hands < weapon.hand:
            print("(Bodies) Weapon (", weapon.name, ") cannot be set, because there are not enough free hands")
            return False

        # Set weapon
        self.weapons_stored.remove(weapon)
        self.weapons_in_use.append(weapon)
        self.free_hands -= weapon.hand
        return True

    def remove_weapon(self, weapon, definitive=False):
        if weapon not in self.weapons_in_use:
            print("(Bodies) Error, cannot remove weapon because it is not equiped")
            return False
        else:
            self.weapons_in_use.remove(weapon)
            self.free_hands += weapon.hand
            if not definitive:
                self.weapons_stored.append(weapon)
                if isinstance(weapon, Bows) and weapon.current_ammo:
                    self.ammo.append(weapon.current_ammo)
                    weapon.unload()
            return True
                
    def set_ammo(self, ammo_type, ammo_number):
        # Find ammo
        ammo_found = False
        for equip in Equipments.list:
            if isinstance(equip, Ammo) and equip.name == ammo_type:
                ammo_found = equip.copy()
                break

        if ammo_found:
            for _ in range(ammo_number):
                self.ammo.append(ammo_found.copy())
            return True

        print("(Bodies) Ammo cannot be set because ammo type (", ammo_type, ") has not been found !")
        return False
    
    def set_equipments(self, armor, weapon1, weapon2, weapon3, weapon4,
                       ammo_type1, ammo_number1, ammo_type2, ammo_number2):
        # Set armors
        self.set_armor(armor)

        # Set weapons
        weapon_list = [weapon1, weapon2, weapon3, weapon4]
        for weapon_name in weapon_list:
            if not weapon_name:
                continue
            else:
                self.set_weapon_in_stored(weapon_name)

        # Set ammo
        if ammo_type1:
            self.set_ammo(ammo_type1, ammo_number1)
        if ammo_type2:
            self.set_ammo(ammo_type2, ammo_number2)

    ############################# DAMAGE FUNCTIONS #############################
    def armor_damage_absorbed(self, damage, armor_coef, resistance_dim_rate, penetration_rate):
        result = self.armor.damage_absorbed(damage, armor_coef, resistance_dim_rate, penetration_rate)

        if self.armor and result[0] <= 0:
            print("Your armor \\ID:", self.armor.get_id(), "\\Name:", self.armor.name, "has been broken!")
            self.remove_armor()

        return result[1]

    def all_weapons_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            try:
                defense += weapon.defense
                weapons_list.append(weapon)
            except:
                pass
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_melee_weapons_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, MeleeWeapons):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def all_shields_absorbed_damage(self, damage):
        weapons_list = []
        defense = 0
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                defense += weapon.defense
                weapons_list.append(weapon)
        for weapon in weapons_list:
            self.weapon_absorbed_damage(weapon, damage * weapon.defense / defense)

    def weapon_absorbed_damage(self, weapon, damage):
        if weapon.decrease(damage) == 0:
            print("Your weapon \\ID:", weapon.get_id(), "\\Name:", weapon.name, "has been broken!")
            self.weapons_in_use.remove(weapon)

    ############################# OTHER EQUIP FUNCTIONS ###########################
    def is_using_a_shield(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, Shields):
                return True
        return False

    def is_using_a_ranged_weapon(self):
        for weapon in self.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                return True
        return False

    def get_full_load(self):
        load = 0
        for weapon in self.weapons_stored:
            load += weapon.load
        for weapon in self.weapons_in_use:
            load += weapon.load
        if self.armor:
            load += self.armor.load
        return load
    
    def get_in_use_load(self):
        load = 0
        for weapon in self.weapons_in_use:
            load += weapon.load
        if self.armor:
            load += self.armor.load
        return load

    def get_full_bulk(self):
        bulk = 0
        for weapon in self.weapons_stored:
            bulk += weapon.bulk
        for weapon in self.weapons_in_use:
            bulk += weapon.bulk
        if self.armor:
            bulk += self.armor.bulk
        return bulk

    def get_in_use_bulk(self):
        bulk = 0
        for weapon in self.weapons_in_use:
            bulk += weapon.bulk
        if self.armor:
            bulk += self.armor.bulk
        return bulk
    
    ########################## PRINTING FUNCTIONS #########################
    def print_life(self):
        print("life:", int(round(self.life)), end=' ')

    def print_stamina(self):
        print("stamina:", int(round(self.stamina)), end=' ')

    def print_states(self):
        print(", State:", self.state, ", Shape:", self.shape, end=' ')

    def print_basic(self):
        self.print_life()
        self.print_stamina()
        self.print_states()

    def print_armor(self):
        self.armor.print_armor()

    def print_obj(self):
        self.print_basic()
        self.print_armor()

    def print_armor(self):
        print(", ArmorID:", self.armor.get_id(), ", Armor:", self.armor.name,
              ", Defense:", self.armor.defense, end=' ')

    def print_full_armor(self):
        self.armor.print_obj()

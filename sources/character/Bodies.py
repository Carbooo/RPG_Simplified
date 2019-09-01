import math as math
import time as time


#############################################################
###################### BODIES CLASS #########################
#############################################################
class Bodies:
    """Common base class for all body of characters"""

    life_resting_coef = 14400.0  # Rest coefficient
    stamina_resting_coef = 200.0  # Rest coefficient
    turn_stamina = 1.0  # Stamina reference used

    def __init__(self, char, life, stamina):
        self.character = char
        self.original_life = float(life)
        self.life = float(life)
        self.life_ratio = 0.0
        self.life_ratio_adjusted = 0.0  # Use for global ratio
        self.original_stamina = float(stamina)
        self.stamina = float(stamina)
        self.stamina_ratio = 0.0
        self.stamina_ratio_adjusted = 0.0
        self.state = "OK"
        self.shape = "OK"
        self.update_life(0, initial=True)
        self.update_stamina(0, initial=True)

    ############################# LIFE FUNCTIONS ##########################
    def update_life(self, life, initial=False):
        self.life = min(self.original_life, max(0.0, self.life + life))
        self.life_ratio = self.life / self.original_life
        self.life_ratio_adjusted = Bodies.life_ratio_adjustment(self.life_ratio)
        if not initial:
            self.calculate_states()
    
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
        self.update_life(self.original_life * self.get_rest_coef(coefficient) / Bodies.life_resting_coef)
        
    def loose_life(self, damage):
        previous_life = self.life
        damage_ratio = damage / self.life

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

        self.update_life(- damage)
        return self.life / previous_life  # Used for spend_time & stamina resulting of the hit

    ############################# STAMINA FUNCTIONS ##########################
    def update_stamina(self, stamina, initial=False):
        self.stamina = min(self.original_stamina, max(0.0, self.stamina + stamina))
        self.stamina_ratio = self.stamina / self.original_stamina
        self.stamina_ratio_adjusted = Bodies.stamina_ratio_adjustment(self.stamina_ratio)
        if not initial:
            self.calculate_states()

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
        self.update_stamina(self.original_stamina * self.get_rest_coef(coefficient) / Bodies.stamina_resting_coef)

    ############################# REST FUNCTIONS ##########################
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

    ############################# STATE / SHAPE FUNCTIONS ##########################
    def calculate_states(self):
        # Life state
        old = self.state
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

        if self.state != old:
            print("ID:", str(self.character.get_id()), ", Name:", self.character.name, "state is now:", self.state)
            time.sleep(3)

        # Stamina shape
        old = self.shape
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

        if self.shape != old:
            print("ID:", str(self.character.get_id()), ", Name:", self.character.name, "shape is now:", self.shape)
            time.sleep(3)

        self.character.calculate_characteristic()

    def is_shape_ko(self):
        if self.shape == "KO":
            return True
        return False

    def is_active(self):
        if self.state != "KO" and self.state != "Dead" and self.shape != "KO":
            return True
        return False

    def is_life_active(self):
        if self.state != "KO" and self.state != "Dead":
            return True
        return False

    def is_alive(self):
        if self.state != "Dead":
            return True
        return False

    ########################## PRINTING FUNCTIONS #########################
    def print_life(self):
        print(", Life:", int(round(self.life)), end=' ')

    def print_stamina(self):
        print(", Stamina:", int(round(self.stamina)), end=' ')

    def print_states(self):
        print(", State:", self.state, ", Shape:", self.shape, end=' ')

    def print_obj(self):
        self.print_life()
        self.print_stamina()
        self.print_states()

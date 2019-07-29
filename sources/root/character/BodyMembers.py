import math as math
from sources.root.character.Equipments import Equipments, NoneArmor, NoneWeapon, Armors

#############################################################
################### BODY MEMBERS CLASS ######################
#############################################################
class BodyMembers:
    'Common base class for all members of a body'
    
    types = ["Head", "Chest", "Left arm", "Right arm", "Left leg", "Right leg"]
    armor_types = ["Head", "Chest", "Arms", "Arms", "Legs", "Legs"]
    life_resting_coef = 14400.0 #Rest coefficient
    stamina_resting_coef = 200.0 #Rest coefficient
    turn_stamina = 1.0 #Stamina reference used
    max_bonus = 3.0 #Max load bonus
    
        
    def __init__(self, body, MemberType, life, stamina, load_mean):
        self.body = body
        self.type = MemberType
        self.original_life = float(life)
        self.life = float(life)
        self.original_stamina = float(stamina)
        self.stamina = float(stamina)
        self.load_mean = load_mean
        self.armor = NoneArmor.copy()
        self.weapon = NoneWeapon.copy()
        

########################### EQUIPMENT FUNCTIONS ########################
    def get_load_ratio(self):
        if self.weapon.hand == 2:
            weapon_load = self.weapon.load / 2
        else:
            weapon_load = self.weapon.load
                
        return  min(BodyMembers.max_bonus, self.load_mean / \
            max(1, self.armor.load + weapon_load) * self.body.force_ratio)


    def is_using_the_weapon(self, weapon):
        if self.weapon == weapon:
            return True
        return False
    
        
    def is_not_weapon_equiped(self):
        if self.weapon.get_id() == 0:
            return True
        return False


    def set_weapon(self, weapon):
        self.weapon = weapon
        return True
        
    
    def remove_weapon(self):
        self.weapon = NoneWeapon.copy()
        return True
        

    def set_armor(self, armor):
        #Find armor
        armor_found = False
        for equip in Equipments.list:
            if isinstance(equip, Armors) and equip.name == armor:
                armor_found = equip.copy()
                break
        
        #Translation from body type to armor type
        member = False
        for i in range(len(BodyMembers.types)):
            if BodyMembers.types[i] == self.type:
                member = BodyMembers.armor_types[i]
                break
            
        #Set armor
        if armor_found is False:
            print("(BodyMembers) Armor (", armor, ") has not been found and therefore cannot be set")
            self.armor = NoneArmor.copy()
            return False
        elif member != armor_found.body_member and armor_found.body_member != "None":
            print("(BodyMembers) Error: Armor type (", armor_found.body_member, \
                  ") is different from Body type (", member, ")")
            return False
        else:
            self.armor = armor_found
        
        return True
    
    
    def remove_armor(self):
        self.armor = NoneArmor.copy()
        return True
    
    
############################# LIFE FUNCTIONS ##########################
    def life_ratio(self):
        return max(0, self.life / self.original_life)
    
    
    def life_rest(self, coefficient):
        self.life = max(0, min(self.original_life, self.life + \
            self.original_life * self.get_rest_coef(coefficient) / BodyMembers.life_resting_coef))
        

############################ STAMINA FUNCTIONS ##########################
    def stamina_ratio(self):
        return float(self.stamina) / self.original_stamina
    
    
    def get_current_stamina(self):
        return self.stamina
    
    
    def spend_stamina(self, value):
        self.stamina = max(0, self.stamina - float(value) * BodyMembers.turn_stamina / self.get_load_ratio())
            
    
    def stamina_rest(self, coefficient):
        self.stamina = max(0, min(self.original_stamina, self.stamina + \
            self.original_stamina * self.get_rest_coef(coefficient) / BodyMembers.stamina_resting_coef))
    
    
############################ GLOBAL FUNCTIONS ##########################        
    def get_rest_coef(self, coefficient):
        life_r = self.life_ratio()
        stamina_r = self.stamina_ratio()
        
        if coefficient > 0:
            return coefficient * math.pow(life_r * stamina_r, 1.0/3.0)
        else:
            return coefficient * (1 - math.pow(life_r * stamina_r, 3))
        
    
########################## PRINTING FUNCTIONS #########################
    def print_armor(self):
        print(", ArmorID:", self.armor.get_id(), ", Armor:", self.armor.name, \
            ", Defense:", self.armor.defense, end=' ')
        
        
    def print_full_armor(self):
        self.armor.print_obj()
        

    def print_life(self):
        print(self.type, "life:", int(round(self.life)), end=' ')
        

    def print_stamina(self):
        print(self.type, "stamina:", int(round(self.stamina)), end=' ')


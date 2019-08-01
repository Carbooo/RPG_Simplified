import copy as copy
import math as math
import time as time
from sources.root.character.Characters import Characters
from sources.root.fight.action.Actions import Actions


#############################################################
###################### EQUIP CHAR CLASS #####################
#############################################################
class EquipChar:
    """Class to equip a character"""
    
    def __init__(self, fight, character):
        Actions.__init__(self, fight)
        self.character = character
        self.next_equipment = []
        self.next_unequipment = []
        self.equip_time = 0.0
        self.equip_handicap = 0.0
        self.after_equip_handicap = 0.0
        self.is_a_success = self.start()

    def start(self):
        Actions.start(self)
        if not self.character.check_stamina(self.character.current_action[3]):
            print("You do not have enough stamina (",
                  self.character.body.get_current_stamina(), ") to modify your equipment")
            return False
        
        if self.character.current_action == Characters.UnequipAll:
            if not self.character.weapons_use:
                print("You have already unequipped all your weapons, action cancelled!")
                return False
            elif self.unequip_all_weapons():
                return True
            return False
        
        if self.character.current_action == Characters.UnequipSpec:
            if not self.character.weapons_use:
                print("You have already unequipped all your weapons, action cancelled!")
                return False
            elif self.unequip_spec_weapons():
                return True
            return False
        
        if self.character.current_action == Characters.EquipAll:
            if not self.character.weapons_stored:
                print("You have no weapon to equip, action cancelled!")
                return False
            elif self.character.nb_of_hands_used() >= 2:
                print("You are already fully equipped, action cancelled!")
                print("Weapons in use:", end=' ')
                self.character.print_weapons_use()
                print("Weapons in store:", end=' ')
                self.character.print_weapons_stored()
                return False
            elif self.character.nb_of_hands_stored() > 2:
                print("You do not have enough free hands to equip all your weapons, action cancelled!")
                print("Weapons in store:", end=' ')
                self.character.print_weapons_stored()
                return False
            elif self.equip_all_weapons():
                return True
            return False
        
        if self.character.current_action == Characters.EquipSpec:
            if not self.character.weapons_stored:
                print("You have no weapon to equip, action cancelled!")
                return False
            elif self.character.nb_of_hands_used() >= 2:
                print("You are already fully equipped, action cancelled!")
                print("Weapons in use:", end=' ')
                self.character.print_weapons_use()
                print("Weapons in store:", end=' ')
                self.character.print_weapons_stored()
                return False
            elif self.equip_spec_weapons():
                return True
            return False
        
        else:
            print("(equip_weapons) mode:", self.character.current_action, "unknown, action cancelled!")
            return False
    
    def unequip_weapons_list(self, weapons_list):
        if not weapons_list:
            print("(EquipChar) Cannot unequip because weapon_list is empty")
            return False
        
        print("")
        print("You are going to unequip the following items:")
        for weapon in weapons_list:
            weapon.print_obj()
        time.sleep(3)
        
        self.next_unequipment = weapons_list
        self.calculate_timelines(weapons_list)
        return self.result()

    def unequip_all_weapons(self):
        return self.unequip_weapons_list(copy.copy(self.character.weapons_use))

    def unequip_spec_weapons(self):    
        equipped_list = copy.copy(self.character.weapons_use)
        equipment_to_remove = []
        while 1:
            print("Current weapons:")
            for equip in equipped_list:
                equip.print_obj()
            print("")
            
            print("Choose a weapon to be unequipped:")            
            try:
                if not equipment_to_remove:
                    read = int(input('--> ID (0 = Cancel): '))
                else:
                    read = int(input('--> ID (0 = Cancel, -1 = Stop): '))
            except:
                print("The input is not an ID")
                print("")
                continue  
            
            if read == -1 and equipment_to_remove:
                print("You have stopped to unequip")
                return self.unequip_weapons_list(equipment_to_remove)
            
            elif self.fight.cancel_action(read):
                return False

            available_equipment = False
            for i in range(len(equipped_list)):
                if read == equipped_list[i].get_id():
                    available_equipment = True
                    equipment_to_remove.append(equipped_list.pop(i))
                    break
                
            if available_equipment is False:
                print("The input is not an available ID")
                print("")
                
            elif not equipped_list:
                return self.unequip_weapons_list(equipment_to_remove)

    def equip_weapons_list(self, weapons_list):
        if not weapons_list:
            print("(EquipChar) Cannot equip because weapon_list is empty")
            return False
        
        print("")
        print("You are going to equip the following weapons:")
        for weapon in weapons_list:
            weapon.print_obj()
        
        self.next_equipment = weapons_list
        self.calculate_timelines(weapons_list)
        time.sleep(3)
        return self.result()

    def equip_all_weapons(self):
        not_equipped_list = []
        for weapon in self.character.weapons_stored:
            if weapon not in self.character.weapons_use:
                not_equipped_list.append(weapon)
        return self.equip_weapons_list(not_equipped_list)

    def equip_spec_weapons(self):
        equipped_list = copy.copy(self.character.weapons_use)
        not_equipped_list = []
        new_equipment = []
        for weapon in self.character.weapons_stored:
            if weapon not in self.character.weapons_use:
                not_equipped_list.append(weapon)
                
        while 1:
            print("Current weapons:")
            for equip in equipped_list:
                equip.print_obj()
            print("")
            
            print("Choose a weapon to be equipped:")
            for equip in not_equipped_list:
                equip.print_obj()
            
            try:
                if not new_equipment:
                    read = int(input('--> ID (0 = Cancel): '))
                else:
                    read = int(input('--> ID (0 = Cancel, -1 = Stop): '))
            except:
                print("The input is not an ID")
                print("")
                continue  
            
            if read == -1 and new_equipment:
                print("")
                print("You have stopped to equip")
                return self.equip_weapons_list(new_equipment)
            
            # Cannot cancel equip move
            elif self.fight.cancel_action(read):
                return False 

            available_equipment = False
            for equip in not_equipped_list:
                if read == equip.get_id():
                    available_equipment = True
                    weapon = equip
                    break
                
            if available_equipment is False:
                print("The input is not an available ID")
                print("")
                continue
            
            nb_of_hands_use = 0
            for equip in equipped_list:
                nb_of_hands_use += equip.hand
            if nb_of_hands_use + weapon.hand <= 2:
                equipped_list.append(weapon)
                not_equipped_list.remove(weapon)
                new_equipment.append(weapon)
            else:
                print("You do not have enough free hands to equip:")
                weapon.print_obj()
                print("")
            
            if nb_of_hands_use + weapon.hand == 2:
                return self.equip_weapons_list(new_equipment)
            
    def result(self):        
        success = False
        if self.next_equipment:
            for weapon in self.next_equipment:
                success = self.character.add_weapon_in_use(weapon)
                if not success:
                    return False
        elif self.next_unequipment:
            for weapon in self.next_unequipment:
                success = self.character.remove_weapon_in_use(weapon)
                if not success:
                    return False
        else:
            print("(EquipChar) Cannot equip, because equip & unequip lists are empty")
            return False
        
        self.character.spend_stamina(self.equip_time * self.character.current_action[3])
        self.character.calculate_characteristic()
        return success
    
    def calculate_timelines(self, weapons):
        self.equip_time = 0
        for weapon in weapons:
            self.equip_time += self.character.current_action[2] * self.character.speed_ratio \
                * math.sqrt(weapon.bulk / Characters.use_bulk_mean)
        self.character.spend_time(self.equip_time)
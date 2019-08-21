import copy as copy
import math as math
import time as time
from sources.character.Characters import Characters
from sources.action.Actions import ActiveActions


#############################################################
###################### EQUIP CHAR CLASS #####################
#############################################################
class EquipChar(ActiveActions):
    """Class to equip a character"""
    
    def __init__(self, fight, initiator):
        super().__init__(self, fight, initiator)
        self.initiator = initiator
        self.next_equipment = []
        self.next_unequipment = []
        self.equip_time = 0.0
        self.is_a_success = self.start()

    def start(self):
        if not self.initiator.check_stamina(Characters.Equip[3]):
            print("You do not have enough stamina (",
                  self.initiator.body.get_current_stamina(), ") to modify your equipment")
            return False
        
        if self.initiator.nb_of_hands_used() == 2 or (
        self.initiator.nb_of_hands_used() == 1 and not self.initiator.weapons_stored):
            return self.unequip_spec_weapons()
        elif self.initiator.nb_of_hands_used() == 0 and self.initiator.weapons_stored:
            return self.equip_spec_weapons()
        elif self.initiator.nb_of_hands_used() == 1 and self.initiator.weapons_stored:
            while 1:
                print("Do you want to equip (EQP) or unequip (UQP) weapons?")            
                read = input('--> Action (0 = Cancel): ')
                
                if self.fight.cancel_action(read):
                    return False
                
                if read == "EQP":
                    return self.equip_spec_weapons()
                elif read == "UQP:
                    return self.unequip_spec_weapons()
                else:
                    print("Your choice is not recognized!")
                
        else:
            print("You have no equipment to equip, action cancelled!")
            return False
    
    def unequip_weapons_list(self, weapons_list):
        print("")
        print("You are going to unequip the following items:")
        for weapon in weapons_list:
            weapon.print_obj()
        time.sleep(3)
        
        self.next_unequipment = weapons_list
        self.calculate_timelines(weapons_list)
        return self.result()

    def unequip_spec_weapons(self):
        print("You have decided to unequip weapons")
        time.sleep(2)
        
        equipped_list = copy.copy(self.initiator.weapons_use)
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
        print("")
        print("You are going to equip the following weapons:")
        for weapon in weapons_list:
            weapon.print_obj()
        
        self.next_equipment = weapons_list
        self.calculate_timelines(weapons_list)
        time.sleep(3)
        return self.result()

    def equip_spec_weapons(self):
        print("You have decided to equip weapons")
        time.sleep(2)
        
        equipped_list = copy.copy(self.initiator.weapons_use)
        not_equipped_list = []
        new_equipment = []
        for weapon in self.initiator.weapons_stored:
            if weapon not in self.initiator.weapons_use:
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
        if self.next_equipment:
            for weapon in self.next_equipment:
                if not self.initiator.add_weapon_in_use(weapon):
                    return False
        else
            for weapon in self.next_unequipment:
                if not self.initiator.remove_weapon_in_use(weapon):
                    return False
       
        self.end_update([self.initiator], self.equip_time * Characters.Equip[3], self.equip_time)
        return True
    
    def calculate_timelines(self, weapons):
        self.equip_time = 0
        for weapon in weapons:
            self.equip_time += Characters.Equip[2] * math.sqrt(weapon.bulk / Characters.use_bulk_mean)

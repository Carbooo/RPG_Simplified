import copy as copy
import math as math
import time as time
import sources.miscellaneous.configuration as cfg
from sources.action.actions import Actions, ActiveActions


#############################################################
###################### EQUIP CHAR CLASS #####################
#############################################################
class ModifyEquipments(ActiveActions):
    """Class to equip a character"""
    
    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Modifying equipment"
        self.next_equipment = []
        self.next_unequipment = []
        self.equip_time = 0.0
        self.is_a_success = self.start()

    def start(self):
        if not self.initiator.check_stamina(cfg.actions["modify_equip"]["stamina"]):
            print("You do not have enough stamina (",
                  self.initiator.body.get_current_stamina(), ") to modify your equipment")
            return False
        
        if self.initiator.equipments.free_hands == 0 or (
                self.initiator.equipments.free_hands == 1 and not self.initiator.equipments.weapons_stored):
            return self.unequip_spec_weapons()
        elif self.initiator.equipments.free_hands == 2 and self.initiator.equipments.weapons_stored:
            return self.equip_spec_weapons()
        elif self.initiator.equipments.free_hands == 1 and self.initiator.equipments.weapons_stored:
            while 1:
                print("Do you want to equip (EQP) or unequip (UQP) weapons?")            
                read = input('--> Action (0 = Cancel): ')
                
                if Actions.cancel_action(read):
                    return False
                
                if read == "EQP":
                    return self.equip_spec_weapons()
                elif read == "UQP":
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
        self.end_update([self.initiator], self.equip_time * cfg.actions["modify_equip"]["stamina"], self.equip_time)
        return True

    def unequip_spec_weapons(self):
        equipped_list = copy.copy(self.initiator.equipments.weapons_in_use)
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
            
            elif Actions.cancel_action(read):
                return False

            available_equipment = False
            for equip in equipped_list:
                if read == equip.get_id():
                    available_equipment = True
                    equipment_to_remove.append(equip)
                    equipped_list.remove(equip)
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
        time.sleep(3)
        
        self.next_equipment = weapons_list
        self.calculate_timelines(weapons_list)
        self.end_update([self.initiator], self.equip_time * cfg.actions["modify_equip"]["stamina"], self.equip_time)
        return True

    def equip_spec_weapons(self):
        equipped_list = copy.copy(self.initiator.equipments.weapons_in_use)
        not_equipped_list = []
        new_equipment = []
        for weapon in self.initiator.equipments.weapons_stored:
            if weapon not in self.initiator.equipments.weapons_in_use:
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
            elif Actions.cancel_action(read):
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
            
    def execute(self):
        if self.next_equipment:
            for weapon in self.next_equipment:
                if not self.initiator.equipments.set_weapon_in_use(weapon):
                    return False
        else:
            for weapon in self.next_unequipment:
                if not self.initiator.equipments.remove_weapon(weapon):
                    return False
                    
        self.initiator.last_action = None  # To remove it from the scheduler
        return True
    
    def calculate_timelines(self, weapons):
        self.equip_time = 0
        for weapon in weapons:
            self.equip_time += cfg.actions["modify_equip"]["duration"] * math.sqrt(weapon.bulk / cfg.use_bulk_mean)

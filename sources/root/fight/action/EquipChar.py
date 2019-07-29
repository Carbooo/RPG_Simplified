import copy as copy
import math as math
import time as time
from sources.root.character.Characters import Characters
from sources.root.fight.action.Actions import Actions


#############################################################
###################### EQUIP CHAR CLASS #####################
#############################################################
class EquipChar:
    'Class to equip a character'
    
    time_ratio = 0.5 #Ratio when the equip / unequp will occur

    def __init__(self, fight, character):
        Actions.__init__(self, fight)
        self.character = character
        self.next_equipment = []
        self.next_unequipment = []
        self.begin_time = character.timeline
        self.end_time = character.timeline
        self.equip_time = 0.0
        self.equip_handicap = 0.0
        self.after_equip_handicap = 0.0
        self.is_dropping = False
        self.is_a_success = self.start()
        
        
    def start(self):
        Actions.start(self)
        if not self.character.is_equip_moving() and \
        not self.character.check_stamina(self.character.current_action[3]):
            print("You do not have enough stamina (", \
                self.attacker.body.get_current_stamina(), ") to modify your equipment")
            return False
        
        if self.character.current_action == Characters.UnequipAll:
            if not self.character.weapons_use:
                print("You have already unequipped all your weapons, action cancelled!")
                return False
            elif self.unequip_all_weapons():
                return True
            return False
        
        if self.character.current_action == Characters.UnequipSpec or \
        self.character.current_action == Characters.UnequipSpecMove:
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
        
        if self.character.current_action == Characters.EquipSpec \
        or self.character.current_action == Characters.EquipSpecMove:
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
        self.character.action_in_progress = self
        print("")
        print("Do you want to put the items away (PAW) or to quickly drop them (DRP) :")
        while 1: 
            read = input('--> (PAW / DRP): ')
            if read == "PAW":
                break
            elif read == "DRP":
                self.is_dropping = True
                break
            else:
                print("Your input is not recognized!")
        
        self.calculate_timelines(weapons_list[0])
        time.sleep(3)
        return True


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
                
            elif equipped_list == []:
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
        self.calculate_timelines(weapons_list[0])
        self.character.action_in_progress = self
        time.sleep(3)
        return True
                

    def equip_all_weapons(self):
        notequipped_list = []
        for weapon_s in self.character.weapons_stored:
            exist = False
            for weapon_u in self.character.weapons_use:
                if weapon_s == weapon_u:
                    exist = True
                    break
            if not exist:
                notequipped_list.append(weapon_s)
        return self.equip_weapons_list(notequipped_list)
        

    def equip_spec_weapons(self):
        equipped_list = copy.copy(self.character.weapons_use)
        notequipped_list = []
        new_equipment = []
        for weapon_s in self.character.weapons_stored:
            exist = False
            for weapon_u in self.character.weapons_use:
                if weapon_s == weapon_u:
                    exist = True
                    break
            if exist is False:
                notequipped_list.append(weapon_s)
        
        while 1:
            print("Current weapons:")
            for equip in equipped_list:
                equip.print_obj()
            print("")
            
            print("Choose a weapon to be equipped:")
            for equip in notequipped_list:
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
            
            #Cannot cancel equip move
            elif self.fight.cancel_action(read):
                return False 

            available_equipment = False
            for equip in notequipped_list:
                if read == equip.get_id():
                    available_equipment = True
                    weapon = equip
                    break
                
            if available_equipment is False:
                print("The input is not an available ID")
                print("")
                continue
            
            NbOfHandsUse = 0
            for equip in equipped_list:
                NbOfHandsUse += equip.hand
            if NbOfHandsUse + weapon.hand <= 2:
                equipped_list.append(weapon)
                notequipped_list.remove(weapon)
                new_equipment.append(weapon)
            else:
                print("You do not have enough free hands to equip:")
                weapon.print_obj()
                print("")
            
            if NbOfHandsUse + weapon.hand == 2:
                return self.equip_weapons_list(new_equipment)
            
        
    def result(self):
        Actions.result(self)
        
        success = False
        if self.next_equipment:
            success = self.character.add_weapon_in_use(self.next_equipment.pop(0))  
        elif self.next_unequipment:
            if self.is_dropping:
                success = self.character.remove_weapon_in_use(self.next_unequipment.pop(0), True)
            else:
                success = self.character.remove_weapon_in_use(self.next_unequipment.pop(0))
        else:
            print("(EquipChar) Cannot equip, because equip & unequip lists are empty")
            return False
        
        if not self.character.is_equip_moving(): #No additional cost for equip/unequip move
            self.character.spend_stamina(self.equip_time * self.character.current_action[3])
        self.character.calculate_characteristic()
        
        if len(self.next_equipment) > 0:
            self.calculate_timelines(self.next_equipment[0])
        elif len(self.next_unequipment) > 0:
            self.calculate_timelines(self.next_unequipment[0])
        return success
    
    
    def calculate_timelines(self, weapon):
        self.equip_time = self.character.current_action[2] * self.character.speed_ratio \
            * math.sqrt(weapon.bulk / Characters.use_bulk_mean)
        if self.is_dropping:
            self.equip_time /= 10
        self.begin_time = self.end_time  # Need to reset time for second equipment
        self.timeline = self.begin_time + EquipChar.time_ratio * self.equip_time / self.character.speed_ratio
        self.end_time = self.begin_time + self.equip_time / self.character.speed_ratio
        self.fight.scheduler.append(self)
        
        if not self.character.is_equip_moving(): # No additional time for equip move
            self.character.spend_time(self.equip_time)
            
            
    
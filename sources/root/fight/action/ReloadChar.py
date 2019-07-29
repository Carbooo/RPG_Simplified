import time as time
from sources.root.character.Equipments import RangedWeapons, Crossbows
from sources.root.character.Characters import Characters
from sources.root.fight.action.Actions import Actions


#############################################################
################### MELEE ATTACK CHAR CLASS #################
#############################################################
class ReloadChar:
    'Class to melee attack a self.character'
    
    time_ratio = 0.95 #Reload just before finishing the action

    def __init__(self, fight, character):
        Actions.__init__(self, fight)
        self.character = character
        self.reload_list = []
        self.reload_time = 0
        self.begin_time = character.timeline
        self.end_time = character.timeline
        self.is_a_success = self.start()
        
        
    def start(self):
        Actions.start(self)
        if self.character.check_stamina(Characters.Reload[3]) is False:
            print("You do not have enough stamina (", \
                self.character.body.return_current_stamina(), ") to reload, action cancelled!")
            return False
        elif self.character.is_using_a_ranged_weapon() is False:
            print("You are not using a ranged weapon, action cancelled!")
            return False
        elif self.character.has_reloaded():
            print("You have already reloaded your ranged weapons, action cancelled!")
            return False
        elif self.character.has_ammo() is False:
            print("You do not have ammo anymore, action cancelled!")
            return False
        
        for weapon in self.character.weapons_use:
            if isinstance(weapon, RangedWeapons):
                ammo_available = []
                for ammo in self.character.ammo:
                    if ammo.ranged_weapon_type == weapon.__class__:
                        ammo_found = False
                        for ammo_bis in ammo_available:
                            if ammo_bis.name == ammo.name:
                                ammo_found = True
                                break
                        if not ammo_found:
                            ammo_available.append(ammo)
                            
                if len(ammo_available) == 1:
                    self.reload_list.append([weapon, ammo_available[0]])
                elif len(ammo_available) > 1:
                    print("Choose the ammo to reload:")
                    for ammo in ammo_available:
                        print("\t\\", end=' ')
                        ammo.print_obj()
                    ammo_chosen = False
                    while not ammo_chosen:
                        try:
                            print("")
                            read = int(input('--> ID (0 = Cancel): '))
                            if self.fight.cancel_action(read):
                                return False
                        except:
                            print("The input is not an ID")
                            continue
                        for ammo in ammo_available:
                            if ammo.get_id() == read:
                                self.reload_list.append([weapon, ammo])
                                ammo_chosen = True
                                break
                        print("ID:", read, "is not available")
        
        self.calculate_timelines()
        self.character.action_in_progress = self
        print("You have decided to reload your ranged weapon")
        print("The actual reload will occur in a few time")
        time.sleep(3)
        return True
        
    
    def result(self):
        Actions.result(self)
        if not self.reload_list:
            print("(ReloadChar) Cannot reload, because reload list is empty")
            return False
        
        self.character.reload(self.reload_list[0][0], self.reload_list[0][1])
        
        if isinstance(self.reload_list[0][0], Crossbows):
            self.character.spend_reload_stamina(self.reload_time * Characters.Reload[3] * 10)
        else:
            self.character.spend_stamina(self.reload_time * Characters.Reload[3])
        self.character.calculate_characteristic()
        
        self.reload_list.pop(0)
        if len(self.reload_list) > 0:
            self.calculate_timelines()
            
        return True


    def calculate_timelines(self):
        self.calculate_reload_time()
        self.begin_time = self.end_time #Need to reset time for second equipment
        self.timeline = self.begin_time + self.reload_time * ReloadChar.time_ratio / self.character.speed_ratio
        self.end_time = self.begin_time + self.reload_time / self.character.speed_ratio
        self.fight.scheduler.append(self)
        
        if not self.character.current_action == Characters.ReloadMove: #No additional time for reload move
            self.character.spend_time(self.reload_time)
        

    def calculate_reload_time(self):
        if not self.reload_list:
            print(self.reload_list)
            print("(ReloadChar) Cannot calculate ReloadTime because reload list is empty")
            return False
        
        weapon = self.reload_list[0][0]
        self.reload_time = (weapon.reload_time - weapon.current_reload) * Characters.Reload[2]
        if isinstance(weapon, Crossbows):
            self.reload_time *= Characters.get_speed_ratio_by_coef(self.character.body.reload_global_ratio())
        else:
            self.reload_time *= self.character.speed_ratio
        
        if self.character.current_action == Characters.ReloadMove:
            self.reload_time *= Characters.ReloadMove[2]
            
        return True

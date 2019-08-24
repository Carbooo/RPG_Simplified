import time as time
from sources.character.Equipments import RangedWeapons, Crossbows
from sources.character.Characters import Characters
from sources.action.Actions import ActiveActions


#############################################################
###################### RELOAD CHAR CLASS ####################
#############################################################
class ReloadChar(ActiveActions):
    """Class to reload a range weapon"""

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Reloading"
        self.weapon_to_reload = None
        self.ammo_to_load = None
        self.is_a_success = self.start()

    def start(self):
        if self.initiator.check_stamina(Characters.Reload[3]) is False:
            print("You do not have enough stamina (",
                  self.initiator.body.return_current_stamina(), ") to reload, action cancelled!")
            return False
        elif self.initiator.is_using_a_ranged_weapon() is False:
            print("You are not using a ranged weapon, action cancelled!")
            return False
        elif self.initiator.has_reloaded():
            print("You have already reloaded your ranged weapons, action cancelled!")
            return False
        elif self.initiator.has_ammo() is False:
            print("You do not have ammo anymore, action cancelled!")
            return False

        for weapon in self.initiator.weapons_use:
            if isinstance(weapon, RangedWeapons):
                self.weapon_to_reload = weapon
                ammo_available = []
                for ammo in self.initiator.ammo:
                    if ammo.ranged_weapon_type == weapon.__class__:
                        ammo_found = False
                        for ammo_bis in ammo_available:
                            if ammo_bis.name == ammo.name:
                                ammo_found = True
                                break
                        if not ammo_found:
                            ammo_available.append(ammo)

                if len(ammo_available) == 1:
                    self.ammo_to_load = ammo_available[0]
                    
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
                                self.ammo_to_load = ammo
                                ammo_chosen = True
                                break
                        print("ID:", read, "is not available")

        print("You have decided to reload your ranged weapon")
        print("Reload in progress...")
        time.sleep(3)
        
        if isinstance(self.weapon_to_reload, Crossbows):
            stamina = self.weapon_to_reload.reload_time * Characters.Reload[3] * 10
        else:
            stamina = self.weapon_to_reload.reload_time * Characters.Reload[3]
        self.end_update([], stamina, self.weapon_to_reload.reload_time)
        return True
    
    def execute(self):
        self.initiator.reload(self.weapon_to_reload, self.ammo_to_load)
        self.initiator.last_action = None  # To remove it from the scheduler
        return True

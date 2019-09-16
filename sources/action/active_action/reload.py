import time as time
import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from sources.character.equipments import RangedWeapons, Crossbows
from sources.action.action import Actions
from sources.action.active_action.active_action import ActiveActions


#############################################################
###################### RELOAD CHAR CLASS ####################
#############################################################
class Reload(ActiveActions):
    """Class to reload a range weapon"""

    def __init__(self, fight, initiator):
        super().__init__(fight, initiator)
        self.name = "Reloading"
        self.weapon_to_reload = None
        self.ammo_to_load = None
        self.is_a_success = self.start()

    def start(self):
        if self.initiator.check_stamina(cfg.actions["reload"]["stamina"]) is False:
            func.optional_print("You do not have enough stamina (",
                  self.initiator.body.return_current_stamina(), ") to reload, action cancelled!")
            return False
        elif self.initiator.equipments.is_using_a_ranged_weapon() is False:
            func.optional_print("You are not using a ranged weapon, action cancelled!")
            return False
        elif self.initiator.equipments.has_reloaded():
            func.optional_print("You have already reloaded your ranged weapons, action cancelled!")
            return False
        elif self.initiator.equipments.has_ammo() is False:
            func.optional_print("You do not have ammo anymore, action cancelled!")
            return False

        for weapon in self.initiator.equipments.weapons_in_use:
            if isinstance(weapon, RangedWeapons):
                self.weapon_to_reload = weapon
                ammo_available = []
                for ammo in self.initiator.equipments.ammo:
                    if ammo.ranged_weapon_type == weapon.__class__:
                        ammo_found = False
                        for ammo_bis in ammo_available:
                            if ammo_bis.name == ammo.name:
                                ammo_found = True
                                break
                        if not ammo_found:
                            ammo_available.append(ammo)

                if len(ammo_available) == 1:
                    self.ammo_to_load  = ammo_available[0]
                    
                elif len(ammo_available) > 1:
                    func.optional_print("Choose the ammo to reload:")
                    for ammo in ammo_available:
                        func.optional_print("\t\\", end=' ')
                        ammo.print_obj()
                    ammo_chosen = False
                    while not ammo_chosen:
                        try:
                            func.optional_print("")
                            read = int(func.optional_input('--> ID (0 = Cancel): '))
                            if Actions.cancel_action(read):
                                return False
                        except:
                            func.optional_print("The input is not an ID")
                            continue
                        for ammo in ammo_available:
                            if ammo.get_id() == read:
                                self.ammo_to_load  = ammo
                                ammo_chosen = True
                                break
                        func.optional_print("ID:", read, "is not available")

        func.optional_print("You have decided to reload your ranged weapon")
        func.optional_print("Reload in progress...")
        time.sleep(3)
        
        if isinstance(self.weapon_to_reload, Crossbows):
            stamina = self.weapon_to_reload.reload_time * cfg.actions["reload"]["stamina"] * 10
        else:
            stamina = self.weapon_to_reload.reload_time * cfg.actions["reload"]["stamina"]
        self.end_update(stamina, self.weapon_to_reload.reload_time)
        return True
    
    def execute(self):
        self.initiator.equipments.reload(self.weapon_to_reload, self.ammo_to_load )
        self.initiator.last_action = None  # To remove it from the scheduler
        return True

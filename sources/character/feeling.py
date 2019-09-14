import math as math
import random as random
import sources.miscellaneous.configuration as cfg


#############################################################
##################### FEELINGS CLASS ########################
#############################################################
class Feeling:
    """Common base class to handle the six feelings"""
    
    def __init__(self, type, sensibility, mastering, knowledge):
        self.type = type
        self.sensibility = float(sensibility)
        self.sensibility_ratio = float(sensibility) / 10.0
        self.mastering = float(mastering)
        self.mastering_ratio = float(mastering) / 10.0
        self.energy = max(0.0, cfg.default_energy + (float(sensibility) - 10.0) * 10.0)
        self.energy_ratio = self.energy / cfg.medium_energy
        self.knowledge = knowledge
        self.warned_of_exceeded_energy = False
    
    def update_energy(self, energy):
        self.energy = max(0, self.energy + energy)
        self.energy_ratio = self.energy / cfg.medium_energy
        
    def gain_energy(self, energy):
        self.update_energy(energy * self.sensibility_ratio)
    
    def loose_energy(self, energy):
        self.update_energy(- energy / self.sensibility_ratio)
      
    def use_energy(self, energy):-
        if not self.check_energy(energy):
            print("Error: Energy feeling below 0")
        
        coef = self.energy_ratio * self.mastering_ratio
        self.loose_energy(energy * self.energy_ratio)
        return coef
        
    def check_energy(self, energy):
        if self.energy >= energy * self.energy_ratio / self.sensibility_ratio:
            return True
        else:
            return False
            
    def natural_energy_update(self, time):
        energy = abs(math.pow((self.energy - cfg.default_energy) / cfg.natural_update_ratio, 3) * time)
        if self.energy > cfg.default_energy:
            self.gain_energy(energy)
        elif self.energy < cfg.default_energy and self.energy > 0:
            self.loose_energy(energy)
    
    def concentrate_energy_update(self, action, ratio):
        ratio *= self.mastering_ratio
        if action == "increase":
            self.gain_energy(cfg.concentrate_update_coef * self.energy_ratio * ratio)
        elif action == "decrease":
            self.loose_energy(cfg.concentrate_update_coef / self.energy_ratio * ratio)
        else:
            print("Error: Wrong action for concentrate_energy_update")
            
    def die_of_exceeded_energy(self, char):
        if self.energy <= cfg.max_safe_energy:
            if self.warned_of_exceeded_energy:
                print("Your ", self.type, " energy is now again under control!")
                self.warned_of_exceeded_energy = False
            return False
        
        energy_gap = (self.energy - cfg.max_safe_energy) / (cfg.max_alive_energy - cfg.max_safe_energy)
        if random.random() < energy_gap / char.willpower_ratio / self.mastering_ratio:
            if not self.warned_of_exceeded_energy: 
                print("Your ", self.type, " energy is overwhelming you and may destroy you!")
                self.warned_of_exceeded_energy = True
                return False
            else:
                print("Your ", self.type, " energy has overwhelmed you and your life is over!")
                char.body.loose_life(100, 1)
                return True

    def print_obj(self):
        print("Type:", self.type, ", Sensibility:", int(round(self.sensibility)), ", Mastering:",
              int(round(self.mastering)), ", Energy:", int(round(self.energy)))

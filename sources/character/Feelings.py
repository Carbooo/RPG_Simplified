import math as math
import random as random

#############################################################
##################### FEELINGS CLASS ########################
#############################################################
class Feelings:
    """Common base class to handle the six feelings"""
    
    natural_update_ratio = 50  # Energy ratio to naturally update feeling
    concentrate_update_coef = 3  # Energy coef to update feeling with concentration
    max_alive_energy = 1000
    max_safe_energy = 200
    
    def __init__(self, type, sensibility, mastering, initial_energy):
        self.type = type
        self.sensibility = sensibility
        self.sensibility_ratio = sensibility / 10
        self.mastering = mastering
        self.mastering_ratio = mastering / 10
        self.energy = initial_energy
        self.energy_ratio = initial_energy / 100
        self.warned_of_exceeded_energy = False
    
    def update_energy(self, energy):
        self.energy = max(0, self.energy + energy)
        self.energy_ratio = self.energy / 100
        
    def gain_energy(self, energy):
        self.update_energy(energy * self.sensibility_ratio)
    
    def loose_energy(self, energy):
        self.update_energy(- energy / self.sensibility_ratio)
      
    def use_energy(self, energy):
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
        energy = abs(math.pow((self.energy - 100) / Feelings.natural_update_ratio, 3) * time)
        if self.energy > 100:
            self.gain_energy(energy)
        elif self.energy < 100 and self.energy > 0:
            self.loose_energy(energy)
    
    def concentrate_energy_update(self, action, ratio):
        ratio *= self.mastering_ratio
        if action == "increase":
            self.gain_energy(Feelings.concentrate_update_coef * self.energy_ratio * ratio)
        elif action == "decrease":
            self.loose_energy(Feelings.concentrate_update_coef / self.energy_ratio * ratio)
        else:
            print("Error: Wrong action for concentrate_energy_update")
            
    def die_of_exceeded_energy(self, char):
        if self.energy <= Feelings.max_safe_energy:
            if self.warned_of_exceeded_energy:
                print("Your ", self.type, " energy is now again under control!")
                self.warned_of_exceeded_energy = False
            return False
        
        energy_gap = (self.energy - Feelings.max_safe_energy) / (Feelings.max_alive_energy - Feelings.max_safe_energy)
        if random.random() < energy_gap / self.willpower_ratio / self.mastering_ratio:
            if not self.warned_of_exceeded_energy: 
                print("Your ", self.type, " energy is overwhelming you and may destroy you!")
                self.warned_of_exceeded_energy = True
                return False
            else:
                print("Your ", self.type, " energy has overwhelmed you and your life is over!")
                char.body.loose_life(100, 1)
                return True
    
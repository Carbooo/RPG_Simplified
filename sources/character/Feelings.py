import math as math

#############################################################
##################### FEELINGS CLASS ########################
#############################################################
class Feelings:
    """Common base class to handle the six feelings"""
    
    natural_update_ratio = 50  # Energy difference ratio to turn update
    
    def __init__(self, type, sensibility, mastering, initial_energy):
        self.type = type
        self.sensibility = sensibility
        self.sensibility_ratio = sensibility / 10
        self.mastering = mastering
        self.mastering_ratio = mastering / 10
        self.energy = initial_energy
        self.energy_ratio = initial_energy / 100
    
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
        
        self.loose_energy(energy * self.energy_ratio)
        return self.energy_ratio * self.mastering_ratio
        
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
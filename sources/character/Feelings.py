

#############################################################
##################### FEELINGS CLASS ########################
#############################################################
class Feelings:
    """Common base class to handle the six feelings"""
    
    def __init__(self, type, sensibility, mastering, initial_energy):
        self.type = type
        self.sensibility = sensibility
        self.sensibility_ratio = sensibility / 10
        self.mastering = mastering
        self.mastering_ratio = mastering / 10
        self.energy = initial_energy
    
    def gain_energy(self, standard_energy):
        self.energy += standard_energy * self.sensibility_ratio
    
    def loose_energy(self, standard_energy):
        self.energy -= standard_energy / self.sensibility_ratio
        if self.energy < 0:
            print("Error: Feeling level below 0")
      
    def use_energy(self, standard_energy):
        self.energy -= standard_energy / self.mastering_ratio
        if self.energy < 0:
            print("Error: Feeling level below 0")
            
    def check_energy(self, standard_energy):
        if self.energy >= standard_energy / self.mastering_ratio:
            return True
        else:
            print("Not enough energy to cast this spell")
            return False
            
    def natural_energy_update(self, time):
        if self.energy >= 150:
            self.gain_energy(0.1 * self.energy * time)
        elif self.energy <= 50:
            self.loose_energy(min(self.energy, 10 * time))
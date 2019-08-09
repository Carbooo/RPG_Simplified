import pickle
import time as time
from sources.action.Actions import Actions

#############################################################
####################### SAVE CLASS ##########################
#############################################################
class Save:
    'Class to save a fight'
    
    save_path = 'saves\\'
    save_extension = '.sav'
    
    def __init__(self, fight, filename = False):
        Actions.__init__(self, fight)
        self.filename = filename
        self.is_a_success = self.start()
        
        
    def start(self):
        Actions.start(self)
        
        if self.filename:
            file = open(Save.save_path + self.filename + Save.save_extension, 'wb')
            pickle.dump(self, file)
        else:
            print("Write a file name for the saving:")     
            
            while 1:
                self.filename = input('--> file name (0 = Cancel): ')
                
                if self.fight.cancel_action(self.filename):
                    return False
                
                try:
                    file = open(Save.save_path + self.filename + Save.save_extension, 'wb')
                    pickle.dump(self, file)
                    print("***** GAME HAS BEEN SAVED *****")
                    time.sleep(3)
                    return True
                except:
                    print("Cannot open file:", self.filename)
        
    
#############################################################
####################### LOAD CLASS ##########################
#############################################################
class Load:
    'Class to load a fight'
    
    
    def __init__(self, fight):
        Actions.__init__(self, fight)
        self.is_a_success = self.start()
        
        
    def start(self):
        Actions.start(self)
        print("Write the file name of a previous save:")
        
        while 1:
            filename = input('--> file name (0 = Cancel): ')
            
            if self.fight.cancel_action(filename):
                return False           
            
            try:
                open_file = True
                file = open(Save.save_path + filename + Save.save_extension, 'rb')
            except:
                open_file = False
                print("Cannot open file:", filename)
        
            if open_file:
                self = pickle.load(file)
                print("***** GAME HAS BEEN LOADED *****")
                time.sleep(3)
                self.fight.start()
                exit(0)
                

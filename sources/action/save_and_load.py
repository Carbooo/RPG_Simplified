import pickle
import time as time
from shutil import copyfile
from sources.action.action import Actions
import sources.miscellaneous.global_functions as func


#############################################################
####################### SAVE CLASS ##########################
#############################################################
class Save(Actions):
    """Class to save a fight"""
    
    save_path = 'saves\\'
    save_extension = '.sav'
    
    def __init__(self, fight, filename=None):
        super().__init__(fight)
        self.filename = filename
        self.is_a_success = self.start()

    def start(self):
        if self.filename:
            file = open(Save.save_path + self.filename + Save.save_extension, 'wb')
            pickle.dump(self, file)
        else:
            func.optional_print("Write a file name for the saving:")
            
            while 1:
                self.filename = func.optional_input('--> file name (0 = Cancel): ')
                
                if Actions.cancel_action(self.filename):
                    return False
                
                try:
                    file = open(Save.save_path + self.filename + Save.save_extension, 'wb')
                    pickle.dump(self, file)
                    func.optional_print("***** GAME HAS BEEN SAVED *****")
                    time.sleep(3)
                    return True
                except:
                    func.optional_print("Cannot open file:", self.filename)

    @staticmethod
    def copy_to_next(filename):
        if "AutoSave" in filename:
            source = Save.save_path + filename + Save.save_extension
            new_name = filename[:-1] + str(int(filename[-1:]) + 1)
            target = Save.save_path + new_name + Save.save_extension
            copyfile(source, target)
        else:
            func.optional_print("Error: Function should only be used for AutoSave files")

    @staticmethod
    def copy_all_to_next():
        for i in range(4, 0, -1):  # Files need to be initialized
            Save.copy_to_next("AutoSave" + str(i))


#############################################################
####################### LOAD CLASS ##########################
#############################################################
class Load(Actions):
    """Class to load a fight"""

    def __init__(self, fight):
        super().__init__(fight)
        self.is_a_success = self.start()
        
    def start(self):
        func.optional_print("Write the file name of a previous save:")
        
        while 1:
            filename = func.optional_input('--> file name (0 = Cancel): ')
            
            if Actions.cancel_action(filename):
                return False           
            
            try:
                open_file = True
                file = open(Save.save_path + filename + Save.save_extension, 'rb')
            except:
                open_file = False
                func.optional_print("Cannot open file:", filename)
        
            if open_file:
                self = pickle.load(file)
                func.optional_print("***** GAME HAS BEEN LOADED *****")
                time.sleep(3)
                self.fight.start()
                exit(0)

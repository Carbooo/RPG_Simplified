from sources.action.action import Actions
import sources.miscellaneous.global_functions as func


#############################################################
################## GET CHAR INFORMATION CLASS ###############
#############################################################
class GetCharInformation(Actions):
    """Class to get information on a character"""
    
    def __init__(self, fight):
        super().__init__(fight)
        self.is_a_success = self.start()
        
    def start(self):
        func.optional_print("Choose one of the following character:")
        
        for char in self.fight.team1.characters_list:
            char.print_basic()
            func.optional_print("")
            
        for char in self.fight.team2.characters_list:
            char.print_basic()
            func.optional_print("")
        
        while 1:
            try:
                read = int(func.optional_input('--> ID (0 = Cancel): '))
                if Actions.cancel_action(read):
                    return False
            except:
                func.optional_print("The input is not an ID")
                continue
            
            for char in self.fight.team1.characters_list:
                if read == char.get_id():
                    func.optional_print("")
                    char.print_obj()
                    func.optional_print("")
                    return True
            
            for char in self.fight.team2.characters_list:
                if read == char.get_id():
                    func.optional_print("")
                    char.print_obj()
                    func.optional_print("")
                    return True                
            
            func.optional_print("ID:", read, "is not available")

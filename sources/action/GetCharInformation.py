from sources.action.Actions import Actions


#############################################################
################## GET CHAR INFORMATION CLASS ###############
#############################################################
class GetCharInformation(Actions):
    'Class to get information on a character'
    
    def __init__(self, fight):
        super().__init__(fight)
        self.is_a_success = self.start()
        
    def start(self):
        print("Choose one of the following character:")
        
        for char in self.fight.team1.characters_list:
            char.print_basic()
            print("")
            
        for char in self.fight.team2.characters_list:
            char.print_basic()
            print("")            
        
        while 1:
            try:
                read = int(input('--> ID (0 = Cancel): '))
                if self.fight.cancel_action(read):
                    return False
            except:
                print("The input is not an ID")
                continue
            
            for char in self.fight.team1.characters_list:
                if read == char.get_id():
                    print("")
                    char.print_obj()
                    print("")
                    return True
            
            for char in self.fight.team2.characters_list:
                if read == char.get_id():
                    print("")
                    char.print_obj()
                    print("")
                    return True                
            
            print("ID:", read, "is not available")

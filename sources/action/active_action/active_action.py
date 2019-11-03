import random as random
from sources.action.action import Actions
from sources.miscellaneous import configuration as cfg


#############################################################
##################### ACTIVE ACTIONS CLASS ##################
#############################################################
class ActiveActions(Actions):
    """
    Super class for all real actions.
    For all new action, stop_action, fighting_availability and get_ranged_action_ratio must be updated
    """

    def __init__(self, fight, initiator):
        super().__init__(fight)
        self.name = "Generic active actions"
        self.feeling_type = None
        self.initiator = initiator
        self.timeline = self.initiator.timeline

    def end_update(self, stamina, time, absolute_time=False):
        self.initiator.spend_stamina(stamina)
        if absolute_time:
            self.initiator.spend_absolute_time(time)
        else:
            self.initiator.spend_time(time)

    @staticmethod
    def get_attack_coef(char, timeline):
        return random.gauss(cfg.mean, cfg.high_variance) * char.get_fighting_availability(timeline)

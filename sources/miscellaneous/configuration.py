######################## LISTING KEY ITEMS ######################
equipments_list = []
char_list = []
team_list = []
field_list = []

######################## GENERIC VARIABLES ######################
variance = 0.1  # Gauss variance
high_variance = 0.25  # Gauss variance

######################## EQUIPMENTS CONFIG ######################
armor_resis_def_ratio = 2.0  # Coef apply to resis dim rate to calculate defense
armor_def_malus_rate = 2.0  # Armor def lost when being hit
shield_def_malus_rate = 0.1  # Armor def lost when defending
attack_weapon_def_malus_rate = 0.01  # Attack weapon def lost when defending

######################## CHARACTER CONFIG ######################
defense_time = 0.5  # Turn time before having a fully operational defense
max_position_area = 6  # Max range for characters positions
load_mean = 50.0  # Load reference for characters characteristics
bulk_mean = 6.0  # Bulk reference for characters characteristics
use_load_mean = 15.0  # Weapons use load reference for characters
use_bulk_mean = 3.5  # Weapons use bulk reference for characters
max_bonus = 1.5  # Max load and bulk bonus
min_speed = 1.0 / 6.0  # Minimum speed for char (necessary for hurt char)
accuracy_mean = 100.0  # Accuracy reference for characters
critical_hit_chance = 0.083  # Chances to hit the head or other key areas (1 / 12)
critical_hit_boost = 6.0  # Coef boost when doing a critical hit
max_magic_distance = 100.0  # Around 200 meters
free_hand_melee_defense = 0.75  # Melee defense for each free hand
free_hand_melee_handiness = 7.5  # Melee handiness for each free hand
free_hand_melee_power = 0.75  # Melee power for each free hand
free_hand_damage_life_rate = 1.0  # extra life damages of hits with free hands
free_hand_ignoring_armor_rate = 0.1  # ignoring armor rate of hits with free hands
free_hand_pen_rate = 0.05  # Penetration of hits with free hands
free_hand_resis_dim_rate = 0.01  # Armor diminution of hits with free hands
team_state_effect_on_moral = 1.0 / 4.0  # Math.pow(team state, this value) as morale
melee_attack_fighting_availability = 1.0  # impact coef on fighting availability
ranged_attack_fighting_availability = 0.25
magic_attack_fighting_availability = 0.35

########################## BODY CONFIG #######################
life_resting_coef = 14400.0  # Rest coefficient
stamina_resting_coef = 200.0  # Rest coefficient
turn_stamina = 0.5  # Stamina reference used

######################## FEELING CONFIG ######################
concentrate_update_coef = 3  # Energy coef to update feeling with concentration
max_alive_energy = 1000.0
max_safe_energy = 300.0
feelings_list = ["Wrath", "Joy", "Love", "Hate", "Fear", "Sadness"]
default_energy = 50.0  # Starting energy for sensibility 10
medium_energy = 100.0  # Energy reference for spells
natural_increase_threshold = 150.0  # Energy threshold to increase feeling (with square2)
natural_decrease_reference = 20.0  # Energy reference to decrease feeling (divided by)

######################## FIELD CONFIG ######################
melee_handicap_ratio = 0.5
ranged_handicap_ratio = 0.5
no_obstacle = " "
melee_handicap = "~"
melee_obstacle = "="
ranged_handicap = ":"
ranged_obstacle = "#"
full_handicap = "%"
full_obstacle = "X"
obstacle_types_list = [no_obstacle, melee_handicap, melee_obstacle, ranged_handicap, ranged_obstacle, full_handicap,
                       full_obstacle]

######################## REST CONFIG ######################
min_rest_turn = 1
max_rest_turn = 10
resting_ratio = 1.0 / 3.0

#################### CONCENTRATE CONFIG ###################
min_concentration_turn = 3
max_concentration_turn = 10
concentration_rate = 1.0 / 3.0
deconcentration_rate = 1.5

######################## MOVE CONFIG ######################
nb_of_move_before_recalculating_path = 2  # Ratio when the path will be recalculated
max_move_per_action = 15  # To prevent eternal stupid moving

################### RANGED ATTACK CONFIG ##################
ranged_attack_stage = [25, 50]  # [Blocked", "Hit", "Hit & stopped"]
moving_char_shooting_handicap = 0.5
melee_fighter_shooting_handicap = 0.5
decrease_hit_chance_per_case = 0.01  # Every case, the distance hit chance diminishes by this ratio
min_distance_ratio = 0.05  # The distance hit chance cannot go lower than that
min_ranged_def_ratio = 0.33  # The minimum ranged def ratio based on the distance between target and shooter

################### MELEE ATTACK CONFIG ###################
melee_attack_stage = [0, 25, 50, 75]  # ["Blocked" < "Delay" < "Hit" < "Strong hit" < "Huge hit"]
random_defenser_move_probability = 0.25
random_attacker_move_probability = 0.35

###################### ACTIONS CONFIG #####################
# A turn is around 6 seconds
# Between each case, there are approximatively 2 meters
actions = {
    "pass_time": {
        "description": "Wait a little",
        "command": "PAS",
        "duration": 0.1,  # Not used, duration choose by the user
        "stamina": 0.0
    },
    "rest": {
        "description": "Rest a little",
        "command": "RES",
        "duration": 0.0,  # Not used, duration choose by the user
        "stamina": 0.0
    },
    "concentrate": {
        "description": "Concentrate on your mind and feelings",
        "command": "CON",
        "duration": 0.0,  # Not used, duration choose by the user
        "stamina": 1.5
    },
    "melee_attack": {
        "description": "Melee attack an enemy character",
        "command": "MAT",
        "duration": 0.5,
        "stamina": 1.0
    },
    "ranged_attack": {
        "description": "Ranged attack an enemy character",
        "command": "RAT",
        "duration": 0.5,
        "stamina": 0.75
    },
    "reload": {
        "description": "Reload your ranged weapon",
        "command": "REL",
        "duration":  0.0,  # Not used, reload time is defined by the equipment
        "stamina": 0.1
    },
    "move": {
        "description": "Move to an adjacent case",
        "command": "MOV",
        "duration": 0.2,  # Normal run is around 2.7 meters -->  twice as slow here
        "stamina": 0.1
    },
    "modify_equip": {
        "description": "Equip / Unequip weapons",
        "command": "EQP",
        "duration": 0.5,
        "stamina": 0.1
    },
    "spell": {
        "description": "Cast a spell",
        "command": "SPL",
        "duration": 0.0,  # Not used, different for each spell
        "stamina": 0.0  # Not used, different for each spell
    },
    "information": {
        "description": "Information on a character state",
        "command": "INF",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    },
    "save": {
        "description": "Save the current game state",
        "command": "SAV",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    },
    "load": {
        "description": "Load a previous game state",
        "command": "LOA",
        "duration": 0.0,  # Irrelevant, not used
        "stamina": 0.0  # Irrelevant, not used
    }
}

######################## SPELLS CONFIG ######################
spells = []
recurrent_spell_frequency = 1.0  # Frequency (in turn) when effects occur

##################### WRATH SPELLS CONFIG ###################
wrath_spells = {
    "description": "Wrath spells",
    "code": "WRA",
    "list": []
}
wrath_improve_strength = {
    "description": "Improve your strength",
    "code": "STR"
}
wrath_fireball = {
    "description": "Throw a fireball",
    "code": "FBL"
}
spells.append(wrath_spells)
wrath_spells["list"].append(wrath_improve_strength)
wrath_spells["list"].append(wrath_fireball)

wrath_spells_energy = {
    "STR": 10.0,
    "FBL": 30.0
}
wrath_spells_time = {
    "STR": 1.0,
    "FBL": 2.5
}
wrath_spells_stamina = {
    "STR": 1.0,
    "FBL": 7.5
}
wrath_spells_hands = {
    "STR": 0,
    "FBL": 2
}
wrath_spells_knowledge = {
    "STR": 1,
    "FBL": 3
}
wrath_spells_power = {
    "STR": {
        "force": 2.0,
        "reflex": 0.8,
        "dexterity": 0.6,
        "duration": 10.0
    },
    "FBL": {
        "attack_value": 50.0,
        "spread_distance": 1,
        "damage_life_rate": 1.5,
        "ignoring_armor_rate": 0.15,
        "pen_rate": 0.1,
        "resis_dim_rate": 0.5
    }
}

##################### JOY SPELLS CONFIG ###################
joy_spells = {
    "description": "Joy spells",
    "code": "JOY",
    "list": []
}
joy_energize = {
    "description": "Boost all your attributes and restore some stamina",
    "code": "EGY"
}
joy_burning_light = {
    "description": "Send a burning light",
    "code": "LGT"
}
spells.append(joy_spells)
joy_spells["list"].append(joy_energize)
joy_spells["list"].append(joy_burning_light)

joy_spells_energy = {
        "EGY": 10.0,
        "LGT": 20.0
    }
joy_spells_time = {
    "EGY": 1.0,
    "LGT": 1.75
}
joy_spells_stamina = {
    "EGY": 2.0,
    "LGT": 4.0
}
joy_spells_hands = {
    "EGY": 0,
    "LGT": 1
}
joy_spells_knowledge = {
    "EGY": 1,
    "LGT": 2
}
joy_spells_power = {
    "EGY": {
        "moral_increase": 1.15,
        "stamina_restored": 20.0,
        "duration": 10.0
    },
    "LGT": {
        "attack_value": 20.0,
        "damage_life_rate": 1.25,
        "ignoring_armor_rate": 0.0,
        "pen_rate": 0.2,
        "resis_dim_rate": 0.33,
        "delay": 1.5,
        "min_damage_for_delay": 5.0
    }
}

##################### LOVE SPELLS CONFIG ###################
love_spells = {
    "description": "Love spells",
    "code": "LOV",
    "list": []
}
love_shield = {
    "description": "Set a protective shield",
    "code": "SHD"
}
love_heal = {
    "description": "Cure an injure ally",
    "code": "HEA"
}
spells.append(love_spells)
love_spells["list"].append(love_shield)
love_spells["list"].append(love_heal)

love_spells_energy = {
        "SHD": 15.0,
        "HEA": 30.0
    }
love_spells_time = {
    "SHD": 1.75,
    "HEA": 3.0
}
love_spells_stamina = {
    "SHD": 2.5,
    "HEA": 5.0
}
love_spells_hands = {
    "SHD": 2,
    "HEA": 2
}
love_spells_knowledge = {
    "SHD": 2,
    "HEA": 3
}
love_spells_power = {
    "SHD": {
        "resistance": 10.0,
        "turn_decay": 10.0
    },
    "HEA": {
        "heal": 40.0
    }
}

##################### SADNESS SPELLS CONFIG ###################
sadness_spells = {
    "description": "Sadness spells",
    "code": "SAD",
    "list": []
}
sadness_throw_ice_pick = {
    "description": "Throw an ice pick",
    "code": "IPK"
}
sadness_despair_storm = {
    "description": "Create a storm slowing and generating despair",
    "code": "DST"
}
spells.append(sadness_spells)
sadness_spells["list"].append(sadness_throw_ice_pick)
sadness_spells["list"].append(sadness_despair_storm)

sadness_spells_energy = {
    "IPK": 20.0,
    "DST": 35.0
}
sadness_spells_time = {
    "IPK": 1.75,
    "DST": 3.0
}
sadness_spells_stamina = {
    "IPK": 2.5,
    "DST": 7.5
}
sadness_spells_hands = {
    "IPK": 1,
    "DST": 2
}
sadness_spells_knowledge = {
    "IPK": 2,
    "DST": 4
}
sadness_spells_power = {
    "IPK": {
        "attack_value": 50.0,
        "damage_life_rate": 1.5,
        "ignoring_armor_rate": 0.1,
        "pen_rate": 0.3,
        "resis_dim_rate": 0.2
    },
    "DST": {
        "spread_distance": 3,
        "moral_dim_rate": 0.5,
        "stamina_dim_rate": 3.0,
        "speed_dim_rate": 0.3,
        "duration": 15.0
    }
}

##################### FEAR SPELLS CONFIG ###################
fear_spells = {
    "description": "Fear spells",
    "code": "FEA",
    "list": []
}
fear_opposing_winds = {
    "description": "Improve your strength",
    "code": "OWI"
}
fear_gigantic_fist = {
    "description": "Throw a fireball",
    "code": "FBL"
}
spells.append(fear_spells)
fear_spells["list"].append(fear_opposing_winds)
fear_spells["list"].append(fear_gigantic_fist)

fear_spells_energy = {
    "OWI": 15.0,
    "MFI": 22.5
}
fear_spells_time = {
    "OWI": 1.25,
    "MFI": 1.75
}
fear_spells_stamina = {
    "OWI": 1.5,
    "MFI": 3.0
}
fear_spells_hands = {
    "OWI": 2,
    "MFI": 1
}
fear_spells_knowledge = {
    "OWI": 2,
    "MFI": 3
}
fear_spells_power = {
    "OWI": {
        "melee_def_ratio": 0.4,
        "defense": 15.0,
        "duration": 10.0
    },
    "MFI": {
        "attack_value": 27.5,
        "damage_life_rate": 1.0,
        "ignoring_armor_rate": 0.85,
        "pen_rate": 0.05,
        "resis_dim_rate": 0.25,
        "min_damage_for_moving": 15.0
    }
}

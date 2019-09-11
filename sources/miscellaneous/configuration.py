######################## LISTING KEY ITEMS ######################
equipments_list = []
char_list = []
team_list = []
field_list = []

######################## GENERIC VARIABLES ######################
variance = 0.1  # Gauss variance
high_variance = 0.25  # Gauss variance

######################## EQUIPMENTS CONFIG ######################
armor_def_malus_rate = 0.1  # Armor def lost when being hit
shield_def_malus_rate = 0.01  # Armor def lost when defending
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
free_hand_melee_handiness = 15.0  # Melee handiness for each free hand
free_hand_melee_power = 0.75  # Melee power for each free hand
free_hand_melee_range = 5.0  # Melee range if no weapon
free_hand_pen_rate = 0.3  # Penetration of hits with free hands
free_hand_resis_dim_rate = 0.01  # Armor diminution of hits with free hands
free_hand_melee_defense = 0.75  # Melee defense for each free hand

########################## BODY CONFIG #######################
life_resting_coef = 14400.0  # Rest coefficient
stamina_resting_coef = 200.0  # Rest coefficient
turn_stamina = 1.0  # Stamina reference used

######################## FEELING CONFIG ######################
natural_update_ratio = 50  # Energy ratio to naturally update feeling
concentrate_update_coef = 3  # Energy coef to update feeling with concentration
max_alive_energy = 1000
max_safe_energy = 200
feelings_list = ["Wrath", "Joy", "Love", "Hate", "Fear", "Sadness"]

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

################### RANGED ATTACK CONFIG ##################
ranged_attack_stage = [25, 50]  # [Blocked", "Hit", "Hit & stopped"]
moving_char_shooting_handicap = 0.66
melee_fighter_shooting_handicap = 0.75

################### MELEE ATTACK CONFIG ###################
melee_attack_stage = [0, 25, 50, 75]  # ["Blocked" < "Delay" < "Hit" < "Strong hit" < "Huge hit"]
random_defenser_move_probability = 0.25
random_attacker_move_probability = 0.5

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
        "duration": 1.0,  # Not used, duration choose by the user
        "stamina": 0.0
    },
    "concentrate": {
        "description": "Concentrate on your mind and feelings",
        "command": "CON",
        "duration": 1.0,  # Not used, duration choose by the user
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
        "duration": 0.15,  # Normal run is around 2.7 meters --> around 1 case per second
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
wrath_spells_power = {
    "STR": {
        "force": 2.0,
        "reflex": 0.8,
        "dexterity": 0.6,
        "duration": 5.0
    },
    "FBL": {
        "attack_value": 50.0,
        "spread_distance": 1,
        "resis_dim_rate": 0.5,
        "pen_rate": 0.25
    }
}

##################### JOY SPELLS CONFIG ###################
joy_spells = {
    "description": "Joy spells",
    "code": "JOY",
    "list": []
}
joy_energize = {
    "description": "Boost all your attributes",
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
    "EGY": 1.0,
    "LGT": 3.0
}
joy_spells_hands = {
    "EGY": 0,
    "LGT": 1
}
joy_spells_power = {
    "EGY": {
        "coef": 1.2,
        "duration": 5.0
    },
    "LGT": {
        "attack_value": 20.0,
        "resis_dim_rate": 0.33,
        "pen_rate": 0.1,
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
love_spells_power = {
    "SHD": {
        "defense": 100.0,
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
    "description": "Create a cloud generating despair",
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
sadness_spells_power = {
    "IPK": {
        "attack_value": 50.0,
        "resis_dim_rate": 0.2,
        "pen_rate": 0.35
    },
    "DST": {
        "spread_distance": 3,
        "moral_dim_rate": 0.5,
        "stamina_dim_rate": 3.0,
        "movement_dim_rate": 0.4
    }
}

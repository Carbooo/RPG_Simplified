from flask import Flask, request, jsonify
from flask_cors import CORS
import json

import sources.miscellaneous.configuration as cfg
import sources.miscellaneous.global_functions as func
from data.import_data import ImportData
from sources.fight.fight import Fight


##################### API INTEGRATION #####################
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Store game state between requests
fight = None

@app.route('/api/initialize', methods=['POST'])
def initialize_game():
    # Data loading
    ImportData("Armors", "data/Armors.csv")
    ImportData("Shields", "data/Shields.csv")
    ImportData("MeleeWeapons", "data/MeleeWeapons.csv")
    ImportData("Ammo", "data/Ammo.csv")
    ImportData("RangedWeapons", "data/RangedWeapons.csv")
    ImportData("Characters", "data/Characters.csv")
    ImportData("Teams", "data/Teams.csv")
    ImportData("ObstaclesField", "data/maps/Short.csv")
    ImportData("ObstaclesField", "data/maps/ShortObstacles.csv")
    ImportData("ObstaclesField", "data/maps/TwoBridges.csv")
    ImportData("ObstaclesField", "data/maps/LongObstacles.csv")
    ImportData("ObstaclesField", "data/maps/VeryLongTwoBridges.csv")

    # Initialize fight
    func.log_level = 1
    fight = Fight(cfg.field_list[3], cfg.team_list[0], cfg.team_list[1])  # Hard coded for now, shoud be a request.json parameter later on
    return jsonify(fight.get_game_state())

@app.route('/api/action', methods=['POST'])
def handle_action():
    fight.execute_action(request.json)
    return jsonify(fight.get_game_state())

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(fight.get_game_state())

@app.route('/api/end-turn', methods=['POST'])
def end_turn():
    fight.end_character_turn(request.json)
    return jsonify(fight.get_game_state())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
import math
from decimal import Decimal
import html


class BoardGame:
    def __init__(self, game_data, tags=[], expansions=[]):
        self.id = game_data["id"]
        self.name = game_data["name"]
        self.description = html.unescape(game_data["description"])
        self.image = game_data["image"]
        self.categories = game_data["categories"]
        self.mechanics = game_data["mechanics"]
        self.players = self.calc_num_players(game_data, expansions)
        self.weight = self.calc_weight(game_data)
        self.playing_time = self.calc_playing_time(game_data)
        self.tags = tags
        self.expansions = expansions

    def _num_players_is_recommended(self, num, votes):
        return int(votes['best_rating']) + int(votes['recommended_rating']) > int(votes['not_recommended_rating'])

    def _num_players_is_best(self, num, votes):
        return int(votes['best_rating']) > 10 and int(votes['best_rating']) > int(votes['recommended_rating'])

    def calc_num_players(self, game_data, expansions):
        num_players = []
        for playcount in game_data["suggested_numplayers"]:
            num = playcount["numplayers"]
            label_to_votes = {val["value"]: val["numvotes"] for val in playcount["result"]}
            votes = {
                "best_rating": 0,
                "recommended_rating": 0,
                "not_recommended_rating": 0,
            }
            for label, numvotes in label_to_votes.items():
                votes[label.lower().replace(" ", "_") + "_rating"] = numvotes

            if not self._num_players_is_recommended(num, votes):
                continue

            if "+" not in num:
                is_best = self._num_players_is_best(num, votes)
                num_players.append((num, "best" if is_best else "recommended"))
            else:
                for i in range(int(num.replace("+", "")) + 1, 11):
                    is_best = self._num_players_is_best(num, votes)
                    num_players.append((num, "best" if is_best else "recommended"))

        for expansion in expansions:
            for expansion_num, _ in expansion.players:
                if expansion_num not in [num for num, _ in num_players]:
                    num_players.append((expansion_num, "expansion"))

        num_players = sorted(num_players, key=lambda x: int(x[0].replace("+", "")))

        return num_players

    def calc_playing_time(self, game_data):
        playing_time_mapping = {
            30: '< 30min',
            60: '30min - 1h',
            120: '1-2h',
            180: '2-3h',
            240: '3-4h',
        }
        for playing_time_max, playing_time in playing_time_mapping.items():
            if playing_time_max > int(game_data["playing_time"]):
                return playing_time

        return '> 4h'

    def calc_weight(self, game_data):
        weight_mapping = {
            0: "Light",
            1: "Light",
            2: "Light Medium",
            3: "Medium",
            4: "Medium Heavy",
            5: "Heavy",
        }
        return weight_mapping[math.ceil(Decimal(game_data["weight"]))]

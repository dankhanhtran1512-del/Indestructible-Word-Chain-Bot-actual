class ScoreManager:
    def __init__(self):
        self.players = {}

    def ensure_player(self, player_id, player_name):
        if player_id not in self.players:
            self.players[player_id] = {
                "name": player_name,
                "score": 0
            }

    def add_points(self, player_id, player_name, points):
        self.ensure_player(player_id, player_name)
        self.players[player_id]["name"] = player_name
        self.players[player_id]["score"] += points
        return self.players[player_id]["score"]

    def get_score(self, player_id, player_name):
        self.ensure_player(player_id, player_name)
        return self.players[player_id]["score"]

    def top_players(self, limit=10):
        return sorted(
            self.players.values(),
            key=lambda player: player["score"],
            reverse=True
        )[:limit]
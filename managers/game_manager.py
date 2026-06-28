from games.engine import GameEngine


class GameManager:
    def __init__(self):
        self.games = {}

    def start_game(self, channel_id, languages):
        self.games[channel_id] = GameEngine(languages)
        return self.games[channel_id]

    def get_game(self, channel_id):
        return self.games.get(channel_id)

    def has_game(self, channel_id):
        return channel_id in self.games

    def end_game(self, channel_id):
        if channel_id not in self.games:
            return False

        self.games[channel_id].running = False
        return True

    def active_channel_ids(self):
        return list(self.games.keys())
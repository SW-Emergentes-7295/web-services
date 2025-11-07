from datetime import datetime

class CommandVoice:
    def __init__(self, user_id: str, command_text: str, timestamp: datetime = None):
        self.user_id = user_id
        self.command_text = command_text
        self.timestamp = timestamp or datetime.now()
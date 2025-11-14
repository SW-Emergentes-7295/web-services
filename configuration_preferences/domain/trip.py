class Trip:
    def __init__(self, title: str, date: str, time: str, route: str):
        self.title = title
        self.date = date
        self.time = time
        self.route = route

    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "route": self.route
        }
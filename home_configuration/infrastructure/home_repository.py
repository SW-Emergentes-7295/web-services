from domain.home import Home

class HomeRepository:
    def __init__(self):
        pass

    def save(self, home:Home):
        print("gaurdando home")
        return home
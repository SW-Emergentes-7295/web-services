# iam/domain/user.py

class User:
    def __init__(self, id=None, name='', email='', phone='', password=''):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

    def to_dict(self):
        return {
            "Id": self.id,
            "Name": self.name,
            "Email": self.email,
            "Phone": self.phone
        }

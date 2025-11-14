import random, string
from configuration_preferences.infrastructure.link_repository import LinkRepository

class LinkServiceDB:
    def __init__(self, repo=None):
        self.repo = repo or LinkRepository()

    def generate_random_code(self, length=20):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    def generate_and_save_link(self, blind_user_id: str):
        if not blind_user_id:
            raise ValueError("blind_user_id es obligatorio")

        new_code = self.generate_random_code()
        self.repo.save_or_update_link(blind_user_id, new_code)

        return {
            "blind_user_id": blind_user_id,
            "link_code": new_code,
            "message": "Link autogenerado y guardado correctamente"
        }

    def get_link(self, blind_user_id: str):
        link = self.repo.get_link_by_user(blind_user_id)
        if not link:
            return {"error": "No se encontró un link para este usuario"}
        return link
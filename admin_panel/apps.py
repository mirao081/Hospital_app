from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'

<<<<<<< HEAD
=======
    def ready(self):
        import admin_panel.utils  # ens

>>>>>>> b52f04c4160118931c5fee8708ece2520ef97dcf
    
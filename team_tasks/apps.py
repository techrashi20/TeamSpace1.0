from django.apps import AppConfig

class TeamTasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team_tasks'

    def ready(self):
        import team_tasks.models  # Signals load karne ke liye
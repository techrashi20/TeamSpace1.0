from django.apps import AppConfig

class TeamAuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team_audit'

    def ready(self):
        import team_audit.signals
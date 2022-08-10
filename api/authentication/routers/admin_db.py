class AdminDBRouter:
    """
    DEPRECATED

    A router to control all database operations on models in the authentication application, all and any dependent applications, and Django administrative applications.
    """
    route_app_labels = {
        'admin',
        'auth',
        'authentication',
        'contenttypes',
        'sessions',
        'sites',
        'token_blacklist',
    }

    def db_for_read(self, model, **hints):
        """
        Attempts to read models defined in any app in 'self.route_app_labels' go to 'admin_db'.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'admin_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write models defined in any app in 'self.route_app_labels' go to 'admin_db'.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'admin_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in any app defined in 'self.route_app_labels' is involved.
        """
        if obj1._meta.app_label in self.route_app_labels or \
           obj2._meta.app_label in self.route_app_labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure any app in 'self.route_app_labels' only appears in the 'admin_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'admin_db'
        return None

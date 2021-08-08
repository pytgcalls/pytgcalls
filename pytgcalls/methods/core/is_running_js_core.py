import builtins


class IsRunningJsCore:
    # noinspection PyProtectedMember
    @staticmethod
    def is_running_js_core():
        return len([
            instance for instance in builtins.client_instances
            if instance._init_js_core
        ]) > 0

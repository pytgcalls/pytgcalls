from ..core import env


class IsRunningJsCore:
    # noinspection PyProtectedMember
    @staticmethod
    def is_running_js_core():
        return len([
            instance for instance in env.client_instances
            if instance._init_js_core
        ]) > 0

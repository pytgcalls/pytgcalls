import psutil


class GetMaxVoiceChat:
    # noinspection PyProtectedMember
    @staticmethod
    def get_max_voice_chat(consumption=5):
        core_count = psutil.cpu_count()
        return int((100 / consumption) * core_count)

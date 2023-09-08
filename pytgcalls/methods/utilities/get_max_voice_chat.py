import psutil

from ...scaffold import Scaffold


class GetMaxVoiceChat(Scaffold):
    @staticmethod
    def get_max_voice_chat(consumption=5):
        core_count = psutil.cpu_count()
        return int((100 / consumption) * core_count)

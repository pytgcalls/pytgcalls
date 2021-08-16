from ...scaffold import Scaffold


class ActiveCalls(Scaffold):
    @property
    def active_calls(self):
        return self._call_holder.active_calls

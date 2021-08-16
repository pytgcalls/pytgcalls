from ...scaffold import Scaffold


class Calls(Scaffold):
    @property
    def calls(self):
        return self._call_holder.calls

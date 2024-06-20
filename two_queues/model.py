from background import run_in_background, background_task
from atom.api import *
import time
import uuid

from enaml.application import deferred_call


class Model(Atom):
    result: str
    result_2: str

    def do_it(self) -> None:
        def _do_it():
            time.sleep(2)
            deferred_call(setattr, self, 'result', str(uuid.uuid4().hex))

        run_in_background(_do_it)

    @background_task
    def do_it_2(self) -> None:
        time.sleep(2)
        deferred_call(setattr, self, 'result_2', str(uuid.uuid4().hex))

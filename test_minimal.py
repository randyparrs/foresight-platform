# { "Depends": "py-genlayer:1j12s63yfjpva9ik2xgnffgrs6v44y1f52jvj9w7xvdn7qckd379" }

from genlayer import *


class TestZero(gl.Contract):

    def __init__(self):
        pass

    @gl.public.view
    def hello(self) -> str:
        return "world"

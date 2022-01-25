from .baseprocessor import BaseProcessor


class COGNET360KProcessor(BaseProcessor):
    def __init__(self, node_lut, relation_lut):
        super().__init__("COGNET360K", node_lut, relation_lut)

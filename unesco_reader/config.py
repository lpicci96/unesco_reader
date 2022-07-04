""" """
import os
import pandas as pd
from dataclasses import dataclass, field


class Paths:
    def __init__(self, project_dir):
        self.project_dir = project_dir

    @property
    def data(self):
        return os.path.join(self.project_dir, "unesco_reader", "data")

    @property
    def glossaries(self):
        return os.path.join(self.project_dir, "unesco_reader", "glossaries")


PATHS = Paths(os.path.dirname(os.path.dirname(__file__)))






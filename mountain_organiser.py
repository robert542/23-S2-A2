from __future__ import annotations

from mountain import Mountain
from infinite_hash_table import InfiniteHashTable

class MountainOrganiser:

    def __init__(self) -> None:
        self.mountains = InfiniteHashTable()

    def cur_position(self, mountain: Mountain) -> int:
        keys = self.mountains.sort_keys()
        for i in range(len(keys)):
            if keys[i] == mountain.name:
                return i

    def add_mountains(self, mountains: list[Mountain]) -> None:
        for mountain in mountains:
            self.mountains[mountain.name] = mountain

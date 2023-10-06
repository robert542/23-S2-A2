from __future__ import annotations
from mountain import Mountain

from double_key_table import DoubleKeyTable

class MountainManager:

    def __init__(self) -> None:
        self.mountains = DoubleKeyTable()

    def add_mountain(self, mountain: Mountain) -> None:
        key = (str(mountain.difficulty_level), mountain.name)
        self.mountains[key] = mountain

    def remove_mountain(self, mountain: Mountain) -> None:
        key = (str(mountain.difficulty_level), mountain.name)
        del self.mountains[key]

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        self.remove_mountain(old)
        self.add_mountain(new)

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        diff_mounts = self.mountains.keys(str(diff))
        res = []
        for value in diff_mounts:
            res.append(self.mountains[(str(diff), value)])
        return res
                


    def group_by_difficulty(self) -> list[list[Mountain]]:
        upper_diffs = self.mountains.keys()
        change = lambda x: int(x)
        upper_diffs = [change(i) for i in upper_diffs]
        upper_diffs.sort()
        res = []
        for diff in upper_diffs:
            res.append(self.mountains_with_difficulty(diff))
        return res
        

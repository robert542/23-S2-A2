from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

from personality import PersonalityDecision

from mountain_manager import MountainManager

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Trail
    bottom: Trail
    following: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.following.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Removing the mountain at the beginning of this series.
        """
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain in series before the current one.
        """
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        return TrailSplit(Trail(None), Trail(None), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        new_following = Trail(TrailSeries(mountain, self.following))
        return TrailSeries(self.mountain, new_following)

    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        new_series_following = Trail(TrailSplit(Trail(None), Trail(None), self.following))
        return TrailSeries(self.mountain, new_series_following)

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None
    difficulty_data: MountainManager|None = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return Trail(TrailSplit(Trail(None), Trail(None), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""

        #holds all paths that have not been recescted
        bank = []
        active = self
        #keeps running while the trail type is not None or there is still something in the bank
        while active.store != None or len(bank)==0:
            #handles when a series is active
            if isinstance(active.store, TrailSeries):
                personality.add_mountain(active.store.mountain)
                active = active.store.following
            #handles when a split is active

            if active.store == None:
                active = bank.pop(0)

            else:
                #finds the path choice
                choice = personality.select_branch(active.store.top, active.store.bottom)
                #breaks if the choice is to stop
                if choice == PersonalityDecision.STOP:
                    break
                #returns the top or bottom path, does not really matter which choice
                if choice == PersonalityDecision.TOP:
                    branch = active.store.top
                else:
                    branch = active.store.bottom
                #adds the eventual reconnection to the bank
                bank.append(active.store.following)
                active = branch.store
                

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        res = []
        if self.store == None:
            return res
        if type(self.store) is type(TrailSplit):
            deal_with = [self.store.top, self.store.bottom]
            for trail in deal_with:
                res += trail.collect_all_mountains()
        else:
            if self.store.mountain is not None:
                res.append(self.store.mountain)
        
        res += self.store.following.collect_all_mountains()

        return res

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        raise NotImplementedError()

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()

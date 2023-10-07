from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self, daddy_table: InfiniteHashTable|None = None) -> None:
        self.array:ArrayR[tuple[K,V|InfiniteHashTable]] = ArrayR(self.TABLE_SIZE)
        self.count = 0
        if daddy_table is None:
            self.level = 0
        else:
            self.level = daddy_table.get_level + 1

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1
    
    @property
    def get_level(self) -> int:
        return self.level

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        position = self.get_location(key)

        if len(position) == 1:
            element = self.array[position[0]]
            if element is None:
                raise KeyError(key)
            return element[1]
        else:
            return self.array[position[0]][1].__getitem__(key)
        

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        position = self.get_location(key)
        local_pos = position[0]
        key_match = key == self.array[local_pos][0]

        if len(position) !=  1:
            self.array[local_pos][1].__setitem__(key, value)
        
        elif self.array[local_pos] is None or key_match:
            self.array[local_pos] = (key, value)
            if not key_match:
                self.count +=1
        
        else:
            pair_1 = (key, value)
            pair_2 = self.array[local_pos]
            new_table = InfiniteHashTable(daddy_table=self)
            new_key = key[0:self.level+1]
            self.array[local_pos] = (new_key, new_table)
            self.array[local_pos][1].__setitem__(pair_2[0], pair_2[1])
            self.array[local_pos][1].__setitem__(pair_1[0], pair_1[1])

            

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        position = self.get_location(key)
        local_pos = position[0]

        if len(position) == 1:
            if self.array[local_pos] is None:
                raise KeyError(key)
            self.array[local_pos] = None
            self.count -= 1

        else:
            self.array[local_pos][1].__delitem__(key)
            
            if len(self.array[local_pos][1]) == 1 and len(self.array[local_pos][1].values()) > 0:
                remaining_key = self.array[local_pos][1].keys()[0]
                remaining_value = self.array[local_pos][1].__getitem__(remaining_key)
                self.array[local_pos] = (remaining_key, remaining_value)


    def __len__(self) -> int:
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()

    def get_location(self, key) -> list[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        position = self.hash(key)

        if self.array[position] is None or not isinstance(self.array[position][1], InfiniteHashTable):
            return [position]
        else:
            lower_position = self.array[position][1].get_location(key)
            return [position]+lower_position


    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        return True
        
    def keys(self) -> list[K]:

        res = []
        for x in self.array:
            if x is not None:
                    res.append(x[0])
        return res
        

    def values(self) -> list[V]:

        res = []
        for x in self.array:
            if x is not None:
                if not isinstance(x[1],InfiniteHashTable):
                    res.append(x[1])
        return res

    def sort_keys(self) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        """
        res = []

        for i in self.array:
            if i is not None:
                if isinstance(i[1],InfiniteHashTable):
                    res.append(i[0])
                else:
                    res = res + i[1].sort_keys()
        return res


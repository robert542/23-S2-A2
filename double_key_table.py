from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        #check if there are other Table sizes defined for the external table
        if sizes is not None:
            self.TABLE_SIZES = sizes

        self.size_index = 0
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0
        self.internal_sizes = internal_sizes



    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        position = self.hash1(key1)

        for _ in range(self.table_size):
            #if a position is empty
            if self.array[position] is None:
                #if you are looking for an index to insert at
                if is_insert:
                    #make a new internal hash table so there is a place with the given internal table specs
                    new_table = LinearProbeTable(self.internal_sizes)
                    #change the hash method to be hash2 from this class instead of the default for linprob object
                    new_table.hash = lambda k: self.hash2(k, new_table)
                    #place in empty index with external key
                    self.array[position] = (key1, new_table)
                    self.count += 1
                    #get the internal position in the new table
                    internal = self.array[position][1].hash(key2)
                    return (position, internal)
                else:
                    raise KeyError(key1)
            #if its not none, then a tuple is stored
            elif self.array[position][0] == key1:
                #get the internal hash table
                table = self.array[position][1]
                #if you are not inserting
                if not is_insert:
                    table_info = table.table_state()
                else:
                    table[key2] = key2
                    table_info = table.table_state()
                    del table[key2]
                #get underlying array data
                #check for where key is placed
                for i in range(len(table_info)):
                    if table_info[i] is not None:
                        if table_info[i][0] == key2:
                            return (position, i)
                #if key is not there, then wrong key was input
                raise KeyError(key2)
            else:
                position = (position + 1) % self.table_size

        if is_insert:
            raise FullError("The outer table is full!")
        else:
            raise KeyError(key1)



    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for entry in self.array:
                if entry is not None:
                    yield entry[0]
        else:
            position = self.hash1(key)
            for _ in range(self.table_size):
                if self.array[position] is not None and self.array[position][0] == key:
                    for sub_key in self.array[position][1].keys():
                        yield sub_key
                    return
                position = (position + 1) % self.table_size
            raise KeyError(f"Key {key} not found")

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        if key is None:
            res = []
            for x in range(self.table_size):
                if self.array[x] is not None:
                    res.append(self.array[x][0])
            return res
        
        position = self.hash1(key)
        for i in range(self.table_size):
            if self.array[i] is not None:
                if self.array[i][0] is key:
                    return self.array[1].keys()
            position = (position+1) % self.table_size

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            for entry in self.array:
                if entry is not None:
                    for value in entry[1].values():
                        yield value
        else:
            position = self.hash1(key)
            for _ in range(self.table_size):
                if self.array[position] is not None and self.array[position][0] == key:
                    for value in self.array[position][1].values():
                        yield value
                    return
                position = (position + 1) % self.table_size
            raise KeyError(f"Key {key} not found")

    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        if key is None:
            res = []
            for x in range(self.table_size):
                if self.array[x] is not None:
                    res.append(self.array[x][1].values())
            return res
        
        position = self.hash1(key)
        for i in range(self.table_size):
            if self.array[i] is not None:
                if self.array[i][0] is key:
                    return self.array[1].values()
            position = (position+1) % self.table_size

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        position = self._linear_probe(key[0], key[1], False)
        table = self.array[position][1]
        value = table[key[1]]
        return value


    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        position = self._linear_probe(key[0], key[1], True)

        self.array[position[0]][1][key[1]] = data

        if len(self) > self.table_size / 2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        position = self._linear_probe(key[0], key[1], False)
        # Remove the element
        del self.array[position[0]][1][key[1]]

        if len(self.array[position[0]][1]) == 0:
            self.array[position[0]] = None
            self.count -= 1
            # Start moving over the cluster
            position = (position[0] + 1) % self.table_size
            while self.array[position] is not None:
                value_key, value = self.array[position]
                self.array[position] = None
                # Reinsert.
                newpos = self._linear_probe(value_key, True)
                self.array[newpos] = (value_key, value)
                position = (position + 1) % self.table_size

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.array
        self.size_index += 1
        if self.size_index == len(self.TABLE_SIZES):
            # Cannot be resized further.
            return
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0
        for item in old_array:
            if item is not None:
                key, value = item
                self[key] = value

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return self.TABLE_SIZES[self.size_index]

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()

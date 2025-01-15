# ref: https://stackoverflow.com/questions/2703599/what-would-a-frozen-dict-be
class FrozenDict(dict):
    def __init__(self, *args, **kwargs):
        self._hash = None
        super(FrozenDict, self).__init__(*args, **kwargs)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(tuple(sorted(self.items())))
        return self._hash

    def _immutable(self, *args, **kwargs):
        raise TypeError('cannot change immutable FrozenDict')

    # make copying a lot more efficient
    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        if memo is not None:
            memo[id(self)] = self
        return self

    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    


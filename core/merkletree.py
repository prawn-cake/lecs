# -*- coding: utf-8 -*-
import math
import codecs
import functools


def str_to_hex(s: str) -> bytes:
    """Convert a string to its' hex representation

    >>> str_to_hex('hello world')
    >>> b'68656c6c6f20776f726c64'

    """
    return codecs.encode(s.encode(), 'hex')


class MerkleTree(object):
    """Simple Merkle tree implementation

    >>> tree = MerkleTree.empty(size=2 ** 4)
    >>> tree.add_element(1)
    >>> tree.add_element(2)
    >>> tree.add_element(7)

    >>> trace = tree.trace(2)
    """

    def __init__(self, struct: list):
        self._tree = struct
        # NOTE: Keep a counter for the last taken data slot in the data layer
        self._last_idx = -1

    @property
    def root(self):
        return self._tree[0][0]

    @property
    def depth(self):
        return len(self._tree)

    @staticmethod
    def empty(size: int):
        """Create an empty tree with the given size

        """
        num_of_rows = math.log2(size)
        if num_of_rows % 1 != 0:
            raise ValueError('Size of the tree must be equal the power of 2, '
                             'e.g 4, 8, 16, 32, etc')
        struct = []
        for x in range(int(num_of_rows) + 1):
            struct.append([None] * 2 ** x)

        return MerkleTree(struct=struct)

    def add_element(self, el):
        data_layer = self._tree[self.depth - 1]
        new_layer = data_layer[:]
        if self._last_idx + 1 > len(data_layer):
            raise ValueError('The tree is full. Max %d elements'
                             % len(data_layer))

        node = (self._last_idx + 1, el)
        new_layer[self._last_idx + 1] = node

        self._tree[-1] = new_layer
        self._last_idx += 1
        self.sift_up(row=self.depth - 1, column=node[1])

    @staticmethod
    def calc_hash(val):
        """Hashing method implementation
        """
        return str(val)

    def sift_up(self, row: int, column: int):
        """Sift up a tree from the element with the given coordinates

        :param row: row of the element
        :param column: column of the element
        """
        parent_coord = self.get_parent_of(row, column)
        parent_row, parent_col = parent_coord

        # NOTE: This could be done via get_neighbor_of method
        children_coord = self.get_children_of(*parent_coord)
        children = [self.val(*coord) for coord in children_coord]

        left_child = children[0][1] if isinstance(children[0], tuple) \
            else str(children[0])

        # tuple represents a data layer value
        if isinstance(children[1], tuple):
            right_child = children[1][1]
        elif isinstance(children[1], str):
            right_child = children[1]
        else:
            right_child = left_child

        values = map(self.calc_hash, [left_child, right_child])
        self._tree[parent_row][parent_col] = ''.join(values)

        if parent_row - 1 >= 0:
            self.sift_up(*parent_coord)

    @staticmethod
    def get_children_of(row, column):
        return [(row + 1, 2 * column), (row + 1, 2 * column + 1)]

    @staticmethod
    def get_parent_of(row: int, column: int):
        parent_col = divmod(column, 2)[0]
        return row - 1, parent_col

    def val(self, row: int, column: int):
        """Tree value getter
        """
        return self._tree[row][column]

    @staticmethod
    def get_neighbor(row: int, column: int):
        """If it's a right node, then return a left one and vice versa
        Column is always a right one if its' modulo by 2 == 0.
        """

        # Root node case, it doesn't have a neighbor
        if (row, column) == (0, 0):
            return 0, 0

        if (column + 1) % 2 == 0:
            return row, column - 1
        return row, column + 1

    def trace(self, data_id):
        """Verify that some data id is present in the block

        :param data_id: some data id
        """
        data_layer = self._tree[self.depth - 1]
        data_idx = None

        # FIXME: here data id is a transaction id or its' hash value
        for i, (idx, val) in enumerate(data_layer):
            if val == data_id:
                data_idx = i
                break

        # data_id is not presented in the block
        if data_idx is None:
            return []

        neighbor_coord = self.get_neighbor(row=self.depth - 1, column=data_idx)
        cur = self.val(*neighbor_coord)

        # Extract value (hash) from data layer tuple node
        # NOTE: We prefix a hash with '-' to indicate that the neighbor is from
        # the right side to give verification function some order information
        trace = [str(cur[1]) if neighbor_coord[1] > data_idx else '-' + str(cur[1])]

        while cur != self.root:
            parent_coord = self.get_parent_of(*neighbor_coord)
            neighbor_coord = self.get_neighbor(*parent_coord)
            cur = self.val(*neighbor_coord)

            # Root case
            if parent_coord == (0, 0):
                trace.append(cur)
            else:
                # NOTE: Same idea as above, we want to save order info
                trace.append(cur if neighbor_coord > parent_coord else '-' + cur)
        return trace

    @staticmethod
    def verify(data_id, trace: list) -> bool:
        """Verification function
        NOTE: trace should contain order info (hashes starting with '-' will
        invert the hashing order)
        """
        if not trace:
            return False

        root, chain = trace[-1], trace[:-1]

        def reducer(acc, val):
            if str(val).startswith('-'):
                return str(val)[1:] + acc
            return acc + str(val)

        initial = str(data_id)
        res = functools.reduce(reducer, chain, initial)
        return res == root

    def traverse(self):
        for i, row in enumerate(self._tree):
            yield i, row


if __name__ == '__main__':
    i = 3
    num_of_elements = 2 ** i

    tree = MerkleTree.empty(size=num_of_elements)
    elements = list(range(8))  # 0-8

    for el in elements:
        tree.add_element(el)
        for i, layer in tree.traverse():
            print('[%d] %d: %s' % (i, len(layer), layer))
        print('\n')

    for i, layer in tree.traverse():
        print('[%d] %d: %s' % (i, len(layer), layer))

    tv = tree.val
    assert [tv(*c) for c in tree.get_children_of(2, 0)] == [(0, 0), (1, 1)]
    assert [tv(*c) for c in tree.get_children_of(2, 1)] == [(2, 2), (3, 3)]
    assert [tv(*c) for c in tree.get_children_of(2, 2)] == [(4, 4), (5, 5)]
    assert [tv(*c) for c in tree.get_children_of(2, 3)] == [(6, 6), (7, 7)]

    assert tree.root == '01234567'

    assert tv(*tree.get_neighbor(row=3, column=0)) == (1, 1)
    assert tv(*tree.get_neighbor(row=3, column=1)) == (0, 0)

    # The neighbor of the root is a root itself
    assert tv(*tree.get_neighbor(0, 0)) == tree.root == '01234567'

    assert tree.trace(1) == ['-0', '23', '4567', '01234567']
    assert tree.trace(7) == ['-6', '-45', '-0123', '01234567']

    assert tree.verify(data_id=7, trace=tree.trace(7)) is True
    assert tree.verify(data_id=8, trace=tree.trace(8)) is False
    assert tree.verify(data_id=None, trace=tree.trace(8)) is False

    # Check # non-existing value
    assert tree.trace(10) == []
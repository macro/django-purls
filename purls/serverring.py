"""
Provides:
    ServerRing - An implementation of a consistent hash ring.
"""
import hashlib


class ServerRing(object):
    """
    A consistent hash ring.

    Based on http://pypi.python.org/pypi/hash_ring/
    with a some enhancements and cleanup.
    """
    def __init__(self, nodes=None, replicas=3, hashfunc=None):
        """
        Manages a hash ring.

        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
                replicas are required to improve the distribution.
        `hashfunc` is a function that creates hash objects (ex. hashlib.sha1)
                if hashfunc is not given, sha1 is used.
        """
        if hashfunc is None:
            self.hashfunc = hashlib.sha1
        self.replicas = replicas
        self.ring = dict()
        self._sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def gen_key(self, key):
        """
        Given a string key it returns a long value, this long value represents
        a place on the hash ring.
        """
        h = self.hashfunc()
        h.update(key)
        return long(h.hexdigest(), 16)

    def add_node(self, node):
        """
        Adds a `node` to the hash ring (including a number of replicas).
        """
        for i in xrange(self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            self.ring[key] = node
            self._sorted_keys.append(key)
        self._sorted_keys.sort()

    def remove_node(self, node):
        """
        Removes `node` from the hash ring and its replicas.
        """
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)

    def get_node(self, string_key):
        """
        Given a string key a corresponding node in the hash ring is returned.
        If the hash ring is empty, `None` is returned.
        """
        return self.get_node_pos(string_key)[0]

    def get_node_pos(self, string_key):
        """
        Given a string key a corresponding node in the hash ring is returned
        along with its position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        """
        if not self.ring:
            return None, None
        key = self.gen_key(string_key)
        nodes = self._sorted_keys
        for i,node in enumerate(nodes):
            if key <= node:
                return self.ring[node], i
        return self.ring[nodes[0]], 0



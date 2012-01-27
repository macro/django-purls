"""
Tests for ServerRing.
"""

import unittest

from purls.serverring import ServerRing


class ServerRingTestCase(unittest.TestCase):
    def _create_random_word_gen(self, n=3,m=8):
        import random
        def random_word_gen(n, m):
            ALPHA = tuple(chr(i) for i in xrange(97,123))
            alpha_sz = len(ALPHA)
            while True:
                yield ''.join(ALPHA[random.randint(0, alpha_sz - 1)]
                        for i in xrange(random.randint(n, m)))
        return random_word_gen(n, m)

    def test_consistency(self):
        """
        Assert the same node is returned by `get_node()` for a given key.
        """
        servers = ('http://asset0.example.com',
                'http://asset1.example.com',
                'http://asset2.example.com',
                'http://asset3.example.com')
        hr = ServerRing(servers)
        random_word_gen = self._create_random_word_gen()
        urls_by_path = dict()
        for i in xrange(100):
            path = '/images/%s/%s.png' % (random_word_gen.next(), random_word_gen.next())
            server = hr.get_node(path)
            urls_by_path[path] = ''.join((server, path))
        for path in urls_by_path:
            url = ''.join((hr.get_node(path), path))
            self.assertEqual(urls_by_path[path], url)

    def test_remove_node(self):
        """
        Assert `get_node()` returns the same node for a given key
        when a node is removed.
        """
        servers = ('http://asset0.example.com',
                'http://asset1.example.com',
                'http://asset2.example.com',
                'http://asset3.example.com')
        hr = ServerRing(servers)
        random_word_gen = self._create_random_word_gen()
        urls_by_serverpath = dict()
        for i in xrange(100):
            path = '/images/%s/%s.png' % (random_word_gen.next(), random_word_gen.next())
            server = hr.get_node(path)
            urls_by_serverpath[(server,path)] = ''.join((server, path))
        removed_server = servers[2]
        hr.remove_node(removed_server)
        for server,path in urls_by_serverpath:
            if server == removed_server:
                continue
            s = hr.get_node(path)
            self.assertEqual(server, s)

    def test_add_node(self):
        """
        Assert `get_node()` returns the same node for a given key
        when a node is added.
        """
        import collections
        servers = ('http://asset0.example.com',
                'http://asset1.example.com',
                'http://asset3.example.com')
        hr = ServerRing(servers)
        random_word_gen = self._create_random_word_gen()
        urls_by_serverpath = dict()
        for i in xrange(100):
            path = '/images/%s/%s.png' % (random_word_gen.next(), random_word_gen.next())
            server = hr.get_node(path)
            urls_by_serverpath[(server,path)] = ''.join((server, path))
        # check new server has entries 'rebalanced'
        new_server = 'http://asset2.example.com'
        hr.add_node(new_server)
        counts_by_server = collections.defaultdict(int)
        for server,path in urls_by_serverpath:
            counts_by_server[hr.get_node(path)] += 1
        # assert new node has entries
        self.assertTrue(counts_by_server[new_server] > 0)

    def test_empty_ring(self):
        """
        Assert `get_node()` returns None for all keys
        when ServerRing is empty.
        """
        hr = ServerRing()
        random_word_gen = self._create_random_word_gen()
        for i in xrange(10):
            path = '/images/%s/%s.png' % (random_word_gen.next(), random_word_gen.next())
            server = hr.get_node(path)
            self.assertIsNone(server)


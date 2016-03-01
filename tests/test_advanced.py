# -*- coding: utf-8 -*-

from .context import smt

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        smt.myname()


if __name__ == '__main__':
    unittest.main()
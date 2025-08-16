import unittest
from app.services.matcher import Matcher

class TestMatcher(unittest.TestCase):
    def test_basic(self):
        q = ["How to reset password?", "What is refund policy?", "Where is my order?"]
        kw = [["reset password", "change password"], ["refund", "return"], ["order tracking"]]
        m = Matcher(q, kw)
        ranked = m.score_all("I forgot my password")
        self.assertEqual(ranked[0][0], 0)

if __name__ == '__main__':
    unittest.main()

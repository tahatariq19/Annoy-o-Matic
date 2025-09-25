import unittest
from main import parse_emojis

class TestEmojiParser(unittest.TestCase):

    def test_parse_emojis(self):
        # Test with standard Unicode emojis
        self.assertEqual(parse_emojis("😂, 👍, ❤️"), ["😂", "👍", "❤"])

        # Test with custom Discord emojis
        self.assertEqual(parse_emojis("<:custom:123>"), ["<:custom:123>"])

        # Test with a mix of both
        self.assertEqual(parse_emojis("😂, <:custom:123>, 👍"), ["😂", "<:custom:123>", "👍"])
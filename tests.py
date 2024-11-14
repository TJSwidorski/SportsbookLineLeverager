
import unittest
import sports

class TestBetTypes(unittest.TestCase):
    def setUp(self):
        # Initialize a common base_url and date_type for test cases
        self.base_url = "https://www.sportsbookreview.com/betting-odds/nfl-football/?week=Week"
        self.week = "10"
        self.bet_types = sports.BetTypes(self.base_url, self.week)

    def test_spread_url(self):
        # Test the URL generated for the spread bet type
        expected_url = "https://www.sportsbookreview.com/betting-odds/nfl-football/pointspread/full-game/?week=Week10"
        self.assertEqual(self.bet_types.spread, expected_url)

    def test_money_line_url(self):
        # Test the URL generated for the money line bet type
        expected_url = "https://www.sportsbookreview.com/betting-odds/nfl-football/money-line/full-game/?week=Week10"
        self.assertEqual(self.bet_types.money_line, expected_url)

    def test_totals_url(self):
        # Test the URL generated for the totals bet type
        expected_url = "https://www.sportsbookreview.com/betting-odds/nfl-football/totals/full-game/?week=Week10"
        self.assertEqual(self.bet_types.totals, expected_url)

    def test_quarters_url(self):
        # Test quarter-specific URLs
        # Testing the 1st quarter
        spread, money_line, totals = self.bet_types.quarters(1)
        expected_spread = "https://www.sportsbookreview.com/betting-odds/nfl-football/pointspread/1st-quarter/?week=Week10"
        expected_money_line = "https://www.sportsbookreview.com/betting-odds/nfl-football/money-line/1st-quarter/?week=Week10"
        expected_totals = "https://www.sportsbookreview.com/betting-odds/nfl-football/totals/1st-quarter/?week=Week10"
        self.assertEqual(spread, expected_spread)
        self.assertEqual(money_line, expected_money_line)
        self.assertEqual(totals, expected_totals)

if __name__ == "__main__":
    unittest.main()
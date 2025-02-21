import pandas as pd

class Package():
  """
  Packages Sportsbook line data so it can be processed
  in Neural Networks and other machine learning programs.
  """
  def __init__(self, df, true_prob = True):
    """
    Takes a DataFrame of sportsbetting data and converts
    the american sportsbook lines into true probability and
    converts the scores into Win/Loss representations.
    """
    self.df = df.dropna()
    self.away_df = None
    self.home_df = None
    if true_prob:
      self.to_values()
    else:
      self.to_nb_values()

  def implied_prob(self, line):
    """
    Returns an american sportsbook line as it's implied probability.
    """
    sign = line[0]
    odds = line[1:]

    if sign == "+":
      num = 100
      den = 100 + int(odds)
    elif sign == '-':
      num = int(odds)
      den = 100 + int(odds)
    else:
      raise ValueError("Invalid odds sign. Must be '+' or '-'.", line)
    
    return num / den

  def true_prob(self, away, home):
    """
    Returns the true probability of an away and home american
    sportsbook line by removing the vig from both implied probabilities.
    """
    away_ip = self.implied_prob(away)
    home_ip = self.implied_prob(home)

    vig = (home_ip + away_ip) - 1

    away_prob = round(away_ip - (0.5 * vig), 4)
    home_prob = round(home_ip - (0.5 * vig), 4)

    return away_prob, home_prob
  
  def win_loss(self, scores):
    """
    Given scores, converts the home and away scores into
    a 1 for a win and a 0 for a loss. In the case of a tie,
    returns None for both scores.
    """
    away_score, home_score = map(int, scores)
    if home_score > away_score:
      return 0, 1
    elif home_score < away_score:
      return 1, 0
    else:
      return None, None

  def to_values(self):
    """
    Takes a df of american sportsbook lines and game scores
    and converts the lines into true probabilites and the scores
    into a 1 for a win and a 0 for a loss. 
    """
    #Initialize the end arrays
    away_lines_array = []
    home_lines_array = []
    away_scores_array = []
    home_scores_array = []

    for _, val in self.df.iterrows():
      #Get the away and home lines
      away_lines = val['Away Lines']
      home_lines = val['Home Lines']
      #Set the away and home arrays for the current game
      away_array = []
      home_array = []

      #Get the away and home scores
      away_score = val['Away Score']
      home_score = val['Home Score']

      #Calculate probabilities
      for away, home in zip(away_lines, home_lines):
        away_tp, home_tp = self.true_prob(away, home)
        assert away_tp + home_tp == 1, "Incorrect True Probability Calculation"
        away_array.append(away_tp)
        home_array.append(home_tp)

      away_lines_array.append(away_array)
      home_lines_array.append(home_array)

      #Calculate Win/Loss
      a, h = self.win_loss([away_score, home_score])
      away_scores_array.append(a)
      home_scores_array.append(h)

    #Update df
    self.df['Away Odds'] = away_lines_array
    self.df['Home Odds'] = home_lines_array
    del self.df['Away Lines']
    del self.df['Home Lines']
    self.df['Away W/L'] = away_scores_array
    self.df['Home W/L'] = home_scores_array
    del self.df['Away Score']
    del self.df['Home Score']

  def to_nb_values(self):
    """
    Takes a df of american sportsbook lines and game scores
    and converts the scores into a 1 for a win and a 0 for a loss.

    Packages the data into independent home and away dataframes. 
    """
    #Initialize the end arrays
    away_lines_array = []
    home_lines_array = []
    away_scores_array = []
    home_scores_array = []

    for _, val in self.df.iterrows():
      #Get the away and home lines
      away_lines = val['Away Lines']
      home_lines = val['Home Lines']

      #Get the away and home scores
      away_score = val['Away Score']
      home_score = val['Home Score']

      away_lines_array.append(away_lines)
      home_lines_array.append(home_lines)

      #Calculate Win/Loss
      a, h = self.win_loss([away_score, home_score])
      away_scores_array.append(a)
      home_scores_array.append(h)

    #Update df
    self.away_df = pd.DataFrame(columns=['Away Lines', 'Away W/L'])
    self.away_df['Away Lines'] = away_lines_array
    self.away_df['Away W/L'] = away_scores_array
    self.home_df = pd.DataFrame(columns=['Home Lines', 'Home W/L'])
    self.home_df['Home Lines'] = home_lines_array
    self.home_df['Home W/L'] = home_scores_array

  def return_df(self):
    """
    Returns the current DataFrame.
    """
    return self.df
  
  def return_away(self):
    """
    Returns the away DataFrame if created.

    Returns None if the DataFrame is not created.
    """
    return self.away_df
  
  def return_home(self):
    """
    Returns the home DataFrame if created.

    Returns None if the DataFrame is not created.
    """
    return self.home_df
import requests
from bs4 import BeautifulSoup
import pandas as pd

class MoneyLineAPI():
  """
  A class for retrieving all the data from Money Line links within
  Sportsbook Review.
  """
  def __init__(self, date_type: str, date, data, scores):
    """
    Given parsed html data [soup], extract the relevant information
    determined by if the sport is a weekly or daily [date_type] sport.
    """
    #Properly format the date_type
    self.date_type = date_type.lower().capitalize()
    #Identify the scores indices according to the date_type
    indices_dict = {
      'Week': [3, 4],
      'Date': [2, 3]
    }
    #Initialize scores indices based on the date_type
    self.scores_indices = indices_dict[self.date_type]
    #Set the date
    if isinstance(date, int):
      self.date = "Week " + str(date)
    else:
      self.date = date
    #Clean the data
    self.data = self.clean_data(data)
    #Clean the scores
    self.scores = self.clean_scores(scores)

  def clean_data(self, data):
    """
    Given raw-data [data], return a list of games where each game is a
    dictionary containing three columns: 'Date_type', 'Away Lines', and
    'Home Lines'. 
    """
    #Create the games list and game_info dictionary
    games = []
    game_info = {}
    index = 0

    while index < len(data):
      #Indicates the index location is a date/time string
      if "PM" in data[index] or "AM" in data[index]:
        #Add the game_info to the games list
        if game_info:
          games.append(game_info)
        #Initialize the new game_info
        game_info = {
          #Set the date title as "Week _" or the actual date "Yr-Mo-Day"
          self.date_type: self.date, 
          #Set the Lines list
          "Lines": []
        }
      #Indicates an empty or missing value
      elif data[index] == "-":
        #Skip this index location
        index += 1
        continue
      #Indicates the index location is an american-odds sportsbook line
      elif "+" in data[index] or "-" in data[index]:
        #Append the line onto the Lines list
        game_info["Lines"].append(data[index])
      #Move to the next index
      index += 1

    #If the game_info has been created, add the game to the games list
    if game_info:
      games.append(game_info)
    
    #Split the Lines list into home and away lines
    for game in games:
      game['Away Lines'] = []
      game['Home Lines'] = []
      for x in range(len(game["Lines"])):
        #Away lines are even indeces
        if x % 2 == 0:
          game['Away Lines'].append(game["Lines"][x])
        #Home lines are odd indeces
        else:
          game['Home Lines'].append(game["Lines"][x])
      #Delete the original Lines list
      del game['Lines']

    #Return the list of all games for this date as a list of game_dicts
    return games
  
  def find(self, element, data):
    """
    A helper function for clean_scores.

    Takes a list of two values [element] and finds the first instance of the
    element in the data [data]. If the element is not found in the data,
    returns None.
    """
    ele_len = len(element)
    data_len = len(data)

    i = 0
    #Set the bounds to avoid out-of-bounds error
    while i < (data_len - ele_len):
      #Check if the element matches the data at the current index
      currElem = [str(data[i]), str(data[i+1])]
      if currElem == element:
        return i
      i += 1

    return None
  
  def clean_scores(self, scores_data):
    """
    Given raw-data [scores_data], return a list of scores for each game
    on the given date. 
    """
    #Set the indices from the indices_dict
    first_index = self.scores_indices[0]
    second_index = self.scores_indices[1]
    #Create the scores list
    scores = []
    game_index = 0
    #Set the first score 
    first_score = [scores_data[first_index], scores_data[second_index]]
    #Update the data
    data = scores_data[second_index+1:]
    #Add the first score to the scores list
    scores.append(first_score)

    while True:
      #Determine if the game isn't recorded 
      #['0', '0'] indicates the game didn't take place
      if (scores[game_index] == ['0', '0']):
        #Find the next score
        for index, string in enumerate(data):
          #Find wagers indices
          if "%" in string:
            i = index
            #Set next score
            next_score = [data[i+3], data[i+4]]
            #Update the data
            data = data[i+5:]
            #Remove the inactive score
            scores.remove(['0', '0'])
            #Add the new score
            scores.append(next_score)
            break
        #Move to the next index
        continue
    
      #Find the current score in the data
      i = self.find(scores[game_index], data)
      #If the score is found, update the data and the scores list
      if (i != None) and (("%" in data[i+2]) or ("-" in data[i+2])):
        if (len(data) > 3):
          i += 4
          if (i+3) > len(data):
            break
          else:
            next_score = [data[i+1], data[i+2]] 
            data = data[i+3:]
            scores.append(next_score)
            game_index += 1
        else:
          break
      elif i != None:
        data = data[i+1:]
      else:
        print("Score causing error:", scores)
        print("Data:", data)
        raise ValueError(self.date)
    
    return scores
  
  def package(self):
    """
    Organizes the data into a DataFrame by combining the Line data and
    the scores data.
    """
    df = pd.DataFrame(self.data, 
                      columns=[self.date_type, 'Away Lines', 'Home Lines'])
    
    scores_df = pd.DataFrame(self.scores, 
                             columns=['Away Score', 'Home Score'])
    
    df.reset_index(drop=True, inplace=True)
    scores_df.reset_index(drop=True, inplace=True)

    df = pd.concat([df, scores_df], axis=1)
    return df


class PointSpreadAPI():
  pass


class TotalsAPI():
  pass


class SportsbookReviewAPI():
  """
  A class for creating a DataFrame for the specified bet type [bet_type],
  given the correct sport url, the date type which identifies the sport
  as a weekly or daily sport [date_type], and the associated date [date]
  either as an int if it is a weekly sport or as a string if it is a daily
  sport.
  """
  def __init__(self, url, bet_type: str, date_type: str, date):
    """
    Initializes the class. Web scrapes the data and scores as raw-data
    from the given website link [url], and calles the appropriate class
    given the type of bet desired [bet_type], type of sport [date_type],
    and the associated date [date]. Creates a dataframe with the data
    processed, organized, and packaged properly.
    """
    #Set the url
    self.url = url
    #Format the bet type
    self.bet_type = bet_type.lower()
    #Identify the bet type   
    bet_dict = {
      'money line': MoneyLineAPI,
      'point spread': PointSpreadAPI,
      'totals': TotalsAPI
    }
    #Format the date type
    self.date_type = date_type.lower()
    #Create parsed data
    self.soup = self.get_soup()
    #Get the data
    data = self.get_data()
    #Get the scores
    scores = self.get_scores()
    #Find the bet type and initialize the associated class
    bet_data = bet_dict[self.bet_type](self.date_type, date, data, scores)
    #Create the dataframe
    self.df = bet_data.package()


  def get_soup(self):
    """
    Sends a request to the url and parses the html content of the page.
    """
    #Send a GET request to the url
    page = requests.get(self.url)
    #Parse the HTML content of the page
    if page.status_code == 200:
      soup = BeautifulSoup(page.text, 'html.parser')
      return soup
    else:
      raise FileNotFoundError("Unable to access the url provided:", self.url)

  def get_data(self):
    """
    Retrieves the proper data from specified html <span> indicators within
    the html parsed data.
    """
    data = []
    spans = self.soup.find_all('span', class_ = 'fs-9')
    for span in spans:
      text = span.get_text(strip=True)
      if text:
        data.append(text)

    return data
  
  def get_scores(self):
    """
    Retrieves the proper score data from specified html <div> indicators
    within the html parsed data.
    """
    scores = []
    divs = self.soup.find_all('div', class_='fs-9')
    for div in divs:
      text = div.get_text(strip=True)
      if text:
        scores.append(text)
    
    return scores
  
  def return_data(self):
    """
    Returns the DataFrame created when the class was initialized.
    """
    return self.df

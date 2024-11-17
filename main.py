import sports
import retrieve
import package

if __name__ == '__main__':
  #NFL Display
  print("NFL Display")
  week = 9
  nfl = sports.NFL(week)
  df = retrieve.SportsbookReviewAPI(nfl.money_line, 'Money Line', 'Week', week).return_data()
  print(df)

  #NHL Display
  print("NHL Display")
  date = '2024-11-15'
  nhl = sports.NHL(date)
  df = retrieve.SportsbookReviewAPI(nhl.money_line, 'Money Line', 'Date', date).return_data()
  print(df)

  #NBA Display
  print("NBA Display")
  date = '2024-11-15'
  nba = sports.NBA(date)
  df = retrieve.SportsbookReviewAPI(nba.money_line, 'Money Line', 'Date', date).return_data()
  print(df)

  #Package Display
  print("NFL Packaged Data")
  week = 9
  nfl = sports.NFL(week)
  df = retrieve.SportsbookReviewAPI(nfl.money_line, 'Money Line', 'Week', week).return_data()
  pack = package.Package(df)
  df = pack.return_df()
  print(df)
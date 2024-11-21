import pandas as pd
import keras
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, accuracy_score
import sports
import retrieve
import package

#Create the combined NFL Multi-Week DataFrame
df_list = []
week = 1
while week <= 10:
  try:
    nfl = sports.NFL(week)
    df = retrieve.SportsbookReviewAPI(nfl.money_line, 'Money Line', 'Week', week).return_data()
    print("Week ", week)
    pack = package.Package(df)
    df = pack.return_df()
    df_list.append(df)
    week += 1
  except:
    print("Error")
    week += 1

df = pd.concat(df_list)

# Reset the index of the original DataFrame
df.reset_index(drop=True, inplace=True)

# Expand the lists in the Away Odds and Home Odds columns
away_odds_df = pd.DataFrame(df['Away Odds'].tolist(), columns=[f'Away_Odds_{i}' for i in range(len(df['Away Odds'].iloc[0]))])
print(away_odds_df)
home_odds_df = pd.DataFrame(df['Home Odds'].tolist(), columns=[f'Home_Odds_{i}' for i in range(len(df['Home Odds'].iloc[0]))])
print(home_odds_df)

# Concatenate the expanded odds DataFrames with the original DataFrame
df_expanded = pd.concat([df.drop(['Away Odds', 'Home Odds'], axis=1), away_odds_df, home_odds_df], axis=1)
print(df_expanded)

# Set the X and Y variables for the Home calculation
# X_home = df_expanded.drop(['Week', 'Away W/L', 'Home W/L'], axis=1)
X_home = df_expanded.filter(regex='^(?!Away_Odds|Week|Away W/L|Home W/L$).*', axis=1)
print(X_home)
y_home = df_expanded['Home W/L']
print(y_home)

# Set the X and Y variables for the Away calculation
# X_away = df_expanded.drop(['Week', 'Away W/L', 'Home W/L'], axis=1)
X_away = df_expanded.filter(regex='^(?!Home_Odds|Week|Away W/L|Home W/L$).*', axis=1)
print(X_away)
y_away = df_expanded['Away W/L']
print(y_away)

# Train test Split
Xh_train, Xh_test, yh_train, yh_test = train_test_split(X_home, y_home, test_size=0.2, random_state=42)
Xa_train, Xa_test, ya_train, ya_test = train_test_split(X_away, y_away, test_size=0.2, random_state=42)

# Fit the scaler on the training data and transform training and testing data
scaler = MinMaxScaler()
Xh_train_scaled = scaler.fit_transform(Xh_train)
Xh_test_scaled = scaler.transform(Xh_test)  # Use transform instead of fit_transform
Xa_train_scaled = scaler.fit_transform(Xa_train)
Xa_test_scaled = scaler.transform(Xa_test)  # Use transform instead of fit_transform

# Define and compile the neural network model for Home and Away predictions (same as before)
# Home model
home_model = keras.Sequential([
    keras.layers.Input(shape=(Xh_train_scaled.shape[1],)),
    keras.layers.Dense(512, activation='relu'),
    keras.layers.Dense(216, activation='relu'),
    keras.layers.Dense(1, activation='linear')
])
home_model.compile(optimizer='adam', loss=tf.keras.losses.Huber(delta=1.0))

# Away model
away_model = keras.Sequential([
    keras.layers.Input(shape=(Xa_train_scaled.shape[1],)),
    keras.layers.Dense(512, activation='relu'),
    keras.layers.Dense(216, activation='relu'),
    keras.layers.Dense(1, activation='linear')
])
away_model.compile(optimizer='adam', loss=tf.keras.losses.Huber(delta=1.0))

# Train the models
home_model.fit(Xh_train_scaled, yh_train, epochs=50, batch_size=64, validation_data=(Xh_test_scaled, yh_test))
away_model.fit(Xa_train_scaled, ya_train, epochs=50, batch_size=64, validation_data=(Xa_test_scaled, ya_test))

# Make Predictions
home_predictions = home_model.predict(Xh_test_scaled)
away_predictions = away_model.predict(Xa_test_scaled)

#Convert predictions to binary values (0 or 1)
home_predictions_binary = (home_predictions >= 0.5).astype(int)
away_predictions_binary = (away_predictions >= 0.5).astype(int)

#Create a DataFrame to display the prediction results
results_df = pd.DataFrame({
  "Week": df['Week'].iloc[Xh_test.index],
  "Actual Home W/L": yh_test,
  "Predicted Home W/L": home_predictions_binary.flatten(),
  "Predicted Home W/L Probability": home_predictions.flatten(),
  "Actual Away W/L": ya_test,
  "Predicted Away W/L": away_predictions_binary.flatten(),
  "Predicted Away W/L Probability": away_predictions.flatten(),
  "Sum": home_predictions.flatten() + away_predictions.flatten()
})
print(results_df)

#Calculate accuracy
home_accuracy = accuracy_score(yh_test, home_predictions_binary)
away_accuracy = accuracy_score(ya_test, away_predictions_binary)

# Calculate Mean Absolute Error
home_mae = mean_absolute_error(yh_test, home_predictions)
away_mae = mean_absolute_error(ya_test, away_predictions)

print(f"Home MAE: {home_mae}")
print(f"Home Accuracy: {home_accuracy:.4f}")
print(f"Away MAE: {away_mae}")
print(f"Away Accuracy: {away_accuracy:.4f}")
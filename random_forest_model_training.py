import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor


def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """Load and prepare the initial dataset."""
    data = pd.read_csv(filepath, header=0, index_col=0).transpose()
    data.drop(columns="player_id", inplace=True)
    data.dropna(inplace=True)
    return data


def split_data(data: pd.DataFrame):
    """Split data into training and testing sets."""
    x = data.drop(['cost'], axis=1)
    y = data['cost']
    return train_test_split(x, y, test_size=0.2)


def create_visualization_data(train_data: pd.DataFrame) -> pd.DataFrame:
    """Create a subset of data for visualization purposes."""
    return train_data.loc[:, [
        'mmr', 'p1', 'p2', 'p3', 'p4', 'p5', 'count', 'mean', 'std',
        'min', 'max', 'sum', 'total_games_played', 'total_winrate', 'cost'
    ]]


def plot_visualizations(visual_data: pd.DataFrame):
    """Create visualization plots."""
    # Histogram plot
    visual_data.hist(figsize=(15, 8))
    plt.savefig('histograms.png')
    plt.close()

    # Correlation heatmap
    plt.figure(figsize=(30, 16))
    sns.heatmap(visual_data.corr(), annot=True, cmap="YlGnBu")
    plt.savefig('correlation_heatmap.png')
    plt.close()


def train_models(x_train, x_test, y_train, y_test):
    """Train and evaluate both Linear Regression and Random Forest models."""
    # Linear Regression
    scaler = StandardScaler()
    x_train_s = scaler.fit_transform(x_train)
    x_test_s = scaler.transform(x_test)
    reg = LinearRegression()
    reg.fit(x_train_s, y_train)
    linear_score = reg.score(x_test_s, y_test)
    print(f"Linear Regression Score: {linear_score}")

    # Random Forest
    forest = RandomForestRegressor()
    forest.fit(x_train, y_train)
    forest_score = forest.score(x_test, y_test)
    print(f"Random Forest Score: {forest_score}")
    return forest  # Return the better performing model


def make_predictions(model, pred_filepath: str):
    """Make predictions on new data."""
    pred_data = pd.read_csv(pred_filepath, header=0, index_col=0).transpose()
    pred_data.drop(columns=["player_id", "cost"], inplace=True)
    predictions = model.predict(pred_data)
    pred_data['Predicted_Cost'] = predictions
    # Create final output
    final = pred_data[['Predicted_Cost', 'mmr', 'p1', 'p2', 'p3', 'p4', 'p5']]
    final.to_csv("results.csv")
    return final


def main():
    # Load and prepare data
    data = load_and_prepare_data("all_info.csv")
    # Split data
    x_train, x_test, y_train, y_test = split_data(data)
    # Create visualization dataset
    train_data = x_train.join(y_train)
    visual_data = create_visualization_data(train_data)
    # Create visualizations
    plot_visualizations(visual_data)
    # Transform winrate
    train_data['total_winrate'] = np.log(train_data['total_winrate'] + 1)
    # Train models
    best_model = train_models(
        train_data.drop(['cost'], axis=1),
        x_test,
        train_data['cost'],
        y_test
    )
    # Make predictions
    final_predictions = make_predictions(best_model, "prediction_data.csv")
    print("\nFinal Predictions:")
    print(final_predictions)


if __name__ == "__main__":
    main()

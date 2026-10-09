from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
PLOT_DIR = BASE_DIR / "plots"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)
PLOT_DIR.mkdir(exist_ok=True)

DATA_FILE = DATA_DIR / "house_prices.csv"
MODEL_FILE = MODEL_DIR / "house_price_model.joblib"
PLOT_FILE = PLOT_DIR / "regression.png"


# ============================================================
# STEP 1: CREATE DATA
# ============================================================

data = {
    "Size": [
        500,
        750,
        1000,
        1250,
        1500,
        1750,
        2000,
        2250,
        2500,
        2750
    ],

    "Price": [
        25,
        36,
        48,
        59,
        70,
        81,
        92,
        103,
        114,
        125
    ]
}


df = pd.DataFrame(data)


# ============================================================
# STEP 2: SAVE DATASET
# ============================================================

df.to_csv(DATA_FILE, index=False)

print("=" * 60)
print("HOUSE PRICE MACHINE LEARNING")
print("=" * 60)

print("\nDataset:")
print(df)

print(f"\nDataset saved to:")
print(DATA_FILE)


# ============================================================
# STEP 3: SEPARATE INPUT AND OUTPUT
# ============================================================

X = df[["Size"]]
y = df["Price"]


# ============================================================
# STEP 4: SPLIT DATA
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# STEP 5: CREATE AND TRAIN MODEL
# ============================================================

model = LinearRegression()

model.fit(X_train, y_train)

print("\nModel trained successfully!")


# ============================================================
# STEP 6: TEST MODEL
# ============================================================

predictions = model.predict(X_test)


# ============================================================
# STEP 7: MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = mse ** 0.5
r2 = r2_score(y_test, predictions)

print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print(f"Mean Absolute Error: {mae:.4f}")
print(f"Mean Squared Error:  {mse:.4f}")
print(f"Root Mean Squared Error: {rmse:.4f}")
print(f"R² Score: {r2:.4f}")


# ============================================================
# STEP 8: SHOW THE MODEL'S FORMULA
# ============================================================

slope = model.coef_[0]
intercept = model.intercept_

print("\n" + "=" * 60)
print("LEARNED FORMULA")
print("=" * 60)

print(f"Price = {slope:.4f} × Size + {intercept:.4f}")


# ============================================================
# STEP 9: SAVE THE TRAINED MODEL
# ============================================================

joblib.dump(model, MODEL_FILE)

print("\nTrained model saved to:")
print(MODEL_FILE)


# ============================================================
# STEP 10: LOAD THE MODEL AGAIN
# ============================================================

loaded_model = joblib.load(MODEL_FILE)

print("\nModel loaded successfully!")


# ============================================================
# STEP 11: MAKE A NEW PREDICTION
# ============================================================

new_house = pd.DataFrame({
    "Size": [1600]
})

price = loaded_model.predict(new_house)

print("\n" + "=" * 60)
print("NEW PREDICTION")
print("=" * 60)

print(
    f"A 1600 sqft house should cost approximately "
    f"{price[0]:.2f} Kes"
)


# ============================================================
# STEP 12: PREDICT MULTIPLE HOUSES
# ============================================================

new_houses = pd.DataFrame({
    "Size": [
        1200,
        1600,
        1800,
        2200,
        3000
    ]
})

new_prices = loaded_model.predict(new_houses)

print("\nMultiple predictions:")

for size, predicted_price in zip(
    new_houses["Size"],
    new_prices
):
    print(
        f"{size} sqft -> "
        f"{predicted_price:.2f} Kes"
    )


# ============================================================
# STEP 13: CREATE GRAPH
# ============================================================

plt.figure(figsize=(10, 6))

# Real data
plt.scatter(
    df["Size"],
    df["Price"],
    label="Real prices"
)

# Regression line
plt.plot(
    df["Size"],
    loaded_model.predict(X),
    label="Model prediction"
)

plt.xlabel("House Size (sqft)")
plt.ylabel("Price (Kes)")

plt.title("House Price Prediction")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(PLOT_FILE, dpi=150)

plt.show()

print("\nGraph saved to:")
print(PLOT_FILE)

print("\nTraining complete!")
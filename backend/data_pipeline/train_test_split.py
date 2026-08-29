import pandas as pd

df = pd.read_csv("data/campus_dataset_final.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Last 336 hours (2 weeks) as test set, rest as train
test_hours = 336
train_df = df.iloc[:-test_hours]
test_df = df.iloc[-test_hours:]

train_df.to_csv("data/train.csv", index=False)
test_df.to_csv("data/test.csv", index=False)

print(f"Train shape: {train_df.shape}")
print(f"Test shape: {test_df.shape}")
print(f"Train range: {train_df['timestamp'].min()} to {train_df['timestamp'].max()}")
print(f"Test range: {test_df['timestamp'].min()} to {test_df['timestamp'].max()}")

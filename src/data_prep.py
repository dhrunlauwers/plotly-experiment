
import pandas as pd

# read the weekly price and volume data
df_raw = pd.read_csv('../data/finances.csv')

# filter out price columns only and rename to just asset names
price_cols = [col for col in df_raw.columns if 'Adj Close' in col]
df_price = df_raw[price_cols]
df_price.columns = [col.split()[2] for col in df_price.columns]

# shift forward one day and drop the empty row at the end
df_shift = df_price.shift(-1)[:-1]

# calculate weekly returns
df_returns_weekly = (df_shift - df_price[:-1]) / df_price[:-1]

# calculate covariance matrix of weekly returns
result = df_returns_weekly.cov()

# tag on the annualized weekly return as a column
result['mu'] = (1 + df_returns_weekly.mean()) ** 50 - 1

# write to file
result.to_csv('../data/cov-matrix-and-returns.csv')
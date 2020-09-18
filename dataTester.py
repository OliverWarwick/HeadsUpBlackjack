import pandas as pd

df = pd.read_csv('trial_run.csv')
pd.set_option('max_columns', 7)
print(df[df.PlayerTotal == 12])

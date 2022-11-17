import pandas as pd
from pathlib import Path

data_dir = 'data'

df_lst = []

def append_name(x, bank_name):
    if bank_name in x:
        return x
    else:
        return bank_name + " - " + x


for branch in Path(data_dir).glob('**/*/*/*_branch.csv'):
    df = pd.read_csv(str(branch))
    bank_name = branch.parent.parent.parent.name
    df[df.columns[0]] = df[df.columns[0]].apply(lambda x: append_name(x, bank_name))
    df_lst.append(df)


print('Number of branch', len(df_lst))

concat_df = pd.concat(df_lst, axis=0)

print('len concat', len(concat_df))

concat_df.to_csv('bank_branch_in_VN.csv', index=False, header=True)
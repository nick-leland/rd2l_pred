import pandas as pd
import os
from os import path
from training_data_prep import list_format, modification, league_money, df_gen


if __name__ == "__main__":
    data_type = 'prediction'
    draft, captains = list_format("input")
    money = league_money(captains, data_type)
    df_gen(draft, league_money(captains, data_type), data_type)
    print(f"{data_type.capitalize()} Data was successfully prepared")


import pandas as pd


def generate_csv(data):
    df = pd.DataFrame(data)
    file_path = "testcases.csv"
    df.to_csv(file_path, index=False)
    return file_path

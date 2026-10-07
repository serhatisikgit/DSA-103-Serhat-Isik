import pandas as pd


def load_and_clean_setup_data(filepath, setup_name):
    """Load and standardize data from one setup"""
    # 1. Load the CSV file into a table (DataFrame)
    df = pd.read_csv(filepath)

    # 2. If the file has temperature in Fahrenheit, convert it to Celsius.
    #    This must happen BEFORE renaming, because we look for the old name.
    if "temp_fahrenheit" in df.columns:
        df["temp_fahrenheit"] = (df["temp_fahrenheit"] - 32) * 5 / 9

    # 3. Rename columns so both setups use the same names.
    #    Columns that don't exist in a file are simply ignored.
    df = df.rename(columns={
        "temp_fahrenheit": "temperature_C",   # converted to Celsius below
        "molarity": "concentration_M",
        "ph_value": "ph",
        "product_yield": "yield_percent",
    })

    # 4. Handle missing data: drop rows that have any empty cell
    df = df.dropna()

    # 5. Add a column that says which setup the data came from
    df["setup"] = setup_name

    return df


def combine_datasets(setup_a_data, setup_b_data):
    """Combine datasets from both setups"""
    # Stack the two tables on top of each other and renumber the rows 0, 1, 2...
    return pd.concat([setup_a_data, setup_b_data], ignore_index=True)


if __name__ == "__main__":
    # Quick test: runs only when you execute this file directly
    setup_a = load_and_clean_setup_data("data/setup_A.csv", "A")
    setup_b = load_and_clean_setup_data("data/setup_B.csv", "B")
    combined = combine_datasets(setup_a, setup_b)
    print(combined)
    print(combined.shape)

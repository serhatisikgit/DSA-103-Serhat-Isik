import numpy as np


def calculate_reaction_rates(dataframe):
    """Calculate reaction rates for each time interval"""
    df = dataframe.copy()
    by_setup = df.groupby("setup")

    """Differences between consecutive measurements within each setup.
    The first row of each setup has no previous value, so it stays NaN."""

    dt = by_setup["time_min"].diff().to_numpy()
    dc = by_setup["concentration_M"].diff().to_numpy()
    dy = by_setup["yield_percent"].diff().to_numpy()

    """Concentration decreases as the reaction runs, so the rate is -dc/dt (M/min)"""

    df["reaction_rate_M_per_min"] = np.negative(dc) / dt
    df["yield_increase_per_min"] = dy / dt

    return df


def find_optimal_conditions(dataframe, rates=None):
    """Analyze data to find optimal reaction conditions"""
    if rates is None:
        rates = calculate_reaction_rates(dataframe)

    df = rates.copy()
    df["temp_start_C"] = df.groupby("setup")["temperature_C"].shift()

    """Yield increase per minute, so setups with different time steps (5 vs 3 min) are comparable"""

    best = df.loc[df["yield_increase_per_min"].idxmax()]

    return {
        "setup": best["setup"],
        "temperature_range_C": (round(float(best["temp_start_C"]), 1), round(float(best["temperature_C"]), 1)),
        "yield_increase_per_min": round(float(best["yield_increase_per_min"]), 2),
        "reaction_rate_M_per_min": round(float(best["reaction_rate_M_per_min"]), 4),
    }


def compare_setups(dataframe):
    """Compare performance between setups A and B"""
    summary = dataframe.groupby("setup").agg(
        mean_yield=("yield_percent", "mean"),
        final_yield=("yield_percent", "last"),
        duration_min=("time_min", "max"),
    )

    mean_yield = {setup: round(float(v), 2) for setup, v in summary["mean_yield"].items()}

    return {
        "mean_yield_percent": mean_yield,
        "final_yield_percent": {setup: float(v) for setup, v in summary["final_yield"].items()},
        "duration_min": {setup: int(v) for setup, v in summary["duration_min"].items()},
        "higher_average_yield": max(mean_yield, key=mean_yield.get),
    }


if __name__ == "__main__":
    from data_cleaner import combine_datasets, load_and_clean_setup_data

    combined = combine_datasets(
        load_and_clean_setup_data("data/setup_A.csv", "A"),
        load_and_clean_setup_data("data/setup_B.csv", "B"),
    )
    rates = calculate_reaction_rates(combined)
    print(rates)

    """Quick checks: setup A, 0 -> 5 min: concentration 1.00 -> 0.85 M, yield 0 -> 12 %"""

    first_a = rates[rates["setup"] == "A"].iloc[1]
    assert np.isclose(first_a["reaction_rate_M_per_min"], 0.03)
    assert np.isclose(first_a["yield_increase_per_min"], 2.4)
    assert rates.groupby("setup")["reaction_rate_M_per_min"].apply(lambda s: s.isna().sum()).eq(1).all()

    print(find_optimal_conditions(combined, rates))
    print(compare_setups(combined))

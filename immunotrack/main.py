import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


def to_timeseries(df, column, time_period="M"):
    # Group the data by 'Vaccination type'
    grouped = df.groupby("Vaccination type")

    # Initialize an empty list to store the resampled DataFrames
    resampled_dfs = []

    # Loop through each group
    for group_name, group_data in grouped:
        # Resample and count occurrences in each period
        resampled = group_data.resample(time_period, on=column).size().reset_index()

        # Rename columns
        resampled.columns = [column, "count"]

        # Add the 'Vaccination type' column
        resampled["Vaccination type"] = group_name

        # Append the resampled DataFrame to the list
        resampled_dfs.append(resampled)

    # Concatenate the resampled DataFrames
    result = pd.concat(resampled_dfs, ignore_index=True)

    # Sort the result by 'date' and 'Vaccination type'
    result = result.sort_values(by=[column, "Vaccination type"])

    return result


def plot_timeseries(timeseries_df):
    # Create a figure with subplots
    fig, ax = plt.subplots(figsize=(18, 4))

    sns.lineplot(
        data=timeseries_df,
        x="Event date",
        y="count",
        ax=ax,
        linewidth=1,
        color="#163960",
    )

    ax.set_title("All vaccines delivered")

    ax.yaxis.grid(True, linestyle="--", linewidth=0.5, color="#888888")
    ax.xaxis.grid(True, linestyle="--", linewidth=0.5, color="#888888")

    # Customize the plot - remove the top, right, and left spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Set y-axis limits to 0 and 140

    ax.set_xlabel("")
    ax.set_ylabel("Vaccine Count")

    # Adjust the layout and display the plot
    plt.tight_layout()
    st.pyplot(fig)

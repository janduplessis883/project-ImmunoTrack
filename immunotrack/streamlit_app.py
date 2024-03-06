import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import pendulum
import seaborn as sns
from io import StringIO

from main import *
from rename_vaccines import *

st.set_page_config(page_title="ImmunoTrack", layout="wide")
now = pendulum.now()
data = None
html = """
<style>
.gradient-text {
    background: linear-gradient(45deg, #284d74, #d8ad45, #b2d9db, #e16d33);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 48px;
    font-weight: bold;
}
</style>
<div class="gradient-text">ImmunoTrack</div>
"""
html4 = """
<style>
.gradient-text {
    background: linear-gradient(45deg, #284d74, #d8ad45, #b2d9db, #e16d33);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 36px;
    font-weight: bold;
}
</style>
<div class="gradient-text">Quick Start</div>
"""

st.sidebar.markdown(html, unsafe_allow_html=True)
quickstart = st.sidebar.checkbox("Quick Start")
if quickstart:
    st.markdown(html4, unsafe_allow_html=True)
    # Reading md file from GitHub
    with open("immunotrack/markdown/quickstart.md", "r") as f:
        markdown_content = f.read()
    st.markdown(markdown_content, unsafe_allow_html=True)

toggle = st.sidebar.checkbox("Load sample data")


def loaddata(url):
    df = pd.read_excel(url)
    df["age_years"] = df["Date of birth"].apply(
        lambda x: now.diff(pendulum.instance(x)).in_years()
    )
    df["age_months"] = df["Date of birth"].apply(
        lambda x: (now.diff(pendulum.instance(x)).in_months())
    )
    df = map_vaccines(df)
    df = drop_vaccines(df)
    return df


def loadcsv(stringio):
    df = pd.read_csv(stringio)
    df["Date of birth"] = pd.to_datetime(df["Date of birth"], dayfirst=True)
    df["Event date"] = pd.to_datetime(df["Event date"], dayfirst=True)
    df["age_years"] = df["Date of birth"].apply(
        lambda x: now.diff(pendulum.instance(x)).in_years()
    )
    df["age_months"] = df["Date of birth"].apply(
        lambda x: (now.diff(pendulum.instance(x)).in_months())
    )
    df = map_vaccines(df)
    df = drop_vaccines(df)
    return df


def update_location(df):
    most_frequent_location = df["Event done at ID"].mode()[0]

    # Replace all other locations with 'Elsewhere'
    df["Event done at ID"] = df["Event done at ID"].apply(
        lambda x: x if x == most_frequent_location else "Elsewhere"
    )
    return df


if toggle:
    url = "immunotrack/sampledata/sampledata.xlsx"
    data = loaddata(url)
    data = update_location(data)
    ts = to_timeseries(data, "Event date", time_period="M")


else:
    # Only display the file uploader if sample data is not selected
    uploaded_file = st.sidebar.file_uploader("Choose a .csv or .xslx file", type="csv")
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        data = loadcsv(stringio)
        data = update_location(data)

if data is not None:
    plot_timeseries(ts)
    vaccination_schedule = {
        "2_months": [
            "Bexsero 1",
            "Rotarix 1",
            "Infanrix Hexa 1",
            "Prevenar - 13 1",
            "Pediacel 1",
        ],
        "3_months": ["Rotarix 2", "Infanrix Hexa 2", "Prevenar - 13 2"],
        "4_months": [
            "Infanrix Hexa 3",
            "Pediacel 2",
            "Bexsero 2",
            "Prevenar - 13 2",
        ],
        "12_months": [
            "Hib/MenC",
            "MMRvaxPRO 1",
            "Prevenar - 13 3",
            "Menitorix 1st Scheduled Booster",
            "Bexsero 3",
            "NeisVac-C 1",
            "MMRvaxPRO Under 1 yr",
        ],
        "3_years": [
            "DTaP/IPV/Hib 1",
            "DTaP/IPV/Hib/HepB 3",
            "DTaP/IPV/Hib 2",
            "DTaP/IPV/Hib 3",
            "Infanrix-IPV+HIB 1",
            "Infanrix-IPV+HIB 3",
            "Infanrix-IPV+HIB 2",
            "Infanrix Hexa Booster",
            "Priorix 1st Scheduled Booster",
            "Infanrix-IPV 1st Scheduled Booster",
            "DTaP/IPV/Hib 4",
            "Prevenar - 13 Booster",
            "DTaP/IPV 1st Scheduled Booster",
            "dTaP/IPV 1",
            "DTaP/IPV/Hib Booster",
            "Repevax 1",
            "Infanrix-IPV Booster",
            "Infanrix-IPV 2nd Scheduled Booster",
            "DTaP/IPV/Hib 1st Scheduled Booster",
            "Infanrix-IPV+HIB 1st Scheduled Booster",
            "Repevax 1st Scheduled Booster",
        ],
        "12_years": [
            "Boostrix-IPV 1st Scheduled Booster",
            "Nimenrix 1",
            "Revaxis 1st Scheduled Booster",
            "MMRvaxPRO 1st Scheduled Booster",
            "Havrix Mono Junior Monodose Booster",
            "Revaxis 2nd Scheduled Booster",
            "Boostrix-IPV Booster",
            "DTaP/IPV Booster",
            "Boostrix-IPV 2nd Scheduled Booster",
            "Bexsero 4",
            "Revaxis Booster",
            "Rotavirus - Oral 3",
            "Revaxis 2",
            "dTaP/IPV 1st Scheduled Booster",
            "Td/IPV 1",
            "Tetanus Diphtheria LD and Polio 1",
            "Revaxis 1",
            "Repevax 2nd Scheduled Booster",
            "NeisVac-C Booster",
            "Typhoid 1",
            "DTaP/IPV 2nd Scheduled Booster",
            "Typhoid Single",
        ],
        # More vaccines and schedules can be added based on the NHS guidelines
    }

    # First, filter out children under 4 months
    df_under_4_months = data[data["age_months"] < 12]

    # Prepare the vaccination schedule for the first 3 months
    vaccination_schedule = {
        "2_months": [
            "Bexsero 1",
            "Rotarix 1",
            "Infanrix Hexa 1",
            "Prevenar - 13 1",
            "Pediacel 1",
        ],
        "3_months": ["Rotarix 2", "Infanrix Hexa 2", "Prevenar 13"],
    }

    # Flatten the vaccination schedule to get a list of all vaccinations up to 3 months
    all_vaccinations = (
        vaccination_schedule["2_months"] + vaccination_schedule["3_months"]
    )

    # Initialize a dictionary to count the number of times each vaccination was administered
    vaccination_counts = {vaccine: 0 for vaccine in all_vaccinations}

    # Count each vaccination in the filtered DataFrame
    for vaccine in all_vaccinations:
        vaccination_counts[vaccine] = df_under_4_months[
            df_under_4_months["Vaccination type"] == vaccine
        ].shape[0]

    # Convert the counts to a DataFrame for easier plotting
    df_vaccination_counts = pd.DataFrame(
        list(vaccination_counts.items()), columns=["Vaccination type", "Count"]
    )

    # Define the range slider for selecting an age range in months
    age_range = st.slider(
        "Select Age Range in Years",
        min_value=0,
        max_value=100,
        value=(0, 3),
        step=1,
    )

    # Display the selected age range
    st.write("Selected Age Range:", age_range[0], "to", age_range[1], "years")

    # Filter the data based on the selected age range
    df_2_3_month_vaccines = data[
        data["age_years"].isin(range(age_range[0], age_range[1] + 1))
    ]

    # Get unique vaccination types for these months
    unique_vaccines = df_2_3_month_vaccines["Vaccination type"].unique().tolist()
    unique_vaccines.sort()

    # Let users select vaccines to plot
    selected_vaccines = st.multiselect(
        "Select Vaccines to Plot", options=unique_vaccines, default=unique_vaccines
    )

    # Filter the data based on selected vaccines
    filtered_vaccines_data = df_2_3_month_vaccines[
        df_2_3_month_vaccines["Vaccination type"].isin(selected_vaccines)
    ]

    # Sort patients by age in months before creating the 'Patient Info' field
    filtered_vaccines_data = filtered_vaccines_data.sort_values(
        by="Date of birth", ascending=True
    )

    # Create 'Patient Info' with ID, Surname, and Age, now in sorted order
    filtered_vaccines_data["Patient Info"] = (
        filtered_vaccines_data["Patient ID"].astype(str)
        + " - "
        + filtered_vaccines_data["Surname"]
        + " - "
        + filtered_vaccines_data["age_years"].astype(str)
        + " y"
    )

    refined_pivot = filtered_vaccines_data.pivot_table(
        index="Patient Info",
        columns="Vaccination type",
        values="Event date",
        aggfunc="count",
        fill_value=0,
    )

    # Plot the heatmap
    plt.figure(figsize=(14, 18))
    sns.heatmap(
        refined_pivot,
        annot=True,
        cmap="flare",
        fmt="d",
        linewidths=0.3,
        linecolor="gray",
        cbar_kws={"shrink": 0.6},
        square=False,
    )

    plt.title("Heatmap for Selected Vaccines Sorted by Age")
    plt.ylabel("Patient Info (ID - Surname - Age)")
    plt.xlabel("Vaccination Type")

    # Adjust font size here for xticks and yticks
    plt.xticks(rotation=45, ha="right", fontsize=8)  # Smaller font size for xticks
    plt.yticks(fontsize=8)  # Smaller font size for yticks

    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)
else:
    st.image("images/main.png", caption="GitHub: janduplessis883")

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    st.subheader("Dataset")
    st.dataframe(df)

    # Attempt to detect a date column automatically
    date_column = None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_column = col
            break

    # If no date column is detected, ask user to manually select one
    if date_column is None:
        date_column = st.selectbox(
            "Select a date column (if available)",
            options=df.columns,
            index=0,
            help="Choose a column that contains date values",
        )

    # If a date column is found or selected
    if date_column:
        # Convert the selected date column to datetime (if it's not already)
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

        # Drop rows with invalid dates
        df = df.dropna(subset=[date_column])

        # Sort the data by the date column
        df = df.sort_values(by=date_column)

        # Display the available date range
        min_date = df[date_column].min().date()
        max_date = df[date_column].max().date()
        st.subheader("Date Range Overview")
        st.write(f"Available dates range from *{min_date}* to *{max_date}*.")

        # Date selection
        st.subheader("Select Date Range")
        start_date = st.date_input(
            "Start Date", value=min_date, min_value=min_date, max_value=max_date
        )
        end_date = st.date_input(
            "End Date", value=max_date, min_value=min_date, max_value=max_date
        )

        # Validate date range
        if start_date > end_date:
            st.error("End date must be on or after the start date!")
        else:
            st.info(f"Selected date range: {start_date} to {end_date}")

            # Filter dataset based on the selected date range
            df_filtered = df[
                (df[date_column].dt.date >= start_date)
                & (df[date_column].dt.date <= end_date)
            ]

            # Display filtered data
            st.subheader("Filtered Data")
            st.dataframe(df_filtered)

            # Summary Statistics
            st.subheader("Summary Statistics")
            st.write(df_filtered.describe())

            # Correlation Heatmap
            if len(df_filtered.select_dtypes(include=["number"]).columns) > 1:
                st.subheader("Correlation Heatmap")
                plt.figure(figsize=(10, 8))
                heatmap_fig = sns.heatmap(
                    df_filtered.corr(), annot=True, cmap="coolwarm"
                )
                st.pyplot(heatmap_fig)

            # Identify numeric columns for visualization
            numeric_columns = df_filtered.select_dtypes(include=["number"]).columns

            if numeric_columns.empty:
                st.error("No numeric columns available for plotting.")
            else:
                # Interactive Line Chart
                st.subheader("Interactive Line Chart")
                line_fig = px.line(
                    df_filtered,
                    x=date_column,
                    y=numeric_columns[0],
                    title="Line Chart",
                    labels={
                        date_column: "Date",
                        numeric_columns[0]: numeric_columns[0],
                    },
                    template="plotly_dark",
                )
                st.plotly_chart(line_fig)

                # Interactive Bar Chart
                st.subheader("Interactive Bar Chart")
                bar_fig = px.bar(
                    df_filtered,
                    x=date_column,
                    y=numeric_columns[0],
                    title="Bar Chart",
                    labels={
                        date_column: "Date",
                        numeric_columns[0]: numeric_columns[0],
                    },
                    color=numeric_columns[0],
                    color_continuous_scale="Viridis",
                    template="plotly_dark",
                )
                st.plotly_chart(bar_fig)

                # Interactive Scatter Plot
                st.subheader("Interactive Scatter Plot")
                scatter_fig = px.scatter(
                    df_filtered,
                    x=date_column,
                    y=numeric_columns[0],
                    size=numeric_columns[0],
                    title="Scatter Plot",
                    labels={
                        date_column: "Date",
                        numeric_columns[0]: numeric_columns[0],
                    },
                    color=numeric_columns[0],
                    color_continuous_scale="Plasma",
                    template="plotly_dark",
                )
                st.plotly_chart(scatter_fig)

            # Download Filtered Data
            st.subheader("Download Filtered Data")
            csv_data = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="filtered_data.csv",
                mime="text/csv",
            )
    else:
        st.error("No date column found or selected in the dataset.")

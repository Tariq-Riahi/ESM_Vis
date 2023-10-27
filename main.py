import streamlit as st
import pandas as pd
import re
import altair as alt


# extracts values from strings
def transform_value(value):
    if isinstance(value, str) and re.search(r'\d', value):
        # If it's a string containing a number, extract the number
        number = int(re.search(r'\d+', value).group())
        return number
    elif value == 'yes':
        # Change 'yes' to True
        return True
    elif value == 'no':
        # Change 'no' to False
        return False
    else:
        # If it's anything else, keep it as a string
        return value

def extract_metrics(df):
    metrics = ["satisfaction", "happiness", "confidence", "stress", "irritation", "sadness", "laugh_frequency", 'social_interaction', 'general_rating', 'comments']
    metric_data = {}

    i = 1
    for metric in metrics:
        metric_df = df.iloc[i::11, :]
        metric_data[metric] = metric_df
        i += 1

    return metric_data

# upload file
uploaded_file = st.file_uploader("Upload a XLSX file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Proper transpose using melt
    df.reset_index(level=0, inplace=True)
    df = pd.melt(df, id_vars='index', var_name='NewColumnName', value_name='Value')
    df = df.set_index('index')
    df = df.iloc[3::2]

    # Extraccting values from strings
    df['Value'] = df['Value'].apply(lambda x: transform_value(x))
    df['Day'] = df['NewColumnName'].apply(lambda x: transform_value(x))
    df['Day'] = 25 - df['Day']

    # Creatings dfs per metric
    metric_data = extract_metrics(df)


    combined_chart = None
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'teal', 'brown', 'pink']
    ci = 0

    for metric in metric_data:
        st.write(metric)
        # st.write(metric_data[metric])

        if metric == "social_interaction" or metric == "comments":
            st.write(metric_data[metric].iloc[:, 1:])
        else:
            # Determine the y-axis range based on the metric
            if metric == 'general_rating':
                y_range = (0, 10)  # Set the range for 'general_rating'
            else:
                y_range = (0, 5)  # Default range for other metrics

            alt_chart = alt.Chart(metric_data[metric].iloc[:, 1:]).mark_line().encode(
                x='Day:O',  # Assuming 'Day' is a timestamp or date column
                y=alt.Y('Value:Q', scale=alt.Scale(domain=y_range)),
                color=alt.value(colors[ci])
            ).properties(
                width=500,
                height=300
            )

            if combined_chart is None and metric != 'general_rating':
                combined_chart = alt_chart
            elif metric != 'general_rating':
                combined_chart += alt_chart

            alt_chart += alt_chart.transform_regression('Day', 'Value').mark_line().encode(
                color=alt.value("#FFF")
            )
            ci += 1
            # Display the Altair chart using Streamlit
            st.altair_chart(alt_chart, use_container_width=True)


    st.altair_chart(combined_chart, use_container_width=True)


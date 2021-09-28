import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import altair as alt
from streamlit import caching
from dotenv import load_dotenv
import os


## CONFIG
possible_values = {
    "content" : ["Excellent", "Very Good", "Good", "Fair", "Poor"],
    "instructor": ["Excellent", "Very Good", "Good", "Fair", "Poor"],
    "useful": ["Great deal", "A lot", "A moderate amount", "A little", "None at all"],
    "going_forward":["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
}

question_string = {
    "company": "What company do you work for?",
    "Date": "Date of workshop",
    "workshop_name": "Which workshop was presented?",
    "content": "Overall, how would you rate the content of the workshop?",
    "instructor":"Overall, how would you rate the instructors of the workshop?",
    "useful": "How useful was this session in understanding the technology that was presented?",
    "going_forward": "Following this workshop, I view IBM and/or Red Hat technologies will be/is an important part of our workflow.",
    "other_workshops": "Are there other technologies you'd like the IBM Developer Advocacy team to provide similar training for?",
    "other_comment": "Please add any further comments on what you felt worked well in the workshop and any suggestions for improvement"
}


WIDTH = 600

menu_items = {
	'Get help': 'https://github.com/omidmeh/cda-survey-frontend',
	'Report a bug': 'https://github.com/omidmeh/cda-survey-frontend/issues/new',
	'About': '''
	 ## CDA Survey Results

	 This app helps you render the survey results for CDA Surveys.
	'''
}

##
load_dotenv()
SHEET_ID = os.environ['SHEET_ID']
SHEET_NAME = os.environ['SHEET_NAME']

st.set_page_config(page_title='CDA Survey Results', layout = 'centered', initial_sidebar_state = 'auto', menu_items=menu_items)
st.title('Survey Results')

@st.cache
def load_data():
    sheet_name = urllib.parse.quote(SHEET_NAME)
    url_2 = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url_2)

def top_two_category_percent(df, feature):
    result = 0

    cat0_count = (df[question_string[feature]] == possible_values[feature][0]).sum()
    cat1_count = (df[question_string[feature]] == possible_values[feature][1]).sum()
    sum_count = df.shape[0]

    result = (cat0_count + cat1_count )/sum_count * 100

    return result


def filter_by(df, column_name, values_to_keep, hide_filtered_columns = True):
    if (values_to_keep):
        result = df[df[column_name].isin(values_to_keep)]
        if hide_filtered_columns:
            result.drop(column_name, axis=1, inplace=True)

        return result
    else:
        return df

def result_chart(df, feature, axis_name=None, width=400 ):
    col_name = question_string[feature]
    

    if axis_name:
        title = axis_name
    else:
        title = col_name

    score = df[col_name].value_counts().reindex(possible_values[feature] ,fill_value=0).reset_index()
    score['percent'] = score[col_name] / sum(score[col_name])
    score['percent'] = score['percent'].round(2)

    c = alt.Chart(score).mark_bar().properties(width=width).encode(
        tooltip=['index', 'percent', f"{col_name}"],
        x=alt.X('index:O', axis=alt.Axis(title=title), sort=None) ,
        y = alt.Y("percent", type="quantitative", axis=alt.Axis(title='Count', format='.0%')))
        # y = alt.Y(col_name, type="quantitative", axis=alt.Axis(title='Count', format='%')))

    return c 
    



# Load Data
data_load_state = st.text('Loading data...')
raw_data = load_data()
data_load_state.text('')


df = raw_data.copy()

# st.sidebar.header('Filters')
# st.sidebar.subheader('Columns')
# hide_filtered_columns = st.sidebar.checkbox("Hide Filtered Columns", value=True, key=None, help=None, on_change=None, args=None, kwargs=None)
# hide_timestamp = st.sidebar.checkbox("Hide Timestamp", value=True, key=None, help=None, on_change=None, args=None, kwargs=None)
# if (hide_timestamp):
#     df.drop('Timestamp', axis=1, inplace=True)
hide_filtered_columns = True
hide_timestamp = True

st.sidebar.subheader('Filter Options')
filter_includes = st.sidebar.multiselect("Company Name", options=df['What company do you work for?'].unique(), )
df = filter_by(df, question_string["company"], filter_includes, hide_filtered_columns)

filter_includes = st.sidebar.multiselect("Date of workshop", options=df['Date of workshop'].unique())
df = filter_by(df, question_string["Date"], filter_includes, hide_filtered_columns)

filter_includes = st.sidebar.multiselect(question_string["workshop_name"], 
                                         options=df[question_string["workshop_name"]].unique())
df = filter_by(df, question_string["workshop_name"], filter_includes, hide_filtered_columns)


## Highlights:
survey_count = df.shape[0]
content_ex_vg = top_two_category_percent(df,'content')

st.subheader("Highlights")

highlights = f"""
- There are a total of **{survey_count} surveys**.
- **{top_two_category_percent(df,'content'):.0f}**% of participants found the **content** "Excellent" or "Very Good".
- **{top_two_category_percent(df,'instructor'):.0f}**% of participants found the **instructors** "Excellent" or "Very Good".
- **{top_two_category_percent(df,'useful'):.0f}**% of participants agree that the workshop was "A great deal" or "A lot" of help in **understanding the technology**.
- **{top_two_category_percent(df,'going_forward'):.0f}**% of participants "agree" or "strongly agree" that **IBM/RH** will be an important part of their workflow.
"""

st.write(highlights)



st.subheader("Details")
c = result_chart(df,"content", axis_name="Content Rating", width=WIDTH/2)
i = result_chart(df,"instructor", axis_name="Instructor Rating", width=WIDTH/2)

u = result_chart(df,"useful", axis_name="Content Usefulness", width=WIDTH/2)
f = result_chart(df,"going_forward", axis_name="Going Forward", width=WIDTH/2)

st.altair_chart(alt.hconcat(c,i))
st.altair_chart(alt.hconcat(u,f))

st.sidebar.subheader("Text Fields")
if st.sidebar.checkbox("Interest in other workshops", value=True):
    st.table(df[question_string["other_workshops"]].dropna().reset_index(drop=True).rename("Interest in other workshops"))

if st.sidebar.checkbox("Other comments", value=True):
    st.table(df[question_string["other_comment"]].dropna().reset_index(drop=True).rename("Other comments"))

# st.sidebar.subheader("Data")
# refresh = st.sidebar.button('Refresh Data')
# if refresh:
#     st.caching.clear_cache()

# st.sidebar.download_button("Download", df)

# DEBUG
# st.sidebar.subheader('Debug')

# st.subheader('Debug')
# st.write(df)
# st.write(df.columns)

## MainMenu {visibility: hidden;}
hide_streamlit_style = """
<style>

footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


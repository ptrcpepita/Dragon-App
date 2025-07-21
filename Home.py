import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="home", layout="wide")

st.markdown(
        """
        <style>
            [data-testid = "stSidebarNav"]{
            background-image: url("https://raw.githubusercontent.com/ptrcp/dragon_app/ddcfeac3b8da8cdd70b8047bbab42f643dc6572a/dragon_logo_png.png");
            background-repeat: no-repeat;
            background-size: 210px;
            padding-top: 100px;
            background-position: 0px 0px;
            }
        </style>
        """, unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="margin-left: -7px;">
        <img src="https://raw.githubusercontent.com/ptrcp/dragon_app/70f79ea1fd389a3822f3ce8f0a351762de1fbf39/dragon2_logo_png.png" width="500">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("")
st.markdown("")
st.markdown("""##### Dragon is an interactive data preparation and visualization app — designed to quickly transform, filter, and visualize dataset to ready use.""")

st.markdown("")
st.markdown("")
st.markdown("##### Features:")
st.markdown("""
##### 🔄 **1. Data Transformation**
- Clean common formatting issues: trim whitespace
- Apply column validation, calculation, grouping, and value extraction
- Remove duplicate data
- Drop unused column
""")
st.markdown("")

st.markdown("""
##### 🎯 **2. Data Filtering**
- Filter by condition (e.g., value ranges, specific names)
""")
st.markdown("")

st.markdown("""
##### 📊 **3. Data Visualization**
- Visualize data
- Compare data with charts
""")

st.markdown("")
st.markdown("")
st.markdown("""###### Users are able to use the feature independently, but it is recommended to use it based on feature order (transform -> filter -> visualize).""")


            
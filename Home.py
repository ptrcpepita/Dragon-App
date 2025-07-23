import streamlit as st

st.set_page_config(page_title="home", layout="wide")

st.markdown(
        """
        <style>
            [data-testid = "stSidebarNav"]{
            background-image: url("https://raw.githubusercontent.com/ptrcpepita/Dragon-App/74d7b0924a521afba224fca618d9e0771ea525e2/asset/dragon_logo_png.png");
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
        <img src="https://raw.githubusercontent.com/ptrcpepita/Dragon-App/ef59d7794c3f32d47a9926637facc2a66380f725/asset/dragon2_logo_png.png" width="500">
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

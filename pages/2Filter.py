import streamlit as st
import pandas as pd
import numpy as np
import io
from io import BytesIO
import os
import requests
import re
from datetime import datetime
import xlsxwriter

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

output = BytesIO()

# BUTTON for flow 1-5
if "explore_clicked" not in st.session_state:
    st.session_state['explore_clicked'] = False
if "filter_clicked" not in st.session_state:
    st.session_state['filter_clicked'] = False
if "previewclean_clicked" not in st.session_state:
    st.session_state['previewclean_clicked'] = False
if 'savedata_clicked' not in st.session_state:
    st.session_state['savedata_clicked'] = False

st.markdown("## 🎯 Data Filtering")

st.image("https://raw.githubusercontent.com/ptrcpepita/Dragon-App/74a060302a502fa4fa7083f392180c4567026fa5/asset/userflow_filter.png", width=700)

# 1. UPLOAD DATA
#st.markdown("---")
#st.subheader("📂 1. Upload an Excel File")
#uploaded_file = st.file_uploader('Upload here', type=["xlsx", "csv"])

#current_file_name = uploaded_file.name if uploaded_file else None
#if ("uploaded_file_name" in st.session_state # cek apakah filenya berubah/ilang
    #and st.session_state.uploaded_file_name != current_file_name):
    #for key in ["original_df", "df", "custom_dtypes", "change_history"]:
        #st.session_state.pop(key, None)
    #st.session_state.uploaded_file_name = current_file_name
    
#elif uploaded_file and "uploaded_file_name" not in st.session_state:
    #st.session_state.uploaded_file_name = current_file_name

st.markdown("---")
st.subheader("📂 1. Insert an Excel File Link")
url = st.text_input("Paste the one drive public Excel file URL here (format = one drive link + '&download=1'):")


current_file_name = os.path.basename(url) if url else None
if ("url_name" in st.session_state # cek apakah filenya berubah/ilang
    and st.session_state.url_name != current_file_name):
    for key in ["original_df", "df", "custom_dtypes", "change_history", "change_history2"]:
        st.session_state.pop(key, None)
    st.session_state.url_name = current_file_name
    
elif url and "url_name" not in st.session_state:
    st.session_state.uploaded_file_name = current_file_name
        
if url:
    try:
        if "original_df" not in st.session_state:
            #df = pd.read_excel(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'}) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})
            
            #st.session_state.original_df = df.copy() # original data
            #st.session_state.df = df.copy() # ini working copy yang user akan pake
            # st.session_state.custom_dtypes = {col: str(df[col].dtype) for col in df.columns}
            #st.session_state.change_history = []
            #st.success("Dataset loaded successfully. Click button below to filter the data")
            
            response = requests.get(url)
            response.raise_for_status()  # Raise error for bad status
            df = pd.read_excel(BytesIO(response.content), dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})  # For .xlsx files

            st.session_state.original_df = df.copy() # original data
            st.session_state.df = df.copy() # ini working copy yang user akan pake
            #st.session_state.change_history = []
            st.success("Dataset loaded successfully. Click button below to filter the data")

        # 2. PREVIEW DATA
        # indent: 2
        if st.button('Preview Data ⏭️'):
            st.session_state['explore_clicked'] = True
        df_original = st.session_state.original_df # supaya original df gak ke ubah

        if st.session_state['explore_clicked']:
            st.markdown("---")
            st.subheader('📈 2. Preview Data')
            st.write("**Data shape:**", df_original.shape)
            st.write("**Data:**")
            st.dataframe(df_original.head(10))

            info_df = pd.DataFrame({"Column": df_original.columns,
                                    "Null Count":df_original.isna().sum().values,
                                    "Dtype": df_original.dtypes.values})

            st.write("**Column Names and Data Types:**")
            st.dataframe(info_df)
            
            st.success("Done previewing. Filter the data by clicking button below")
            
            # indent: 3
            # 3. FILTER DATA
            if st.button('Filter Data ⏭️'):
                st.session_state['filter_clicked'] = True
            if st.session_state['filter_clicked']:
                st.markdown("---")
                st.subheader('🎯 3. Data Filtering')
                df = st.session_state.df
                
                if "filtered_cols" not in st.session_state:
                    st.session_state.filtered_cols = []
                    
                col = st.selectbox("Choose column to be filtered", options=[""] + list(df.columns), key="filter_column")
                if col:
                    col_dtypes = df[col].dtypes
                    st.write("New data shape:", len(df))
                    st.write(f"Data type: ", col_dtypes)
                    st.write(f"Values: ", df[col].value_counts())

                    if pd.api.types.is_string_dtype(col_dtypes) or pd.api.types.is_object_dtype(col_dtypes):
                        value = st.text_input("Type value(s) to remove/drop (separated by comma, case sensitive)")
                        if value:
                            value_sep = [(x.strip()) for x in value.split(',') if x.strip()]
                            if st.button("Drop value"):
                                df = df[~df[col].isin(value_sep)]
                                st.session_state.df = df
                                st.session_state.filtered_cols.append(col)
                                st.success(f"Successfully drop value '{value}' from '{col}' column")
                                st.write(f"Values: ", df[col].value_counts())
                                st.write("New data shape: ",len(df))
                    elif pd.api.types.is_numeric_dtype(col_dtypes):
                        min_num = df[col].min()
                        max_num = df[col].max()
                        st.write(f"Available number range: `{min_num:,.0f} to {max_num:,.0f}`")
                        min_val = st.number_input("Input number range (min) to DROP", value=0)
                        max_val = st.number_input("Input number range (max) to DROP", value=0)
                        
                        if st.button("Drop value"):
                            df = df[~df[col].between(min_val, max_val)]
                            st.session_state.df = df
                            st.session_state.filtered_cols.append(col)
                            st.success(f"Successfully drop values between {min_val:,} and {max_val:,} from column '{col}'")
                            st.write("New data shape:", len(df))
                            
                    elif pd.api.types.is_datetime64_any_dtype(col_dtypes):
                        min_date = df[col].min()
                        max_date = df[col].max()
                        st.write(f"Available date range: `{min_date.date()} to {max_date.date()}`")
                        date_range = st.date_input("Choose date range to drop", value=(min_date, max_date))
                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            start_date = pd.to_datetime(start_date)
                            end_date = pd.to_datetime(end_date)

                            df = df[~((df[col] >= start_date) & (df[col] <= end_date))]
                            if st.button("Drop value"):
                                st.session_state.df = df
                                st.session_state.filtered_cols.append(col)
                                st.success(f"Successfully drop values between {start_date} and {end_date} from column '{col}'")
                                st.write(f"Values: ", df[col].value_counts())
                                st.write("New data shape: ",len(df))

                if st.session_state.filtered_cols:
                    st.info(f"Columns filtered so far: {', '.join(st.session_state.filtered_cols)}")
                st.markdown("")
                st.markdown("")
                if st.button("🔄 Reset Filter"):
                    st.session_state.df = st.session_state.original_df
                    st.session_state.filtered_cols = []
                    st.success("Filter reset!")
                    
                # INDENT 4
                # PREVIEW FILTERED DATA
                if st.button('Preview Filtered Data ⏭️'):
                    st.session_state['previewclean_clicked'] = True
                if st.session_state['previewclean_clicked']:
                    st.markdown("---")
                    st.subheader('🎯 4. Preview Filtered Data')
                    st.write("**Data shape:**", df.shape)
                    st.write("**Data:**")
                    st.dataframe(df.head(10))

                    info_df = pd.DataFrame({"Column": df.columns,
                                    "Null Count":df.isna().sum().values,
                                    "Dtype": df.dtypes.values})
                    st.write("**Column Names and Data Types:**")
                    st.dataframe(info_df)
                    st.write("**Check Distinct Value**")
                    selected_columns = st.multiselect("Choose column to check distinct value:", options=df.columns.tolist())
                    if selected_columns:
                        for col in selected_columns:
                            st.write(df[col].value_counts())
                    
                    # INDENT 5
                    # SAVE DATA
                    if st.button('Save Data ⏭️'):
                        st.session_state['savedata_clicked'] = True
                    if st.session_state['savedata_clicked']:
                        st.markdown("---")
                        st.subheader('📥 5. Save Filtered Data')
                        try:
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df.to_excel(writer, index=False, sheet_name='Sheet1')
                                writer.close()
                                processed_data = output.getvalue()
                
                            if st.download_button(label="Download as Excel", data=processed_data,
                                                file_name=f"filtered_{uploaded_file.name}.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
                                st.success("Dataset successfully saved.")
                        except Exception as e:
                            st.error(f"❌ Error saving file: {e}")
                                           
            st.write("")
            st.write("")
            st.write("")
            if st.button("🔄🔄 Reset All"):
                st.session_state.clear()
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
else:
    st.info("Please upload an Excel file to get started.")

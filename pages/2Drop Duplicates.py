import requests
import io
import os
from io import BytesIO
import streamlit as st
import pandas as pd

if "removedupli_clicked" not in st.session_state:
    st.session_state['removedupli_clicked'] = False

st.markdown("## 🔄 Drop Duplicate Data")

st.image("https://raw.githubusercontent.com/ptrcpepita/Dragon-App/93cd0d4daea18d24544b50e00fb68cea9b8a98f2/asset/userflow_transform.png", width=650)

st.subheader("📂 Insert an Excel File Link")
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
            response = requests.get(url)
            response.raise_for_status()  # Raise error for bad status
            df = pd.read_excel(BytesIO(response.content), dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})  # For .xlsx files
            
            st.session_state.original_df = df.copy() # original data
            st.session_state.df = df.copy() # ini working copy yang user akan pake
            st.success("Dataset loaded successfully. Click button below to transform the data")
            
            # REMOVE DUPLICATE
            # indent: 2
        st.markdown("")
        if st.button('Remove Duplicate ⏭️'):
            st.session_state['removedupli_clicked'] = True
        df_original = st.session_state.original_df
        df = st.session_state.df
        
        if st.session_state['removedupli_clicked']:
            st.markdown("---")
            st.subheader('📑 Remove Duplicate')
            st.write("Data shape: ", {len(df)})
            st.write("Data preview:")
            st.dataframe(df.head(10))
            input_dupli = st.number_input("How many base column to remove duplicate?", min_value=0, max_value =len(df.columns), step=1, format='%d', key='num_dupli')
            st.write("min: 1, max:", len(df.columns))

                #if input_dupli == 0:
                    #st.info("No duplicate will be removed.")
                #else:
                    #if st.button("Ok", key='ok'):
            if input_dupli != 0:
                st.session_state['dupli_config'] = True

                if st.session_state.get('dupli_config', False):
                    selected_cols = []
                    for i in range(st.session_state['num_dupli']):
                        col = st.selectbox(f"Choose column {i+1}", options=[""] + list(df.columns), key=f"dupli_col_{i}")
                        st.dataframe(df[col].value_counts())
                        #st.write("Total of unique value: ",df[col].nunique())
                        if col:
                            selected_cols.append(col)
                            
                    dupli_row = df[df.duplicated(subset=selected_cols, keep=False)]
                    dupli_row = dupli_row.sort_values(by=selected_cols)
                    st.write("Duplicated data rows:")
                    st.dataframe(dupli_row)
        
                    if selected_cols:
                        keep_option = st.radio("Which duplicate data should be DROP?", options=["First", "Last", "All", "Choose index"], index=0, horizontal=True)
                        st.markdown("""
                        Note:
                        - First: drop the first, keep the last occurrence
                        - Last: drop keep last, keep the first occurrence
                        - All: drop all duplicate
                        - Choose index: choose index you want to DROP
                        """)
                                
                        choose_index = False
                        if keep_option == "Choose index":
                            choose_index = True
                            index = st.text_input("Enter index number you want to **DROP** (separated by commas): ", placeholder='eg. 9, 15, 180')
                            if index:
                                    #try:
                                number = [int(x.strip()) for x in index.split(',') if x.strip().isdigit()]
                                st.write(f"Index number entered: {number}")
                                        #except Exception as e:
                                            #st.error(f"Invalid input: {e}")
                    
                    if st.button("Remove", key='remove dupli'):
                            #df_cleaned = None
                        if keep_option == "Last":
                            df = df.drop_duplicates(subset=selected_cols, keep='first').reset_index(drop=True)
                        elif keep_option == "First":
                            df = df.drop_duplicates(subset=selected_cols, keep='last').reset_index(drop=True)
                        elif keep_option == "All":
                            dup_mask = df.duplicated(subset=selected_cols, keep=False)
                            df = df[~dup_mask].reset_index(drop=True)
                        elif choose_index == True:
                            df = df.drop(number).reset_index(drop=True)
                            choose_index = False
                        
                        st.success(f"Successfully remove duplicate based on {', '.join(selected_cols)} using '{keep_option}'")
                        st.write("New data:")
                        st.dataframe(df.head())
                        st.write("New data shape: ",len(df))
                        st.session_state.df = df

            st.write("")
            st.markdown("")
            st.markdown("")
            st.write("")
            st.write("")
            if st.button("🔄🔄 Reset All", key='reset_all'):
                st.session_state.clear()
                st.rerun()
                        
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
else:
    st.info("Please upload an Excel file to get started.")

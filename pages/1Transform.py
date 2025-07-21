import streamlit as st
import pandas as pd
import numpy as np
import io
from io import BytesIO
import re
from datetime import datetime
import xlsxwriter

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

output = BytesIO()

# BUTTON for flow 1-5
if "explore_clicked" not in st.session_state:
    st.session_state['explore_clicked'] = False
if "clean_clicked" not in st.session_state:
    st.session_state['clean_clicked'] = False
if "transform_clicked" not in st.session_state:
    st.session_state['transform_clicked'] = False
if "removedupli_clicked" not in st.session_state:
    st.session_state['removedupli_clicked'] = False
if "previewclean2_clicked" not in st.session_state:
    st.session_state['previewclean2_clicked'] = False
if "dropcol_clicked" not in st.session_state:
    st.session_state['dropcol_clicked'] = False
if 'savedata_clicked' not in st.session_state:
    st.session_state['savedata_clicked'] = False

st.markdown("## 🔄 Data Transformation")

st.image("https://raw.githubusercontent.com/ptrcp/dragon_app/0cc868f337e105fe2ba4b1508bd51cdc7e9d1c63/userflow_transform.png", width=650)

# 1. UPLOAD DATA
st.markdown("---")
st.subheader("📂 1. Upload an Excel File")
uploaded_file = st.file_uploader('Upload here', type=["xlsx", "xls", "csv"])

current_file_name = uploaded_file.name if uploaded_file else None
if ("uploaded_file_name" in st.session_state # cek apakah filenya berubah/ilang
    and st.session_state.uploaded_file_name != current_file_name):
    for key in ["original_df", "df", "custom_dtypes", "change_history", "change_history2"]:
        st.session_state.pop(key, None)
    st.session_state.uploaded_file_name = current_file_name
    
elif uploaded_file and "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = current_file_name
        
if uploaded_file:
    try:
        if "original_df" not in st.session_state:
            df = pd.read_excel(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})
            #else:
                #df = pd.read_csv(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})
            st.session_state.original_df = df.copy() # original data
            st.session_state.df = df.copy() # ini working copy yang user akan pake
            # st.session_state.custom_dtypes = {col: str(df[col].dtype) for col in df.columns}
            st.session_state.change_history = []
            st.success("Dataset loaded successfully. Click button below to transform the data")

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
            st.dataframe(df_original)

            info_df = pd.DataFrame({"Column": df_original.columns,
                                    "Non-Null Count": df_original.notnull().sum().values,
                                    "Null Count":df_original.isna().sum().values,
                                    "Dtype": df_original.dtypes.values})

            st.write("**Column Names and Data Types:**")
            st.dataframe(info_df)
            
            st.success("Done exploring. Clean the data by clicking button below")

            # 3. CLEAN DATA
            # indent: 3
            if st.button('Clean Data ⏭️'):
                st.session_state['clean_clicked'] = True
            if st.session_state['clean_clicked']:
                st.markdown("---")
                st.subheader('✨ 3. Data Cleaning')
                df = st.session_state.df
                
                string_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
                
                st.markdown("""
                **Cleaning for ‘string’ data type:**
                - Remove accessing space
                """)

                if st.button("Clean for string"):
                    for col in string_cols:
                        df[col] = (df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.upper())
                    st.success("✅ String fields cleaned!")
                        
                # 4. TRANSFORM DATA
                # indent: 4
                st.markdown("")
                if st.button('Transform Data ⏭️'):
                    st.session_state['transform_clicked'] = True

                if st.session_state['transform_clicked']:
                    st.markdown("---")
                    st.subheader('🔄 4. Data Transformation')
                    df = st.session_state.df
            
                    if "change_history" not in st.session_state:
                        st.session_state.change_history = []

                    transform_opt = ['KTP/ID Validation', 'Phone Number Validation', 'Tahun Periode Polis',
                                    'Age (current)', 'Age (order)', 'Age Group (current)', 'Age Group (order)','Post Code', 'Kecamatan', 'Kota/Kab.', 'Provinsi',
                                    'Chassis Number', 'Gross Premi/Year', 'Grouping Gross Premi/Year', 'Grouping Sum Insured']
            
                    selected_column = st.selectbox("Transformation Options", options=[""] + transform_opt)
                    if selected_column:
                                                    
                            # ON PROGRESS
                            if selected_column == "KTP/ID Validation":
                                st.markdown("""
                                `KTP/ID Validation` needs `KTP/ID` and `BirthDate/DoB` column and will do this validation:
                                - Length validation (16 digits)
                                - Read gender from the 7th and 8th digit (if > 40 = female)
                                - Read birthdate from the 7th until 12th digit
                                - Match the extracted birthdate and birthdate from the data
                                """)
                                ktp = st.selectbox("Choose field that represents `KTP`", options=[""] + list(df.columns))
                                dob_data = st.selectbox("Choose field that represents `DoB`", options=[""] + list(df.columns))
                                gender_data = st.selectbox("Choose field that represents `gender`", options=[""] + list(df.columns))
                                
                                if ktp:
                                    if st.button("Validate KTP"):
                                        df_ktp =df.copy()
                                        
                                        def ktp_val(ktp):
                                            if pd.isna(ktp) or ktp == "NAN" or ktp == "NA":
                                                return "Invalid: empty", "NA", "NA"
                                            ktp = str(ktp).strip()
                                            ktp = re.sub(r"\s+", " ", ktp)
                                            ktp = re.sub(r"\..*$", "", ktp)
                                            
                                            if not len(ktp) == 16:
                                                return "Invalid: Length", "NA", "NA"

                                            elif ktp[0] == '0':
                                                return "Invalid: Wrong format", "NA", "NA"
                                            elif ktp[:2] == '97' or ktp[:2] == "98" or ktp[:2] == "99" or ktp[:2] == "10":
                                                return "Invalid: Wrong format", "NA", "NA"
                                                
                                            else:
                                                day = int(ktp[6:8])
                                            
                                                if day >= 40:
                                                    day -= 40
                                                    month = int(ktp[8:10])
                                                    year_suffix = int(ktp[10:12])
                                                    year = 1900 + year_suffix if year_suffix >= 40 else 2000 + year_suffix
                                                    dob = f"{day:02d}/{month:02d}/{year}"
                                                    dob = pd.to_datetime(dob, errors="coerce", dayfirst=True)
                                                    return ktp, "F", dob
                                    
                                                month = int(ktp[8:10])
                                                year_suffix = int(ktp[10:12])
                                                year = 1900 + year_suffix if year_suffix >= 40 else 2000 + year_suffix
                                                dob = f"{day:02d}/{month:02d}/{year}"
                                                dob = pd.to_datetime(dob, errors="coerce", dayfirst=True)
                                            
                                                return ktp, "M", dob
                                    
                                        df_ktp[f"{ktp}_val"] = df_ktp[ktp].apply(lambda x: ktp_val(x)[0])
                                        df_ktp["Gender KTP"] = df_ktp[ktp].apply(lambda x: ktp_val(x)[1])
                                        df_ktp["DoB KTP"] = df_ktp[ktp].apply(lambda x: ktp_val(x)[2])
                                        
                                        df_ktp["DoB KTP"] = pd.to_datetime(df_ktp["DoB KTP"], errors="coerce")
                                        df_ktp[dob_data] = pd.to_datetime(df_ktp[dob_data], errors="coerce")
                                        
                                        df_ktp["DoB Match"] = df_ktp["DoB KTP"].dt.date == df_ktp[dob_data].dt.date
                                        df_ktp["DoB Match"] = df_ktp["DoB Match"].map({True: "Yes", False: "No"})
                                        df_ktp["Gender Match"] = df_ktp["Gender KTP"] == df_ktp[gender_data]
                                        df_ktp["Gender Match"] = df_ktp["Gender Match"].map({True: "Yes", False: "No"})
                                
                                        st.session_state.df = df_ktp

                                        st.success("KTP validation complete")
                            
                                        st.dataframe(df_ktp[[ktp,f"{ktp}_val", dob_data, "DoB KTP", "DoB Match", gender_data, "Gender KTP", "Gender Match"]])
                                        st.session_state.change_history.append(
                                            "• Field `KTP Validation` created"
                                        )       
                                
                            # DONE
                            if selected_column == "Phone Number Validation":
                                st.markdown("""
                                `Phone Number Validation` needs `Phone Number` column and will do this validation:
                                - Change all prefix into '08xxx'
                                - Fill '0' to more than 5 digits serial number (e.g. 000000xxx)
                                - Length validation between 10-13 digits
                                """)
                                phone_col = st.selectbox("Choose field that represents `phone number`", options=[""] + list(df.columns))
                                if phone_col:
                                    if st.button("Validate phone number"):
                                        df_validated = df.copy()
                                        def validate_phone(phone):
                                            if pd.isna(phone):
                                                return "NA","Invalid: empty"
                                            phone = str(phone)
                                            phone = re.sub(r'\D','',phone)
                                            if phone == '0':
                                                return "NA", "Invalid: empty"
                                            if phone.startswith("62"):
                                                phone = "0" + phone[2:]
                                            elif phone.startswith("+62"):
                                                phone = "0" + phone[3:]
                                            elif phone.startswith("8"):
                                                phone = "0" + phone
                                            # HARUSNYA YG '0' SAMA EMPTY SAMA NA DISAMAIN DULU JADI = NA (?)
                                            if re.search(r'(\d)\1{5,}', phone):
                                                return "NA", 'Invalid: repeated digits'
                                            if phone == "NAN":
                                                return "NA", "Invalid: empty"
                                            if not 10 <= len(phone) <= 13:
                                                return "NA", "Invalid: Length"

                                            return phone, "Valid"
                                            
                                        df_validated[f"{phone_col}_new"] = df_validated[phone_col].apply(lambda x: validate_phone(x)[0])
                                        df_validated[f"{phone_col}_status"] = df_validated[phone_col].apply(lambda x:validate_phone(x)[1])
                                        st.session_state.df = df_validated
                                        st.success("Phone number validation complete")
                                        st.dataframe(df_validated[[phone_col,f"{phone_col}_new",f"{phone_col}_status"]])
                                        st.session_state.change_history.append(
                                            "• Field `Phone Number Validation` created"
                                        )
                        
                            # DONE
                            if selected_column == "Tahun Periode Polis":
                                st.markdown("""
                                `Tahun Periode Polis` needs `Period From` and `Period To` column and will do this calculation:
                                - (Period To - Period From)/365 
                                """)
                                period_from = st.selectbox("Choose field that represents `period from`", options=[""] + list(df.columns))
                                period_to = st.selectbox("Choose field that represents `period to`", options=[""] + list(df.columns))
                                if period_from and period_to:
                                    if st.button("Calculate tahun periode polis"):
                                        try:
                                            df_calc = df.copy()
                                            df_calc[period_from] = pd.to_datetime(df_calc[period_from], errors='coerce')
                                            df_calc[period_to] = pd.to_datetime(df_calc[period_to], errors='coerce')
                                            df_calc["Tahun periode polis"] = (df_calc[period_to] - df_calc[period_from]).dt.days/365
                                            df_calc["Tahun periode polis"] = df_calc["Tahun periode polis"].round(1)
                                            st.dataframe(df_calc[[period_from, period_to, "Tahun periode polis"]])

                                            st.session_state.df = df_calc
                                            st.success("`Tahun periode polis` successfully calculated and stored")
                                            st.session_state.change_history.append(
                                            "• Field `Tahun Periode Polis` created"
                                            )
                                        except Exception as e:
                                            st.error(f"Error calculating tahun {e}")

                            # DONE
                            if selected_column == "Age (current)":
                                st.markdown("""
                                `Age (current)` needs `Birth Date` column and will do this calculation:
                                - Date today-Birth date
                                """)
                                dob = st.selectbox("Choose field that represents `birth date`", options=[""] + list(df.columns))
                                if dob:
                                    if st.button("Calculate current age"):
                                        try:
                                            df_age = df.copy()
                                            df_age[dob] = pd.to_datetime(df_age[dob], errors='coerce')
                                            today = pd.to_datetime("today")
                                            df_age["Age (current)"] = (today - df_age[dob]).dt.days / 365.25
                                            df_age["Age (current)"] = df_age["Age (current)"].round(0)
                                    
                                            df_age["Age (current)"].loc[df_age["Age (current)"] > 99] = 0
                                            df_age["Age (current)"].loc[df_age["Age (current)"] < 17] = 0
                                    
                                            st.dataframe(df_age[[dob, "Age (current)"]])
                                            st.session_state.df = df_age
                                            st.success("Age (current) successfully calculated and stored")
                                            st.session_state.change_history.append(
                                            "• Field `Age (current)` created"
                                            )
                                        except Exception as e:
                                            st.error(f"Error calculating age (current) {e}")
                            
                            if selected_column == "Age Group (current)":
                                st.markdown("""
                                `Age Group (current)` needs `Age (current)` column and will gorup it based on this range:
                                - 18-24
                                - 25-34
                                - 35-44
                                - 45-54
                                - 55-64
                                - 65+
                                """)
                                age_group = st.selectbox("Choose field that represents `Age (current)`", options=[""] + list(df.columns))
                                if age_group:
                                    if st.button("Group age (current)"):
                                        try:
                                            df_age_group = df.copy()
                                            df_age_group[age_group] = df_age_group[age_group].astype(int)
                                            df_age_group["Age group (current)"] = ""
                                            df_age_group.loc[(df_age_group[age_group] > 17) & (df_age_group[age_group] < 25), "Age group (current)"] = "18-24"
                                            df_age_group.loc[(df_age_group[age_group] > 24) & (df_age_group[age_group] < 35), "Age group (current)"] = "25-34"
                                            df_age_group.loc[(df_age_group[age_group] > 34) & (df_age_group[age_group] < 45), "Age group (current)"] = "35-44"
                                            df_age_group.loc[(df_age_group[age_group] > 44) & (df_age_group[age_group] < 55), "Age group (current)"] = "45-54"
                                            df_age_group.loc[(df_age_group[age_group] > 54) & (df_age_group[age_group] < 65), "Age group (current)"] = "55-64"
                                            df_age_group.loc[df_age_group[age_group] >= 65, "Age group (current)"] = "65+"
                                            df_age_group.loc[df_age_group[age_group] == 0, "Age group (current)"] = "NA"
                                            st.dataframe(df_age_group[[age_group, "Age group (current)"]])
                                            st.session_state.df = df_age_group
                                            st.success("Age group (current) successfully calculated and stored")
                                            st.session_state.change_history.append(
                                            "• Field `Age Group (current)` created"
                                            )
                                        except Exception as e:
                                            st.error(f"Error calculating age {e}")
                                            
                            if selected_column == "Age (order)":
                                st.markdown("""
                                `Age (order)` needs `Birth Date` and `Policy Order Date`/`Period From` column and will do this calculation:
                                - Policy order date - birth date
                                """)
                                dob = st.selectbox("Choose field that represents `birth date`", options=[""] + list(df.columns))
                                policy = st.selectbox("Choose field that represents `policy order date`/`period from`", options=[""] + list(df.columns))
                                if dob:
                                    if st.button("Calculate age based on order"):
                                        try:
                                            df_age = df.copy()
                                            df_age[dob] = pd.to_datetime(df_age[dob], errors='coerce')
                                            df_age[policy] = pd.to_datetime(df_age[policy], errors='coerce')
                                            
                                            df_age["Age (order)"] = (df_age[policy] - df_age[dob]).dt.days / 365.25
                                            df_age["Age (order)"] = df_age["Age (order)"].round(0)
                                    
                                            df_age["Age (order)"].loc[df_age["Age (order)"] > 99] = 0
                                            df_age["Age (order)"].loc[df_age["Age (order)"] < 17] = 0
                                    
                                            st.dataframe(df_age[[dob, policy, "Age (order)"]])
                                            st.session_state.df = df_age
                                            st.success("Age (order) successfully calculated and stored")
                                            st.session_state.change_history.append(
                                            "• Field `Age (order)` created"
                                            )
                                        except Exception as e:
                                            st.error(f"Error calculating age (order) {e}")
                                            
                            if selected_column == "Age Group (order)":
                                st.markdown("""
                                `Age Group (order)` needs `Age (order)` column and will gorup it based on this range:
                                - 18-24
                                - 25-34
                                - 35-44
                                - 45-54
                                - 55-64
                                - 65+
                                """)
                                age_group = st.selectbox("Choose field that represents `Age (order)`", options=[""] + list(df.columns))
                                if age_group:
                                    if st.button("Group age (order)"):
                                        try:
                                            df_age_group = df.copy()
                                            df_age_group[age_group] = df_age_group[age_group].astype(int)
                                            df_age_group["Age group (order)"] = ""
                                            df_age_group.loc[(df_age_group[age_group] > 17) & (df_age_group[age_group] < 25), "Age group (order)"] = "18-24"
                                            df_age_group.loc[(df_age_group[age_group] > 24) & (df_age_group[age_group] < 35), "Age group (order)"] = "25-34"
                                            df_age_group.loc[(df_age_group[age_group] > 34) & (df_age_group[age_group] < 45), "Age group (order)"] = "35-44"
                                            df_age_group.loc[(df_age_group[age_group] > 44) & (df_age_group[age_group] < 55), "Age group (order)"] = "45-54"
                                            df_age_group.loc[(df_age_group[age_group] > 54) & (df_age_group[age_group] < 65), "Age group (order)"] = "55-64"
                                            df_age_group.loc[df_age_group[age_group] >= 65, "Age group (order)"] = "65+"
                                            df_age_group.loc[df_age_group[age_group] == 0, "Age group (order)"] = "NA"
                                            st.dataframe(df_age_group[[age_group, "Age group (order)"]])
                                            st.session_state.df = df_age_group
                                            st.success("Age group (order) successfully calculated and stored")
                                            st.session_state.change_history.append(
                                            "• Field `Age Group (order)` created"
                                            )
                                        except Exception as e:
                                            st.error(f"Error calculating age {e}")
                            # indent 7
                            if selected_column == "Post Code":
                                st.markdown("""
                                `Post Code` needs `Address` column and will detect the valid 5 digit number (ignore repeated patterns like 00000).
                                """)
                                post_code = st.selectbox("Choose field that represents address", options=[""] + list(df.columns))
                                if post_code:
                                    if st.button("Extract post code"):
                                        df_post = df.copy()
                                        def extract_postcode(text):
                                            if pd.isna(text):
                                                return ""
                                            text = str(text)
                                            matches = re.findall(r"\b\d{5}\b", text)
                                            for code in matches:
                                                if len(set(code)) > 2:
                                                    return code
                                            return ""
                                        df_post["Post Code"] = df_post[post_code].apply(extract_postcode)
                                        st.dataframe(df_post[[post_code, "Post Code"]])
                                        st.session_state.df = df_post
                                        st.success("Post code extracted successfully")
                                        st.session_state.change_history.append(
                                            "• Field `Post Code` created"
                                        )

                            if selected_column == "Kota/Kab.":
                                st.markdown("""
                                `Kota/Kab.` needs `Post Code` column and will do the mapping.
                                """)
                                kota = st.selectbox("Choose field that represents post code", options=[""] + list(df.columns))
                                if kota:
                                    if st.button("City mapping"):
                                        df_kota = df.copy()
                                        kodepos = {
                                    '236' : 'Kab. Aceh Barat', '2376':'Kab. Aceh Barat Daya', '233' : 'Kab. Aceh Besar', '234' : 'Kab. Aceh Besar','235' : 'Kab. Aceh Besar',
                                           '236' : 'Kab. Aceh Besar','237' : 'Kab. Aceh Besar', '238' : 'Kab. Aceh Besar', '239' : 'Kab. Aceh Besar',
                                    '2365' : 'Kab. Aceh Jaya', '237': 'Kab. Aceh Selatan', '247': 'Kab. Aceh Singkil','2447': 'Kab. Aceh Tamiang','245': 'Kab. Aceh Tengah','2466': 'Kab. Aceh Tenggara',
                                    '2467': 'Kab. Aceh Tenggara','2444': 'Kab. Aceh Timur','2445': 'Kab. Aceh Timur','2446': 'Kab. Aceh Timur','243': 'Kab. Aceh Utara',
                                    '2615': 'Kab. Agam','2647': 'Kab. Agam', '858': 'Kab. Alor','971': 'Ambon','972': 'Ambon','212': 'Kab. Asahan','213': 'Kab. Asahan',
                                    '9977': 'Kab. Asmat','9978': 'Kab. Asmat','9979': 'Kab. Asmat', '803': 'Kab. Badung','716': 'Kab. Balangan','761': 'Balikpapan','231': 'Banda Aceh',
                                    '232': 'Banda Aceh', '351': 'Bandar Lampung','352': 'Bandar Lampung','401': 'Bandung',
                                    '402': 'Bandung', '403': 'Kab. Bandung Barat','404': 'Kab. Bandung Barat','405': 'Kab. Bandung Barat', '406': 'Bandung','407': 'Bandung',
                                    '409': 'Bandung', '947': 'Kab. Banggai', '948': 'Kab. Banggai Kepulauan', '9489': 'Kab. Banggai Laut', '3317': 'Kab. Bangka', '332': 'Kab. Bangka',
                                    '333': 'Kab. Bangka Barat', '337': 'Kab. Bangka Selatan', '336': 'Kab. Bangka Tengah', '691': 'Kab. Bangkalan', '806': 'Kab. Bangli','463': 'Banjar',
                                    '706': 'Kab. Banjar',
    '707': 'Banjarbaru',
    '701': 'Banjarmasin',
    '702': 'Banjarmasin',
    '534': 'Kab. Banjarnegara',
    '924': 'Kab. Bantaeng',
    '551': 'Kab. Bantul',
    '552': 'Kab. Bantul',
    '553': 'Kab. Bantul',
    '554': 'Kab. Bantul',
    '555': 'Kab. Bantul',
    '556': 'Kab. Bantul',
    '557': 'Kab. Bantul',
    '309': 'Kab. Banyuasin',
    '531': 'Kab. Banyumas',
    '684': 'Kab. Banyuwangi',
    '705': 'Kab. Barito Kuala',
    '737': 'Kab. Barito Selatan',
    '736': 'Kab. Barito Timur',
    '738': 'Kab. Barito Utara',
    '907': 'Kab. Barru',
    '294': 'Batam',
    '512': 'Kab. Batang',
    '366': 'Kab. Batanghari',
    '653': 'Batu',
    '2125': 'Kab. Batu Bara',
    '9371': 'Bau Bau',
    '9372': 'Bau Bau',
    '9373': 'Bau Bau',
    '171': 'Bekasi',
    '172': 'Kab. Bekasi',
    '173': 'Kab. Bekasi',
    '174': 'Kab. Bekasi',
    '175': 'Kab. Bekasi',
    '176': 'Kab. Bekasi',
    '177': 'Kab. Bekasi',
    '334': 'Kab. Belitung',
    '335': 'Kab. Belitung Timur',
    '857': 'Kab. Belu',
    '245': 'Kab. Bener Meriah',
    '287': 'Kab. Bengkalis',
    '791': 'Kab. Bengkayang',
    '792': 'Kab. Bengkayang',
    '381': 'Bengkulu',
    '382': 'Bengkulu',
    '385': 'Kab. Bengkulu Selatan',
    '383': 'Kab. Bengkulu Tengah',
    '384': 'Kab. Bengkulu Utara',
    '386': 'Kab. Bengkulu Utara',
    '773': 'Kab. Berau',
    '9851': 'Kab. Biak Numfor',
    '9852': 'Kab. Biak Numfor',
    '9853': 'Kab. Biak Numfor',
    '9854': 'Kab. Biak Numfor',
    '9855': 'Kab. Biak Numfor',
    '9856': 'Kab. Biak Numfor',
    '841': 'Kab. Bima',
    '2071': 'Binjai',
    '2072': 'Binjai',
    '2073': 'Binjai',
    '2074': 'Binjai',
    '2913': 'Kab. Bintan',
    '2914': 'Kab. Bintan',
    '2915': 'Kab. Bintan',
    '2916': 'Kab. Bintan',
    '2917': 'Kab. Bintan',
    '2918': 'Kab. Bintan',
    '2919': 'Kab. Bintan',
    '242': 'Kab. Bireuen',
    '243': 'Kab. Bireuen',
    '955': 'Bitung',
    '6615': 'Kab. Blitar',
    '6616': 'Kab. Blitar',
    '6617': 'Kab. Blitar',
    '6618': 'Kab. Blitar',
    '6619': 'Kab. Blitar',
    '6611': 'Blitar',
    '6612': 'Blitar',
    '6613': 'Blitar',
    '582': 'Kab. Blora',
    '583': 'Kab. Blora',
    '9626': 'Kab. Boalemo',
    '161': 'Kab. Bogor',
    '162': 'Kab. Bogor',
    '163': 'Kab. Bogor',
    '164': 'Kab. Bogor',
    '165': 'Kab. Bogor',
    '166': 'Kab. Bogor',
    '167': 'Kab. Bogor',
    '168': 'Kab. Bogor',
    '169': 'Kab. Bogor',
    '161': 'Bogor', '162': 'Bogor', '163': 'Bogor', '164': 'Bogor', '165': 'Bogor', '166': 'Bogor',
    '621': 'Kab. Bojonegoro',
    '9573': 'Kab. Bolaang Mongondow', '9574': 'Kab. Bolaang Mongondow', '9575': 'Kab. Bolaang Mongondow',
    '9577': 'Kab. Bolaang Mongondow Selatan',
    '9578': 'Kab. Bolaang Mongondow Timur',
    '9576': 'Kab. Bolaang Mongondow Utara',
    '9377': 'Kab. Bombana', '9378': 'Kab. Bombana',
    '682': 'Kab. Bondowoso',
    '902': 'Kab. Bone', '903': 'Kab. Bone', '904': 'Kab. Bone', '905': 'Kab. Bone', '906': 'Kab. Bone', '907': 'Kab. Bone', '908': 'Kab. Bone', '909': 'Kab. Bone', '910': 'Kab. Bone', '911': 'Kab. Bone', '912': 'Kab. Bone', '913': 'Kab. Bone', '914': 'Kab. Bone', '915': 'Kab. Bone', '916': 'Kab. Bone', '917': 'Kab. Bone', '918': 'Kab. Bone', '919': 'Kab. Bone', '920': 'Kab. Bone', '921': 'Kab. Bone', '922': 'Kab. Bone', '923': 'Kab. Bone', '924': 'Kab. Bone', '925': 'Kab. Bone', '926': 'Kab. Bone', '927': 'Kab. Bone',
    '9654': 'Kab. Bone Bolango', '9655': 'Kab. Bone Bolango', '9656': 'Kab. Bone Bolango', '9657': 'Kab. Bone Bolango',
    '753': 'Bontang',
    '9965': 'Kab. Boven Digoel', '9966': 'Kab. Boven Digoel', '9967': 'Kab. Boven Digoel', '9968': 'Kab. Boven Digoel', '9969': 'Kab. Boven Digoel',
    '573': 'Kab. Boyolali',
    '522': 'Kab. Brebes',
    '2611': 'Bukittinggi', '2612': 'Bukittinggi', '2613': 'Bukittinggi',
    '811': 'Kab. Buleleng',
    '925': 'Kab. Bulukumba',
    '772': 'Kab. Bulungan',
    '372': 'Kab. Bungo',
    '9456': 'Kab. Buol', '9457': 'Kab. Buol',
    '9757': 'Kab. Buru',
    '9754': 'Kab. Buru Selatan',
    '9375': 'Kab. Buton',
    '9374': 'Kab. Buton Selatan',
    '9376': 'Kab. Buton Tengah',
    '9367': 'Kab. Buton Utara',
    '462': 'Kab. Ciamis', '463': 'Kab. Ciamis',
    '432': 'Kab. Cianjur',
    '532': 'Kab. Cilacap',
    '424': 'Cilegon',
    '405': 'Cimahi',
    '451': 'Cirebon',
    '452': 'Kab. Cirebon', '453': 'Kab. Cirebon', '454': 'Kab. Cirebon', '455': 'Kab. Cirebon', '456': 'Kab. Cirebon',
    '222': 'Kab. Dairi',
    '9875': 'Kab. Deiyai', '9876': 'Kab. Deiyai', '9877': 'Kab. Deiyai',
    '203': 'Kab. Deli Serdang', '204': 'Kab. Deli Serdang', '205': 'Kab. Deli Serdang',
    '595': 'Kab. Demak',
    '801': 'Denpasar', '802': 'Denpasar',
    '164': 'Depok', '165': 'Depok',
    '275': 'Kab. Dharmasraya', '276': 'Kab. Dharmasraya',
    '9887': 'Kab. Dogiyai', '9888': 'Kab. Dogiyai',
    '842': 'Kab. Dompu',
    '9434': 'Kab. Donggala', '9435': 'Kab. Donggala',
    '288': 'Dumai',
    '314': 'Kab. Empat Lawang', '315': 'Kab. Empat Lawang',
    '861': 'Kab. Ende', '862': 'Kab. Ende', '863': 'Kab. Ende',
    '917': 'Kab. Enrekang',
    '9801': 'Kab. Fak Fak', '9802': 'Kab. Fak Fak', '9803': 'Kab. Fak Fak',
    '862': 'Kab. Flores Timur',
    '441': 'Kab. Garut',
    '2465': 'Kab. Gayo Lues',
    '805': 'Kab. Gianyar',
        '9615': 'Kab. Gorontalo', '9624': 'Kab. Gorontalo',
    '9611': 'Gorontalo', '9612': 'Gorontalo',
    '9613': 'Gorontalo',  
    '9651': 'Kab. Gorontalo Utara', '9652': 'Kab. Gorontalo Utara','902': 'Kab. Gowa','921': 'Kab. Gowa',           
    '611': 'Kab. Gresik',
    '581': 'Kab. Grobogan',
                                    '745': 'Kab. Gunung Mas', '558': 'Kab. Gunungkidul',
    '228': 'Gunungsitoli',
    '9775': 'Kab. Halmahera Barat', '9778': 'Kab. Halmahera Selatan', '9779': 'Kab. Halmahera Selatan',
    '9785': 'Kab. Halmahera Tengah',
    '9786': 'Kab. Halmahera Timur',
    '9776': 'Kab. Halmahera Utara',
    '712': 'Kab. Hulu Sungai Selatan',
    '713': 'Kab. Hulu Sungai Tengah',
    '714': 'Kab. Hulu Sungai Utara',
    '224': 'Kab. Humbang Hasundutan',
    '292': 'Kab. Indragiri Hilir',
    '293': 'Kab. Indragiri Hulu',
    '452': 'Kab. Indramayu',
    '9878': 'Kab. Intan Jaya', '9879': 'Kab. Intan Jaya',
    '111': 'Jakarta Barat',  '112': 'Jakarta Barat',
    '113': 'Jakarta Barat',  '114': 'Jakarta Barat',
    '115': 'Jakarta Barat',  '116': 'Jakarta Barat',
     '117': 'Jakarta Barat',  '118': 'Jakarta Barat',
     '101': 'Jakarta Pusat', '102': 'Jakarta Pusat',
    '103': 'Jakarta Pusat', '104': 'Jakarta Pusat',
    '105': 'Jakarta Pusat', '106': 'Jakarta Pusat',
    '107': 'Jakarta Pusat',
    '121': 'Jakarta Selatan', '122': 'Jakarta Selatan',
    '123': 'Jakarta Selatan', '124': 'Jakarta Selatan',
    '125': 'Jakarta Selatan', '126': 'Jakarta Selatan',
    '127': 'Jakarta Selatan', '128': 'Jakarta Selatan',
    '129': 'Jakarta Selatan',
    '131': 'Jakarta Timur', '132': 'Jakarta Timur',
    '133': 'Jakarta Timur', '134': 'Jakarta Timur',
    '135': 'Jakarta Timur', '136': 'Jakarta Timur',
    '137': 'Jakarta Timur', '138': 'Jakarta Timur',
    '139': 'Jakarta Timur',
    '141': 'Jakarta Utara', '142': 'Jakarta Utara',
    '143': 'Jakarta Utara', '144': 'Jakarta Utara',
    '361': 'Jambi', '362': 'Jambi',
    '9935': 'Kab. Jayapura', '9936': 'Kab. Jayapura',
    '9911': 'Jayapura', '9933': 'Jayapura',
    '9950': 'Kab. Jayawijaya', '9951': 'Kab. Jayawijaya',
    '9952': 'Kab. Jayawijaya', '9953': 'Kab. Jayawijaya',
    '9954': 'Kab. Jayawijaya', '9955': 'Kab. Jayawijaya',
    '681': 'Kab. Jember', '822': 'Kab. Jembrana',
    '923': 'Kab. Jeneponto', '924': 'Kab. Jeneponto',
    '925': 'Kab. Jeneponto', '594': 'Kab. Jepara',
    '614': 'Kab. Jombang', '9811': 'Kab. Kaimana',
    '9812': 'Kab. Kaimana', '284': 'Kab. Kampar',
    '735': 'Kab. Kapuas', '745': 'Kab. Kapuas',
    '787': 'Kab. Kapuas Hulu', '571': 'Kab. Karanganyar',
    '572': 'Kab. Karanganyar', '573': 'Kab. Karanganyar',
    '574': 'Kab. Karanganyar', '575': 'Kab. Karanganyar',
    '576': 'Kab. Karanganyar', '577': 'Kab. Karanganyar',
    '808': 'Kab. Karangasem', '413': 'Kab. Karawang',
    '296': 'Kab. Karimun', '221': 'Kab. Karo',
    '744': 'Kab. Katingan', '389': 'Kab. Kaur', '788': 'Kab. Kayong Utara',
    '543': 'Kab. Kebumen', '544': 'Kab. Kebumen', '642': 'Kab. Kediri', '641': 'Kediri', # 182 (lanjut ke yg sering dulu)
                                            '145': 'Kab. Kepulauan Seribu', '593': 'Kab. Kudus', '455': 'Kab. Kuningan',
                                            '641': 'Kab. Kediri', '561': 'Magelang', '562': 'Kab. Magelang',
                                            '563': 'Kab. Magelang', '564': 'Kab. Magelang', '565': 'Kab. Magelang', 
                                            '901': 'Makassar', '902': 'Makassar', '6511': 'Malang', '6512': 'Malang',
                                            '6513': 'Malang', '6514': 'Malang', '6515': 'Kab. Malang', '6516': 'Kab. Malang', '6517': 'Kab. Malang', '6518': 'Kab. Malang', '6519': 'Kab. Malang', '251': 'Padang', '252': 'Padang',
                                            '301': 'Palembang', '302': 'Palembang', '941': 'Palu', '942': 'Palu',
                                            '281': 'Pekanbaru', '282': 'Pekanbaru',  '781': 'Pontianak', '782': 'Pontianak', '411': 'Purwakarta', '1511': 'Tangerang','1512': 'Tangerang', '1513': 'Tangerang', '1514': 'Tangerang', '1515': 'Tangerang', '158': 'Kab. Tangerang', '152': 'Tangerang Selatan','153': 'Tangerang Selatan','154': 'Tangerang Selatan', '551': 'Yogyakarta','552': 'Yogyakarta', '521': 'Tegal', '522': 'Kab. Tegal', '523': 'Kab. Tegal', '524': 'Kab. Tegal'
                                        }
                                        def map_postal_code(postal):
                                            if pd.isna(postal) or postal=="NA" or postal=="NAN" or postal==0 or postal=="" or postal==None or postal=="0":
                                                return "NA"
                                            postal = str(postal)
                                            prefix3 = postal[:3]  
                                            if prefix3 in kodepos:
                                                return kodepos[prefix3]
                                            prefix4 = postal[:4]
                                            if prefix4 in kodepos:
                                                return kodepos[prefix4]
                                            #return kodepos.get(prefix3, postal) 
                                            return "Unknown"
                                            
                                        df_kota['Kota/Kab.'] = df_kota[kota].apply(map_postal_code)
                                        st.dataframe(df_kota[[kota, "Kota/Kab."]])
                                        st.session_state.df = df_kota
                                        st.success("Kota mapped successfully")
                                        st.session_state.change_history.append(
                                            "• Field `Kota/Kab.` created"
                                        )
                            # indent 7
                            if selected_column == "Provinsi":
                                st.markdown("""
                                `Provinsi` needs `Post Code` column and will do the mapping.
                                """)
                                prov = st.selectbox("Choose field that represents `post code`", options=[""] + list(df.columns))
                                if prov:
                                    if st.button("Provinsi mapping"):
                                        df_prov = df.copy()
                                        kode_pos_prov = {'23':'Aceh', '24':'Aceh', '80':'Bali', '81':'Bali', '82':'Bali', '15':'Banten', '42':'Banten', '38':'Bengkulu',
                                                 '39':'Bengkulu', '55':'DI Yogyakarta','10':'DKI Jakarta', '11':'DKI Jakarta', '12':'DKI Jakarta',
                                                 '13':'DKI Jakarta', '14':'DKI Jakarta','96':'Gorontalo','36':'Jambi', '37':'Jambi',
                                                 '16':'Jawa Barat', '17':'Jawa Barat', '40': 'Jawa Barat',
                                                 '41':'Jawa Barat', '42':'Jawa Barat', '43':'Jawa Barat', '44':'Jawa Barat', '45':'Jawa Barat', '46':'Jawa Barat',
                                                 '50':'Jawa Tengah','51':'Jawa Tengah','52':'Jawa Tengah','53':'Jawa Tengah','54':'Jawa Tengah', '56':'Jawa Tengah',
                                                 '57':'Jawa Tengah', '58':'Jawa Tengah', '59':'Jawa Tengah', '60':'Jawa Timur', '61':'Jawa Timur',
                                                 '62':'Jawa Timur', '63':'Jawa Timur','64':'Jawa Timur', '65':'Jawa Timur', '66':'Jawa Timur',
                                                 '67':'Jawa Timur', '68':'Jawa Timur', '69':'Jawa Timur', '78':'Kalimantan Barat', '79':'Kalimantan Barat',
                                                 '70':'Kalimantan Selatan','71':'Kalimantan Selatan','72':'Kalimantan Selatan','73':'Kalimantan Tengah','74':'Kalimantan Tengah',
                                                 '751':'Kalimantan Timur', '752':'Kalimantan Timur', '762':'Kalimantan Timur', '773':'Kalimantan Timur', '755':'Kalimantan Timur', '753':'Kalimantan Timur', '754':'Kalimantan Timur','761':'Kalimantan Timur', '756':'Kalimantan Timur', '757':'Kalimantan Timur', '758':'Kalimantan Timur', '759':'Kalimantan Timur', '760':'Kalimantan Timur',
                                                 '773':'Kalimantan Timur', '771': 'Kalimantan Utara', '772':'Kalimantan Utara', '774':'Kalimantan Utara', '775':'Kalimantan Utara',
                                                 '33':'Kep. Bangka Belitung', '29':'Kep. Riau', '34':'Lampung', '35':'Lampung', '971':'Maluku', '972':'Maluku', '973':'Maluku', 
                                                 '974':'Maluku', '975':'Maluku', '976':'Maluku', '977':'Maluku Utara', '978':'Maluku Utara', '83':'NTB', '84':'NTB',
                                                 '85':'NTT','86':'NTT','87':'NTT', '985':'Papua', '994':'Papua',# PAPUA semua ?
                                                 '980':'Papua Barat', '981':'Papua Barat', '982':'Papua Barat Daya','983':'Papua Barat','984':'Papua Barat Daya',
                                                 '990':'Papua Pegunungan','991':'Papua Pegunungan','992':'Papua Pegunungan','993':'Papua Pegunungan','994':'Papua Pegunungan',
                                                 '995':'Papua Pegunungan','999':'Papua Pegunungan', '996':'Papua Selatan','997':'Papua Selatan','997':'Papua Selatan',
                                                 '987':'Papua Tengah', '988':'Papua Tengah', # papua tgh belum semua (papua pegunungan sama papua tengah beririsan
                                                 '28':'Riau','29':'Riau','913':'Sulawesi Barat','914':'Sulawesi Barat','915':'Sulawesi Barat',
                                                 '901':'Sulawesi Selatan', '902':'Sulawesi Selatan',  '903':'Sulawesi Selatan', '904':'Sulawesi Selatan',
                                                 '905':'Sulawesi Selatan', '906':'Sulawesi Selatan', '907':'Sulawesi Selatan', '908':'Sulawesi Selatan', '909':'Sulawesi Selatan',
                                                 '910':'Sulawesi Selatan', '911':'Sulawesi Selatan', '912':'Sulawesi Selatan', '916':'Sulawesi Selatan', '917':'Sulawesi Selatan', '918':'Sulawesi Selatan', '919':'Sulawesi Selatan',
                                                 '920':'Sulawesi Selatan', '921':'Sulawesi Selatan', '922':'Sulawesi Selatan', '923':'Sulawesi Selatan', '924':'Sulawesi Selatan', '925':'Sulawesi Selatan', '926':'Sulawesi Selatan',
                                                 '929':'Sulawesi Selatan', '927':'Sulawesi Selatan', '928':'Sulawesi Selatan',
                                                 '94':'Sulawesi Tengah', '93':'Sulawesi Tenggara', '95':'Sulawesi Utara','25':'Sumatera Barat','26':'Sumatera Barat',
                                                 '27':'Sumatera Barat','30':'Sumatera Selatan','31':'Sumatera Selatan','32':'Sumatera Selatan',
                                                 '20':'Sumatera Utara','21':'Sumatera Utara','22':'Sumatera Utara'
                                                }
                                        def map_postal_code(postal):
                                            if pd.isna(postal) or postal=="NA" or postal=="NAN" or postal==0 or postal=="" or postal==None or postal=="0":
                                                return "NA"
                                            postal = str(postal)
                                            prefix3 = postal[:3]  
                                            if prefix3 in kode_pos_prov:
                                                return kode_pos_prov[prefix3]
                                            prefix2 = postal[:2]
                                            if prefix2 in kode_pos_prov:
                                                return kode_pos_prov[prefix2]
                                        
                                            return "Unknown"
                                        df_prov['Provinsi'] = df_prov[prov].apply(map_postal_code)
                                        st.dataframe(df_prov[[prov, "Provinsi"]])
                                        st.session_state.df = df_prov
                                        st.success("Province mapped successfully")
                                        st.session_state.change_history.append(
                                            "• Field `Province` created"
                                        ) 
                            # indent 7
                            if selected_column == "Chassis Number":
                                st.markdown("""
                                `Chassis Number` needs `Chassis Number` column and will do the validation.
                                """)
                                chas = st.selectbox("Choose field that represents chassis number", options=[""] + list(df.columns))
                                if chas:
                                    if st.button("Chassis validation"):
                                        df_chassis = df.copy()
                                        def validate_chassis(chassis):
                                            if pd.isna(chassis):
                                                return "Invalid: empty"
                                            chassis = str(chassis)
                                            if re.search(r'(\d)\1{5,}', chassis):
                                                return 'Invalid: repeated digits'
                                            if not len(chassis) == 17:
                                                return f"Invalid: Length {len(chassis)}"

                                            return chassis
                                        df_chassis[f"{chas}_val"] = df_chassis[chas].apply(lambda x: validate_chassis(x))
                                        st.session_state.df = df_chassis
                                        st.success("Chassis number validation complete")
                                        st.dataframe(df_chassis[[chas,f"{chas}_val"]])
                                        st.session_state.change_history.append(
                                            "• Field `Chassis Validation` created"
                                        )
                            # DONEEEE
                            if selected_column == "Gross Premi/Year":
                                st.markdown("""
                                `Gross Premi/Year` needs `Tahun Periode Polis` and `Gross Premi` column and will calculate Gross Premi based on policy period year.
                                """)
                                periode_polis = st.selectbox("Choose field that represents `tahun periode polis`", options=[""]+list(df.columns))
                                gross_prem = st.selectbox("Choose field that represents `gross premi`", options=[""]+list(df.columns))
                                if gross_prem:
                                    if st.button("Calculate gross premi/year"):
                                        df_prem = df.copy()
                                        def validate_prem(premi):
                                            if pd.isna(premi):
                                                return "Invalid: empty gross premi"
                                            premi = int(premi)
                                            return premi
                                        def validate_period(period):
                                            if pd.isna(period):
                                                return "Invalid: empty policy period in year"
                                            period = int(period)
                                            return period
                                    
                                        premi = df_prem[gross_prem].apply(lambda x: validate_prem(x))
                                        period = df_prem[periode_polis].apply(lambda x: validate_period(x))
                                
                                        df_prem["Gross Premi/Year"] = premi/period
                                        st.session_state.df = df_prem
                                        st.success("Gross premi/year successfully calculated")
                                        st.dataframe(df_prem[[periode_polis,gross_prem,"Gross Premi/Year"]].head(20))
                                        st.session_state.change_history.append(
                                            "• Field `Gross Premi/Year` created"
                                        )
                            # DONE
                            if selected_column == 'Grouping Gross Premi/Year':
                                st.markdown("""
                                `Grouping Gross Premi/Year` needs `Gross Premi/Year` column and will group it based on this segmentation:
                                - < 1jt
                                - 1-5jt
                                - 5-10jt
                                - 10-15jt
                                - 15-20jt
                                - 20-25jt
                                - 25-30jt
                                - '> 30jt
                                """)
                                group_premi = st.selectbox("Choose field that represents `Gross Premi/Year`", options=[""]+list(df.columns))
                                if group_premi:
                                    if st.button("Group gross premi/year"):
                                        df_group_prem = df.copy()
                                        def grouping_premi(premi):
                                            premi = pd.to_numeric(premi, errors="coerce")
                                            if pd.isna(premi):
                                                return "Invalid: empty gross premi/year"
                                            elif premi < 1000000:
                                                return '< 1jt'
                                            elif 1000000 <= premi < 5000000:
                                                return '1-5jt'
                                            elif 5000000 <= premi < 10000000:
                                                return '5-10jt'
                                            elif 10000000 <= premi < 15000000:
                                                return '10-15jt'
                                            elif 15000000 <= premi < 20000000:
                                                return '15-20jt'
                                            elif 20000000 <= premi < 25000000:
                                                return '20-25jt'
                                            elif 25000000 <= premi < 30000000:
                                                return '25-30jt'
                                            return '> 30jt'
                                        df_group_prem['Grouping Gross Premi/Year'] = df_group_prem[group_premi].apply(grouping_premi)
                                
                                        st.session_state.df = df_group_prem
                                        st.success("Grouping gross premi/year successfully created")
                                        st.dataframe(df_group_prem[[group_premi,"Grouping Gross Premi/Year"]])
                                        st.session_state.change_history.append(
                                            "• Field `Grouping Gross Premi/Year` created"
                                        )
                    
                            if selected_column == 'Grouping Sum Insured':
                                st.markdown("""
                                `Grouping Sum Insured` needs `Sum Insured` column and will group it based on this segmentation:
                                - < 100jt
                                - 100-125jt
                                - 125-200jt
                                - 200-400jt
                                - 400-800jt
                                - 800jt-1.5m
                                - '> 1.5m
                                """)
                                group_tsi = st.selectbox("Choose field that represents `Sum Insured`", options=[""]+list(df.columns))
                                if group_tsi:
                                    if st.button("Group sum insured"):
                                        df_group_tsi = df.copy()
                                        def grouping_tsi(tsi):
                                            tsi = pd.to_numeric(tsi, errors="coerce")
                                            if pd.isna(tsi):
                                                return "Invalid: empty sum insured"
                                            elif tsi < 100000000:
                                                return '< 100jt'
                                            elif 100000000 <= tsi < 125000000:
                                                return '100-125jt'
                                            elif 125000000 <= tsi < 200000000:
                                                return '125-200jt'
                                            elif 200000000 <= tsi < 400000000:
                                                return '200-400jt'
                                            elif 400000000 <= tsi < 800000000:
                                                return '400-800jt'
                                            elif 800000000 <= tsi < 1500000000:
                                                return '800jt-1.5m'
                                            return '> 1.5m'
                                        df_group_tsi['Grouping Sum Insured'] = df_group_tsi[group_tsi].apply(grouping_tsi)
                                
                                        st.session_state.df = df_group_tsi
                                        st.success("Grouping sum insured successfully created")
                                        st.dataframe(df_group_tsi[[group_tsi,"Grouping Sum Insured"]])
                                        st.session_state.change_history.append(
                                            "• Field `Grouping Sum Insured` created"
                                        )
                                                    
                    # indent: 5     
                    st.markdown("**History Changes:**")
                    if st.session_state.change_history:
                        for entry in st.session_state.change_history:
                            st.markdown(entry)
                    else:
                        st.markdown("*None*")
            
                    if st.button("🔄 Reset data transformation"):
                        st.session_state.df = st.session_state.original_df.copy()
                        #st.session_state.custom_dtypes = {col: str(st.session_state.df[col].dtype) for col in st.session_state.df.columns}
                        st.session_state.change_history = []
                        st.success("Changes has been reset.")

                    # 5. PREVIEW DATA
                    # indent: 5
                    st.markdown("")
                    if st.button('Preview Data ⏭️', key='preview'):
                        st.session_state['previewclean2_clicked'] = True

                    if st.session_state['previewclean2_clicked']:
                        st.markdown("---")
                        st.subheader('📊 5. Preview Data')
                        st.write("**Data shape:**", df.shape)
                        st.write("**First 5 Rows:**")
                        st.dataframe(df.head())
                        st.write("**Last 5 Rows:**")
                        st.dataframe(df.tail())
                        st.write("**All Data Row:**")
                        st.dataframe(df)
            
                        info_df = pd.DataFrame({"Column": df.columns,
                        "Non-Null Count": df.notnull().sum().values,
                        "Null Count":df.isna().sum().values,
                        "Dtype": df.dtypes.values})
                        st.write("**Column Names and Data Types:**")
                        st.dataframe(info_df)

                        # 6. REMOVE DUPLICATE
                        # indent: 6
                        st.markdown("")
                        if st.button('Remove Duplicate ⏭️', key='dupli'):
                            st.session_state['removedupli_clicked'] = True

                        if st.session_state['removedupli_clicked']:
                            st.markdown("---")
                            st.subheader('📑 6. Remove Duplicate')
                            st.write("Data shape: ", {len(df)})
                            input_dupli = st.number_input("How many base column to remove duplicate?", min_value=0, max_value =len(df.columns), step=1, format='%d', key='num_dupli')
                            st.write("min: 1, max:", len(df.columns))

                            if input_dupli == 0:
                                st.info("No duplicate will be removed.")
                            else:
                                if st.button("Ok", key='ok'):
                                    st.session_state['dupli_config'] = True

                                if st.session_state.get('dupli_config', False):
                                    selected_cols = []
                                    for i in range(st.session_state['num_dupli']):
                                        col = st.selectbox(f"Choose column {i+1}", options=[""] + list(df.columns), key=f"dupli_col_{i}")
                                        st.dataframe(df[col].value_counts())
                                        st.write("Total of unique value: ",df[col].nunique())
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
                                                try:
                                                    number = [int(x.strip()) for x in index.split(',') if x.strip().isdigit()]
                                                    st.write(f"Index number entered: {number}")
                                                except Exception as e:
                                                    st.error(f"Invalid input: {e}")
                    
                                    if st.button("Remove", key='remove dupli'):
                                        df_cleaned = None
                                        if keep_option == "Last":
                                            df_cleaned = df.drop_duplicates(subset=selected_cols, keep='first').reset_index(drop=True)
                                        elif keep_option == "First":
                                            df_cleaned = df.drop_duplicates(subset=selected_cols, keep='last').reset_index(drop=True)
                                        elif keep_option == "All":
                                            dup_mask = df.duplicated(subset=selected_cols, keep=False)
                                            df_cleaned = df[~dup_mask].reset_index(drop=True)
                                        elif choose_index == True:
                                            df_cleaned = df.drop(number).reset_index(drop=True)
                                            choose_index = False
                        
                                        st.success(f"Successfully remove duplicate based on {', '.join(selected_cols)} using '{keep_option}'")
                                        st.write("New data:")
                                        st.dataframe(df_cleaned)
                                        st.write("New data shape: ",len(df_cleaned))
                                        st.session_state.df = df_cleaned

                            # INDENT: 7
                            # DROP COLUMNS
                            st.markdown("")
                            if st.button('Drop Column ⏭️', key='drop_col'):
                                st.session_state['dropcol_clicked'] = True
                            if st.session_state['dropcol_clicked']:
                                st.markdown("----")
                                st.subheader("🗑️ 8. Drop Column")
                                if "change_history2" not in st.session_state:
                                    st.session_state.change_history2 = []
                                    
                                df = st.session_state.df
                                drop_col = []
                                drop_col = st.multiselect("Choose column(s) to drop", options=[""]+list(df.columns))
                                if st.button("Drop"):
                                    df_drop = None
                                    df_drop = df.drop(drop_col, axis=1)
                                    st.success(f"Successfully drop {drop_col} column")
                                    st.write("Available columns: ", df_drop.columns)
                                    st.session_state.df = df_drop
                                    st.session_state.change_history2.append(drop_col)
                                    
                                if st.session_state.change_history2:
                                    for entry in st.session_state.change_history2:
                                        st.info(f"Dropped Columns: {entry}")
                                else:
                                    st.markdown("*None*")
                            
                                # 8. SAVE DATA
                                # indent: 8
                                if st.button('Save Transformed Data ⏭️', key='save_trans_data'):
                                    st.session_state['savedata_clicked'] = True
                    
                                if st.session_state['savedata_clicked']:
                                    st.markdown("----")
                                    st.subheader('📥 8. Save Transformed Data')
                                    try:
                                        output = BytesIO()
                                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                            df.to_excel(writer, index=False, sheet_name='Sheet1')
                                            writer.close()
                                            processed_data = output.getvalue()
                
                                        if st.download_button(label="Download as Excel", data=processed_data,
                                                   file_name=f"transformed_{uploaded_file.name}.xlsx",
                                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
                                            st.success("Dataset successfully saved.")
                                    except Exception as e:
                                        st.error(f"❌ Error saving file: {e}")
                               
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

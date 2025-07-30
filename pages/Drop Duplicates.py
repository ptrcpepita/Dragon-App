st.subheader("📂 1. Insert an Excel File Link")

url = st.text_input("Paste the one drive public Excel file URL here (format = one drive link + '&download=1'):")

#if url:
   # try:
       # response = requests.get(url)
       # response.raise_for_status()  # Raise error for bad status
       # df = pd.read_excel(BytesIO(response.content))  # For .xlsx files
       # st.success("File loaded successfully!")
       # st.dataframe(df.head())  
  #  except Exception as e:
      #  st.error(f"Failed to load the Excel file: {e}")

#uploaded_file = st.file_uploader('Upload here', type=["xlsx", "csv"])

#current_file_name = uploaded_file.name if uploaded_file else None
#if ("uploaded_file_name" in st.session_state # cek apakah filenya berubah/ilang
   # and st.session_state.uploaded_file_name != current_file_name):
    #for key in ["original_df", "df", "custom_dtypes", "change_history", "change_history2"]:
       # st.session_state.pop(key, None)
   # st.session_state.uploaded_file_name = current_file_name
    
# elif uploaded_file and "uploaded_file_name" not in st.session_state:
   # st.session_state.uploaded_file_name = current_file_name

current_file_name = os.path.basename(url) if url else None
if ("url_name" in st.session_state # cek apakah filenya berubah/ilang
    and st.session_state.url_name != current_file_name):
    for key in ["original_df", "df", "custom_dtypes", "change_history", "change_history2"]:
        st.session_state.pop(key, None)
    st.session_state.url_name = current_file_name
    
elif url and "url_name" not in st.session_state:
    st.session_state.uploaded_file_name = current_file_name
        
#if uploaded_file:
    #try:
        #if "original_df" not in st.session_state:
if url:
    try:
        if "original_df" not in st.session_state:
            response = requests.get(url)
            response.raise_for_status()  # Raise error for bad status
            df = pd.read_excel(BytesIO(response.content), dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})  # For .xlsx files
            #st.success("File loaded successfully!")
            #st.dataframe(df.head())  

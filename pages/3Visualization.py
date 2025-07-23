import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

st.markdown("## 📊 Data Visualization")
st.image("https://raw.githubusercontent.com/ptrcpepita/Dragon-App/86e4aa03a4ed44ae49f7f60eb07301c143749ce4/asset/userflow_visualization.png", width=700)

# Upload & Plot Button
st.markdown("---")
st.subheader("📂 Upload an Excel File")
uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'}) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file, dtype={'Policy No': 'str', 'Phone No': 'str', 'ID Number': 'str', 'HP':'str', 'NIK':'str', 'Tahun':'str', 'Policy Holder Code':'str', 'Post Code': 'str', 'Postal Code': 'str', 'Kode Pos': 'str', 'Home Post Code': 'str', 'Office Post Code': 'str'})
    st.session_state.original_df = df
    if st.button("Visualize data ⏭️"):
        st.session_state.plot_clicked = True
        st.session_state.df = df.copy()
    if st.button("Comparison chart ⏭️"): 
        st.session_state.plot_clicked = False
        st.session_state.df = df.copy()
else:
    st.info("Please upload an Excel file to get started.")

# Setelah klik Plot Data
if st.session_state.get("plot_clicked"):
    st.markdown("---")
    st.subheader("📊 Visualize Data")

    # Sidebar
    with st.sidebar:
        st.markdown("### Dashboard Filter")
        
        if "filter_count" not in st.session_state:
            st.session_state.filter_count = 1
            st.session_state.filters = []

        def add_filter():
            st.session_state.filter_count += 1

        def remove_filter():
            if st.session_state.filter_count >= 1:
                st.session_state.filter_count -=1
                
        filters = []
        
        for i in range(st.session_state.filter_count):
            select_col = st.selectbox(f"ℹ️ Filter {i+1}", [""] + list(st.session_state.original_df.columns), key=f"filt_{i}")
            if select_col:
                col_dtype = st.session_state.original_df[select_col].dtype
                if pd.api.types.is_numeric_dtype(col_dtype):
                    min_val = st.number_input("Min", value=int(st.session_state.original_df[select_col].min()),  min_value=int(st.session_state.original_df[select_col].min()), key=f"min_{i}")
                    max_val = st.number_input("Max", value=int(st.session_state.original_df[select_col].max()), max_value=int(st.session_state.original_df[select_col].max()), key=f"max_{i}")
                    #filters.append((select_col, lambda x, min_v=min_val, max_v=max_val: (x >= min_val) & (x <= max_val)))
                    #filters.extend([(select_col, lambda x: (x >= min_val) & (x <= max_val))])
                    filters.append({"col": select_col, "type": "numeric", "min": min_val, "max": max_val})
                    
                elif pd.api.types.is_datetime64_any_dtype(col_dtype):
                    min_date = df[select_col].min()
                    max_date = df[select_col].max()
                    date = st.date_input("From-To", value=(min_date, max_date))
                    #filters.append((select_col, lambda x, dates=date: x.isin(date)))
                    #filters.extend([(select_col, lambda x: x.isin(date))])
                    filters.append({"col": select_col, "type":"date", "start":date[0], "end":date[1]})
                    
                else:
                    unique_vals = st.session_state.original_df[select_col].dropna().unique().tolist()
                    selected_vals = st.multiselect("Choose values", unique_vals, key=f"sel_{i}")
                    #filters.append((select_col, lambda x, sel_vals=selected_vals: x.isin(selected_vals)))
                    #filters.extend([(select_col, lambda x: x.isin(selected_vals))])
                    filters.append({"col": select_col, "type":"categorical", "values":selected_vals})
        
        st.button("➕ Add filter", key="add_filt_btn", on_click=add_filter)
        st.button("➖ Remove filter", key ='remove_filt_btn', on_click = remove_filter)

    # Filtering logic
    df_plot = st.session_state.original_df.copy()

    for f in filters:
        col = f["col"]
        if f["type"] == "categorical":
            df_plot = df_plot[df_plot[col].isin(f["values"])]
        elif f["type"] == "numeric":
            df_plot = df_plot[(df_plot[col] >= f["min"]) & (df_plot[col] <= f["max"])]
        elif f["type"] == "date":
            df_plot = df_plot[(df_plot[col] >= f["start"]) & (df_plot[col] <= f["end"])]
            
    #for col, condition in filters:
        #df_plot = df_plot[condition(df_plot[col])]

    # Show Plot
    cols = st.columns(3)
    custom_color = ['#0068c9','#83c9ff','#ff2b2b','#ffa15a', '#00cc96']
            
    # SELECT COLUMNS TO BE PLOTTED
    selected = st.multiselect(f"Choose column to be plotted", [""] + list(df_plot.columns))
    if selected:
        cols_row = 3
        rows = [selected[i:i+cols_row] for i in range(0, len(selected), cols_row)]
        for row in rows:
            cols = st.columns([1.8, 1.8, 1.8])
            for i, col in enumerate(row):
                with cols[i]:
                    if pd.api.types.is_numeric_dtype(df_plot[col]):
                        fig = px.histogram(df_plot, x=col, histfunc='count',title="", text_auto=True)
                        fig.update_layout(title_text=f"{col}", xaxis_title='', yaxis_title='')
                        fig.update_traces(textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif pd.api.types.is_datetime64_any_dtype(df_plot[col]):
                        df_plot[col] = pd.to_datetime(df_plot[col], errors="coerce")
                        df_plot["Month-Year"] = df_plot[col].dt.strftime("%b %Y")
                        df_date = df_plot["Month-Year"].value_counts().sort_index().reset_index()
                        df_date.columns =["Month-Year", "Count"]
                        
                        fig = px.histogram(df_date, x="Month-Year", y='Count', text_auto=True,title="")
                        fig.update_layout(title_text=f"{col}", xaxis_title='', yaxis_title='')
                        fig.update_traces(textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
        
                    elif pd.api.types.is_string_dtype(df_plot[col]) or pd.api.types.is_object_dtype(df_plot[col]):
                        value_counts = df_plot[col].value_counts()
            
                        if len(value_counts) <= 3: 
                            fig = px.pie(df_plot, names=col, title="")
                            fig.update_layout(title_text=f"{col}", showlegend = False)
                            fig.update_traces(textinfo='percent+label+value')
                            st.plotly_chart(fig, use_container_width=True)
            
                        else:
                            df_bar = df_plot[col].value_counts().reset_index()
                            df_bar.columns = [col, "Count"]
                            fig = px.bar(df_bar, x=col, y="Count", title="", text="Count")
                            fig.update_layout(title_text=f"{col}", xaxis_title='', yaxis_title='')
                            fig.update_traces(textposition='outside')
                            st.plotly_chart(fig, use_container_width=True)
        st.write(len(df_plot), "data out of", len(df))
            
    st.write("")
    st.write("")
    st.write("")
    if st.button("🔄🔄 Reset All"):
        st.session_state.clear()
        st.rerun()
        
# Setelah klik Plot Data (2)
elif st.session_state.get("plot_clicked") == False:
    st.markdown("---")
    st.subheader("📊 Comparison Chart")

    # Sidebar
    with st.sidebar:
        st.markdown("### Dashboard Filter")
        
        if "filter_count" not in st.session_state:
            st.session_state.filter_count = 1
            st.session_state.filters = []

        def add_filter():
            st.session_state.filter_count += 1

        def remove_filter():
            if st.session_state.filter_count >= 1:
                st.session_state.filter_count -=1
                
        filters = []
        
        for i in range(st.session_state.filter_count):
            select_col = st.selectbox(f"ℹ️ Filter {i+1}", [""] + list(st.session_state.original_df.columns), key=f"filt_{i}")
            if select_col:
                col_dtype = st.session_state.original_df[select_col].dtype
                if pd.api.types.is_numeric_dtype(col_dtype):
                    min_val = st.number_input("Min", value=int(st.session_state.original_df[select_col].min()),  min_value=int(st.session_state.original_df[select_col].min()), key=f"min_{i}")
                    max_val = st.number_input("Max", value=int(st.session_state.original_df[select_col].max()), max_value=int(st.session_state.original_df[select_col].max()), key=f"max_{i}")
                    #filters.append((select_col, lambda x, min_v=min_val, max_v=max_val: (x >= min_val) & (x <= max_val)))
                    #filters.extend([(select_col, lambda x: (x >= min_val) & (x <= max_val))])
                    filters.append({"col": select_col, "type": "numeric", "min": min_val, "max": max_val})
                    
                elif pd.api.types.is_datetime64_any_dtype(col_dtype):
                    min_date = df[select_col].min()
                    max_date = df[select_col].max()
                    date = st.date_input("From-To", value=(min_date, max_date))
                    #filters.append((select_col, lambda x, dates=date: x.isin(date)))
                    #filters.extend([(select_col, lambda x: x.isin(date))])
                    filters.append({"col": select_col, "type":"date", "start":date[0], "end":date[1]})
                    
                else:
                    unique_vals = st.session_state.original_df[select_col].dropna().unique().tolist()
                    selected_vals = st.multiselect("Choose values", unique_vals, key=f"sel_{i}")
                    #filters.append((select_col, lambda x, sel_vals=selected_vals: x.isin(selected_vals)))
                    #filters.extend([(select_col, lambda x: x.isin(selected_vals))])
                    filters.append({"col": select_col, "type":"categorical", "values":selected_vals})
        
        st.button("➕ Add filter", key="add_filt_btn", on_click=add_filter)
        st.button("➖ Remove filter", key ='remove_filt_btn', on_click = remove_filter)

    # Filtering logic
    df_plot = st.session_state.original_df.copy()

    for f in filters:
        col = f["col"]
        if f["type"] == "categorical":
            df_plot = df_plot[df_plot[col].isin(f["values"])]
        elif f["type"] == "numeric":
            df_plot = df_plot[(df_plot[col] >= f["min"]) & (df_plot[col] <= f["max"])]
        elif f["type"] == "date":
            df_plot = df_plot[(df_plot[col] >= f["start"]) & (df_plot[col] <= f["end"])]
            
    #for col, condition in filters:
        #df_plot = df_plot[condition(df_plot[col])]

    # Show Plot
    cols = st.columns(3)
    #custom_color = ['#0068c9','#83c9ff','#ff2b2b','#ffa15a', '#00cc96', '#ab63fa', '#ffabab']
    
    base = st.selectbox(f"Choose column as a base for comparison", [""] + list(df_plot.columns))
    if base:
        if df_plot[base].nunique() <= 8:
            
            selected = st.multiselect(f"Choose column to be plotted", [""] + list(df_plot.columns))
            
            #df_color = df_plot[base].value_counts().sort_values(ascending=False).reset_index()
            #df_color.columns = ["Value", "Count"]
            #color = px.colors.qualitative.Plotly
            
            #for i, val in enumerate(df_color["Value"]):
                #col_color = color[i]
                #st.markdown(f"""
                #<div style="display: flex; align-itmes: center; gap: 8px;">
                #<div style = "width: 16px; height: 16px; background-color: {col_color}; border-radius: 3px;">
                #</div><span>{val}</span></div>
                #""", unsafe_allow_html=True)
            rows = []
            if selected:
                cols_row = 3
                rows = [selected[i:i+cols_row] for i in range(0, len(selected), cols_row)]
            for row in rows:
                cols = st.columns([1.8, 1.8, 1.8])
                for i, col in enumerate(row):
                    with cols[i]:
                        if pd.api.types.is_numeric_dtype(df_plot[col]):
                            base_groups = {}
                            fig = go.Figure()
                            for j in df_plot[base].unique():
                                base_groups[j] = df_plot[df_plot[base]==j]
                                fig.add_trace(go.Histogram(name=str(j), x=base_groups[j][col])) #x=[col])) #y= [base_groups[j][col].mean()]))
                            
                            fig.update_layout(barmode="group", title_text=f"{(col)}", xaxis_title='', yaxis_title='', showlegend=True)
                            fig.update_traces(textposition='outside')
                            st.plotly_chart(fig, use_container_width=True)

                           #fig = px.histogram(df_plot, x=col, histfunc='count',title="", text_auto=True)
                        #fig.update_layout(title_text=f"{col}", xaxis_title='', yaxis_title='')
                        #fig.update_traces(textposition='outside')
                        #st.plotly_chart(fig, use_container_width=True)
                        
                        elif pd.api.types.is_string_dtype(df_plot[col]) or pd.api.types.is_object_dtype(df_plot[col]):
                            base_groups = {}
                            dist={}
                            all_categories= set()
                            
                            for j in df_plot[base].unique():
                                base_groups[j] = df_plot[df_plot[base]==j]
                                dist[j] = base_groups[j][col].value_counts()
                                all_categories.update(dist[j].index)
                                
                            all_categories = sorted(all_categories)
                            fig = go.Figure()
                            
                            for j in dist:
                                y = [dist[j].get(cat, 0) for cat in all_categories]
                                fig.add_trace(go.Bar(name=str(j), x=all_categories, y= y))
                                
                            fig.update_layout(barmode="group", title_text=f"{(col)}", xaxis_title='', yaxis_title='', showlegend=True)
                            fig.update_traces(textposition='outside')
                            st.plotly_chart(fig, use_container_widtg=True)
                    
        else:
            st.error("Please choose column with have max 8 unique values")
                    
    st.write("")
    st.write("")
    st.write("")
    if st.button("🔄🔄 Reset All"):
        st.session_state.clear()
        st.rerun()           

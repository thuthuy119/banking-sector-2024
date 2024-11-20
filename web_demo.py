#streamlit run web_demo.py
import requests
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import plotly_express as px
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components
from PIL import Image
import math
from numpy import cos, sin, arcsin, sqrt, pi
from math import radians
from unidecode import unidecode
import streamlit.components.v1 as components
from PIL import Image
import plotly.graph_objects as go 

#--------------------1. PAGE TITLE--------------------------------

st.set_page_config(page_title='Bank_geo_analysis', layout="wide")
row0_0, row0_1, title, _ = st.columns((1, 0.3, 6, 1))
# with row0_0:
#     image1 = Image.open('D:/ry_practice/logo.png')
#     st.image(image1)
with title:
    st.markdown("<h2 style='font-weight: bold;text-align: center; color:firebrick;'>Business sector geo-location analysis demo</h2>", unsafe_allow_html=True)

#--------------------2. IMPORTING AND PROCESSING DATA -------------------- 

#--------------------2.1. Banking data --------------------------------------
link = ('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/bank_demographic_fix.csv')
@st.cache_data()
def get_dataset(allow_output_mutation=True):
    dataframe = pd.read_csv(link)
    dataframe['outlet'].fillna(value=0, inplace=True)
    dataframe['atm'].fillna(value=0, inplace=True)
    dataframe['branch'].fillna(value=0, inplace=True)
    return dataframe


df2 = get_dataset()


@st.cache_data()
def movecol(df, cols_to_move=[], ref_col='', place='After'):
    cols = df.columns.tolist()
    if place == 'After':
        seg1 = cols[:list(cols).index(ref_col) + 1]
        seg2 = cols_to_move
    if place == 'Before':
        seg1 = cols[:list(cols).index(ref_col)]
        seg2 = cols_to_move + [ref_col]

    seg1 = [i for i in seg1 if i not in seg2]
    seg3 = [i for i in cols if i not in seg1 + seg2]

    return(df[seg1 + seg2 + seg3])

##----------------------2.2. Clustering data ---------------------------------------
link2 = ('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/cluster_result_district_fixx.csv')


@st.cache_data()
def get_data():
    data = pd.read_csv(link2)
    data = movecol(data,
                   cols_to_move=['id', 'district'],
                   ref_col='land',
                   place='Before')
    data = data.set_index('district')
    data = data.sort_values('id', ascending=True)
    two = '00' + \
        data.loc['Quan Ba Dinh':'Quan Thanh Xuan', :]['id'].astype(str)
    one = '0' + data.loc['Huyen Soc Son':'Huyen Me Linh', :]['id'].astype(str)
    three = data.loc['Quan Ha Dong':, 'id'].astype(str)
    id_district = pd.concat([two, one, three])
    data['id_district'] = id_district
    return data


df4 = get_data()

##---------------------------2.3. Location data ------------------------


url = 'https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hanoi.json'
response = requests.get(url)
if response.status_code == 200:
    file = response.text  # Nội dung tệp JSON được lưu dưới dạng chuỗi
    hanoi_json = json.loads(response.text)  # Chuyển đổi chuỗi JSON thành đối tượng Python
else:
    st.error(f"Failed to load JSON file from URL. Status code: {response.status_code}")
    hanoi_json = None


@st.cache_data()
def get_json_data():
    # data = json.load(file)
    # geojson = data['level2s']
    # return geojson
    geojson = json.loads(file)
    del geojson['level1_id']
    del geojson['name']
    del geojson['coordinates']
    del geojson['type']
    del geojson['bbox']
    # change key name geojson['level2s'] to geojson['FeatureCollection']
    features = geojson['level2s']
    del geojson['level2s']
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = features
    # restructure geojson['features']: type, coordinates, bbox to geometry dict, level2_id into id,
    # name to properties dict, add type as features
    district = geojson['features']
    for i in range(len(district)):
        # id
        dist_id = district[i]['level2_id']
        del district[i]['level2_id']
        district[i]['id'] = dist_id
        # properties
        district[i]['properties'] = {}
        district[i]['properties']['name'] = district[i]['name']
        del district[i]['name']
        # geometry
        district[i]['geometry'] = {}
        district[i]['geometry']['type'] = district[i]['type']
        district[i]['geometry']['coordinates'] = district[i]['coordinates']
        district[i]['geometry']['bbox'] = district[i]['bbox']
        del district[i]['type']
        del district[i]['coordinates']
        del district[i]['bbox']
        # type
        district[i]['type'] = 'feature'
    return geojson


geojson = get_json_data()

mapbox_access_token = 'pk.eyJ1IjoiaGFtaWJvIiwiYSI6ImNrN2N2Ym5uYTAybzEzb256cmk2NGtjeTUifQ.3qaqDjFrZdS3sqeoPeJG-w'

#----------------------------- 3. BUILDING APPLICATON---------------------------

## ----------------------------Navigation panel (1. Overview, 2. Sector, 3. Methodology) --------------------------------


# st.write('<style>div.row-widget.stRadio> div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.sidebar.title('Navigation')
st.sidebar.write('There are 3 pages in the app. Overview page shows the summary of demographical characteristics of Hanoi municipality.  \n Sector page (Banking) analyzes geographic information while the technique of conducting the process is explained in Methodology page.')
button = st.sidebar.radio('Select a page:', options=[
                          'Overview', 'Sector', 'Methodology'])


##-----------------------------------------3.1. OVERVIEW-------------------------------------
if button == 'Overview':
    st.markdown("<h3 style = 'font-weight: bold;color:#AD2A1A;'> Geographic summary </h3>",
                unsafe_allow_html=True)
    st.markdown("<h4 style = 'color: firebrick;'> Location characteristics </h4>",
                unsafe_allow_html=True)
    st.markdown("<h6 style = 'font-style: italic;color: firebrick;'> This section displays a specific location in Vietnam with its general summary. Choosing province and district listed in the selectbox to see the information. </h6>", unsafe_allow_html=True)
    # with first:
    #     st.markdown("<h4 style = 'color: darkorange;'> This section displays a specific location in Vietnam with its general summary.  <br>Choosing province and district listed in the selectbox to see the information</h4>", unsafe_allow_html=True)
    st.write('')
    bt1, bt2, _, bt3 = st.columns((0.5, 0.5, 0.1, 2))
    with bt1:
        province_select = st.selectbox(
            'Select province', options=df2['province_name_vi'].unique())
    with bt2:
        df_province = df2[df2['province_name_vi'] == province_select]
        district_select = st.selectbox(
            'Select district', options=df_province['district'].unique())

    table, _, demo_map = st.columns((2, 0.1, 2))
    with table:
        df_district = df_province[df_province['district'] == district_select]
        df_bftp = df4[df4['id'] ==
                      df_district['district_code'].iloc[0]].iloc[:, 3:10]
        df_bftp.columns = df_bftp.columns.str.title()
        df_transpose = df_bftp.T
        st.markdown("<h5 style = 'font-style: italic;color:#CD594A;'>District factor characteristics and its location are displayed in the section below. Some geographical information can be found in the Quick facts expander. </h5>", unsafe_allow_html=True)
        st.write('')
        components.html(df_transpose.to_html(), height=220, scrolling=True)

        st.markdown(
            "<h4 style = 'color: firebrick;'>Comparing districts sharing the same cluster traits</h4>", unsafe_allow_html=True)
        st.write('')
        cp = st.checkbox('Comparing areas', value=False, key='Comparing')
        if cp:
            st.markdown("<h5 style = 'font-style: italic;color: #CD594A;'>The map on the right is displaying districts from the same cluster in each factor group</h5>", unsafe_allow_html=True)
            group = st.selectbox(
                '', options=df4.iloc[:, 3:10].columns.str.title(), index=2)
            charac = st.selectbox('', options=df4[group.lower()].unique())
            with demo_map:
                px.set_mapbox_access_token(mapbox_access_token)

                dfff = df4[df4.index.isin(
                    df4[df4[group.lower()] == charac].index.unique())]
                fig_2 = px.choropleth_mapbox(dfff, geojson=geojson, locations='id_district', hover_name=dfff.index,
                                             center={'lat': dfff['lat'].values[1], 'lon': dfff['lon'].values[1]}, color='id_district',
                                             color_discrete_sequence=px.colors.qualitative.G10,
                                             zoom=10, opacity=0.5
                                             )
                fig_2.update_layout(showlegend=False,
                                    # legend=dict(
                                    #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
                                    mapbox_style='light', width=525, height=560, margin={"r": 0, "t": 0, "l": 0, "b": 0})
                fig_2.update_traces(marker_line=dict(
                    width=1.5, color='LightSlateGrey'))
                st.plotly_chart(fig_2)

        else:

            with demo_map:
                px.set_mapbox_access_token(mapbox_access_token)

                dff = df4[df4.index == district_select]
                fig_1 = px.choropleth_mapbox(dff, geojson=geojson, locations='id_district', hover_name=dff.index,
                                             center={
                                                 'lat': dff['lat'].values[0], 'lon': dff['lon'].values[0]},
                                             color_discrete_sequence=['Gold'],
                                             zoom=11, opacity=0.5
                                             )
                fig_1.update_layout(showlegend=False,
                                    # legend=dict(
                                    #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
                                    mapbox_style='light', width=525, height=300, margin={"r": 0, "t": 0, "l": 0, "b": 0})
                fig_1.update_traces(marker_line=dict(
                    width=1.5, color='LightSlateGrey'))
                st.plotly_chart(fig_1)

                df_info = df_district.groupby(
                    'district')[['area', 'population', 'pop_density']].agg('sum').reset_index()

                # st.markdown("<h4 style='text-align: left; color: darkgreen;'>Quick facts</h4>", unsafe_allow_html=True)
                fact = st.expander(label='Quick facts', expanded=False)
                with fact:
                    st.table(df_info.set_index('district')
                             .style
                             .format({'area': '{:.2f}', 'population': '{:.0f}', 'pop_density': '{:.2f}'})
                             # .background_gradient(cmap = 'Dark2')
                             .set_properties(**{'background-color': 'lightsalmon', 'color': 'white'})
                             )
    st.write('')
    st.markdown("<h4 style='text-align: left; color:firebrick;'>Graphs and charts</h4>",
                unsafe_allow_html=True)
    st.markdown("<h6 style = 'font-style: italic;color:#CD594A;'>This section below contains 2 types of chart. While the pie charts demonstrate proportions of factor attributes in each district, the bar charts compare the specific values of those attributes on a commune level.</h6>", unsafe_allow_html=True)
    st.write('')

    @st.cache_data()
    def get_df_age():
        df_age_total = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                    'total_female', 'f0_14', 'f15_55', 'f55+']]
        df_age_total = df_age_total.copy()
        df_age_total['0_14'] = df_age_total['m0_14']+df_age_total['f0_14']
        df_age_total['15_60'] = df_age_total['m15_60']+df_age_total['f15_55']
        df_age_total['60+'] = df_age_total['m60+']+df_age_total['f55+']
        return df_age_total
    df_age_1 = get_df_age()

    if cp:
        part1, _, part2 = st.columns((2, 0.1, 2))
        with part1:
            # st.markdown("<h6 style = 'font-style: italic;color: #CO2F1D;'>Having more detailed comparison by multiselecting district below:</h6>", unsafe_allow_html=True)
            dst_compare = st.multiselect(
                '', options=df4[df4[group.lower()] == charac].index.unique().values)
        plot1, _, plot2 = st.columns((1, 0.1, 2))
        if group == 'Age':
            with plot1:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_age():
                        df_district = df_province[df_province['district'] == dist]
                        df_age_cp = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                                 'total_female', 'f0_14', 'f15_55', 'f55+']]
                        df_age_cp = df_age_cp.copy()
                        df_age_cp['0_14'] = df_age_cp['m0_14'] + \
                            df_age_cp['f0_14']
                        df_age_cp['15_60'] = df_age_cp['m15_60'] + \
                            df_age_cp['f15_55']
                        df_age_cp['60+'] = df_age_cp['m60+']+df_age_cp['f55+']
                        return df_age_cp
                    df_age_1 = get_cp_age()

                    df_age = df_age_1.groupby('district')[
                        ['0_14', '15_60', '60+']].agg('sum').reset_index()
                    df_agegroup = pd.melt(df_age[['district', '0_14', '15_60', '60+']], id_vars=[
                                          'district'], var_name='Age group', value_name='value')
                    age2 = px.pie(df_agegroup, title="<b>Age group in {}</b>".format(dist), values='value', color='Age group',
                                  hole=0.3, color_discrete_map={'0_14': '#17BECF', '15_60': '#66AA00', '60+': '#1F77B4'})
                    age2.update_layout(showlegend=True)
                    st.plotly_chart(age2, use_container_width=True)
            with plot2:

                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_age():
                        df_district = df_province[df_province['district'] == dist]
                        df_age_cp = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                                 'total_female', 'f0_14', 'f15_55', 'f55+']]
                        df_age_cp = df_age_cp.copy()
                        df_age_cp['0_14'] = df_age_cp['m0_14'] + \
                            df_age_cp['f0_14']
                        df_age_cp['15_60'] = df_age_cp['m15_60'] + \
                            df_age_cp['f15_55']
                        df_age_cp['60+'] = df_age_cp['m60+']+df_age_cp['f55+']
                        return df_age_cp
                    df_age_1 = get_cp_age()
                    df_age2 = df_age_1[['commune', '0_14', '15_60', '60+']]
                    df_age2melt = pd.melt(
                        df_age2, id_vars=['commune'], var_name='Age group', value_name='value')
                    age2bar = px.bar(df_age2melt, title=' ', x='commune', y='value',
                                     color='Age group', color_discrete_sequence=['#17BECF', "#66AA00", '#1F77B4'])
                    age2bar.update_layout(
                        barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                    st.plotly_chart(age2bar, use_container_width=True)
        if group == 'Pop':
            with plot1:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_age():
                        df_district = df_province[df_province['district'] == dist]
                        df_age_cp = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                                 'total_female', 'f0_14', 'f15_55', 'f55+']]
                        df_age_cp = df_age_cp.copy()
                        df_age_cp['0_14'] = df_age_cp['m0_14'] + \
                            df_age_cp['f0_14']
                        df_age_cp['15_60'] = df_age_cp['m15_60'] + \
                            df_age_cp['f15_55']
                        df_age_cp['60+'] = df_age_cp['m60+']+df_age_cp['f55+']
                        return df_age_cp
                    df_age_1 = get_cp_age()
                    df_age = df_age_1.groupby('district')[
                        ['total_male', 'total_female']].agg('sum').reset_index()
                    df_sex = pd.melt(df_age[['district', 'total_male', 'total_female']], id_vars=[
                                     'district'], var_name='Gender', value_name='value')
                    age1 = px.pie(df_sex, title="<b>Gender ratio in {}</b>".format(dist), values='value', color='Gender',
                                  hole=0.3, color_discrete_map={'total_male': '#325A9B', 'total_female': '#DA60CA'})
                    st.plotly_chart(age1, use_container_width=True)
            with plot2:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_age():
                        df_district = df_province[df_province['district'] == dist]
                        df_age_cp = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                                 'total_female', 'f0_14', 'f15_55', 'f55+']]
                        df_age_cp = df_age_cp.copy()
                        df_age_cp['0_14'] = df_age_cp['m0_14'] + \
                            df_age_cp['f0_14']
                        df_age_cp['15_60'] = df_age_cp['m15_60'] + \
                            df_age_cp['f15_55']
                        df_age_cp['60+'] = df_age_cp['m60+']+df_age_cp['f55+']
                        return df_age_cp
                    df_age_1 = get_cp_age()
                    df_age3 = df_age_1[['commune',
                                        'total_male', 'total_female']]
                    df_age3melt = pd.melt(
                        df_age3, id_vars=['commune'], var_name='Gender', value_name='value')
                    age3bar = px.bar(df_age3melt, title=' ', x='commune', y='value',
                                     color='Gender', color_discrete_sequence=['#325A9B', "#DA60CA"])
                    age3bar.update_layout(
                        barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                    st.plotly_chart(age3bar, use_container_width=True)
        if group == 'School':
            with plot1:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_school():
                        df_district = df_province[df_province['district'] == dist]
                        df_edu = df_district[[
                            'district', 'commune', 'edu_primary', 'edu_secondary', 'edu_high_school', 'edu_higher']]
                        return df_edu
                    df_edu = get_cp_school()
                    df_edu1 = df_edu.groupby('district')[
                        ['edu_primary', 'edu_secondary', 'edu_high_school', 'edu_higher']].agg('sum').reset_index()
                    df_edu1melt = pd.melt(
                        df_edu1, id_vars=['district'], var_name='Education level', value_name='value')
                    edu1 = px.pie(df_edu1melt, title="<b>Educational stage in {}</b>".format(dist), values='value', color='Education level', hole=0.3,
                                  color_discrete_map={'edu_primary': '#00CC96', 'edu_secondary': '#FECB52', 'edu_high_school': '#FC6955', 'edu_higher': 'rgb(29, 105, 150)'})
                    st.plotly_chart(edu1, use_container_width=True)
            with plot2:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_school():
                        df_district = df_province[df_province['district'] == dist]
                        df_edu = df_district[[
                            'district', 'commune', 'edu_primary', 'edu_secondary', 'edu_high_school', 'edu_higher']]
                        return df_edu
                    df_edu = get_cp_school()
                    df_edu2 = df_edu[[
                        'commune', 'edu_primary', 'edu_secondary', 'edu_high_school', 'edu_higher']]
                    df_edu2melt = pd.melt(
                        df_edu2, id_vars=['commune'], var_name='Education level', value_name='value')
                    edu2bar = px.bar(df_edu2melt, title=' ', x='commune', y='value', color='Education level', color_discrete_sequence=[
                                     '#00CC96', '#FECB52', '#FC6955', 'rgb(29, 105, 150)'])
                    edu2bar.update_layout(
                        barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                    st.plotly_chart(edu2bar, use_container_width=True)
        if group == 'Marriage':
            with plot1:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_dist():
                        df_district = df_province[df_province['district'] == dist]
                        return df_district
                    df_district = get_cp_dist()
                    df_hhs = df_district.groupby(
                        'district')[['commune', 'hh1_2', 'hh_2+']].agg('sum').reset_index()
                    df_hhs1 = pd.melt(
                        df_hhs, id_vars=['district'], var_name='Number of ppl', value_name='value')
                    hh1 = px.pie(df_hhs1, values='value', title="<b>Size of households in {}</b>".format(district_select),
                                 color='Number of ppl', hole=0.3, color_discrete_map={'hh1_2': '#EF553B',
                                                                                      'hh_2+': '#00A08B'})
                    st.plotly_chart(hh1, use_container_width=True)
            with plot2:
                for dist in dst_compare:
                    @st.cache_data()
                    def get_cp_dist():
                        df_district = df_province[df_province['district'] == dist]
                        return df_district
                    df_district = get_cp_dist()
                    df_hh = df_district[['commune', 'hh1_2', 'hh_2+']]
                    df_hhmelt = pd.melt(
                        df_hh, id_vars=['commune'], var_name='Household size', value_name='value')
                    hh = px.bar(df_hhmelt, title=' ', x='commune', y='value',
                                color='Household size', color_discrete_sequence=['#EF553B', "#00A08B"])
                    hh.update_layout(
                        barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                    st.plotly_chart(hh, use_container_width=True)
        else:
            st.write('')

    else:
        button, plot1, plot2 = st.columns((0.4, 1, 2))
        with button:
            buttonplot = st.radio(
                '', options=['Household', 'Age group', 'Gender', 'Education'])
        if buttonplot == 'Household':
            with plot1:
                df_hhs = df_district.groupby(
                    'district')[['commune', 'hh1_2', 'hh_2+']].agg('sum').reset_index()
                df_hhs1 = pd.melt(
                    df_hhs, id_vars=['district'], var_name='Number of ppl', value_name='value')
                hh1 = px.pie(df_hhs1, values='value', title="<b>Size of households in {}</b>".format(district_select),
                             color='Number of ppl', hole=0.3, color_discrete_map={'hh1_2': '#EF553B',
                                                                                  'hh_2+': '#00A08B'})
                st.plotly_chart(hh1, use_container_width=True)
            with plot2:
                df_hh = df_district[['commune', 'hh1_2', 'hh_2+']]
                df_hhmelt = pd.melt(
                    df_hh, id_vars=['commune'], var_name='Household size', value_name='value')
                hh = px.bar(df_hhmelt, title=' ', x='commune', y='value',
                            color='Household size', color_discrete_sequence=['#EF553B', "#00A08B"])
                hh.update_layout(barmode='stack', xaxis_tickangle=-
                                 30, xaxis_title='', yaxis_title=' ')
                st.plotly_chart(hh, use_container_width=True)

        if buttonplot == 'Age group':
            with plot1:
                df_age = df_age_1.groupby('district')[
                    ['0_14', '15_60', '60+']].agg('sum').reset_index()
                df_agegroup = pd.melt(df_age[['district', '0_14', '15_60', '60+']], id_vars=[
                                      'district'], var_name='Age group', value_name='value')
                age2 = px.pie(df_agegroup, title="<b>Age group in {}</b>".format(district_select), values='value',
                              color='Age group', hole=0.3, color_discrete_map={'0_14': '#17BECF', '15_60': '#66AA00', '60+': '#1F77B4'})
                st.plotly_chart(age2, use_container_width=True)
            with plot2:
                df_age2 = df_age_1[['commune', '0_14', '15_60', '60+']]
                df_age2melt = pd.melt(
                    df_age2, id_vars=['commune'], var_name='Age group', value_name='value')
                age2bar = px.bar(df_age2melt, title=' ', x='commune', y='value',
                                 color='Age group', color_discrete_sequence=['#17BECF', "#66AA00", '#1F77B4'])
                age2bar.update_layout(
                    barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                st.plotly_chart(age2bar, use_container_width=True)
        if buttonplot == 'Gender':
            with plot1:
                df_age = df_age_1.groupby('district')[
                    ['total_male', 'total_female']].agg('sum').reset_index()
                df_sex = pd.melt(df_age[['district', 'total_male', 'total_female']], id_vars=[
                                 'district'], var_name='Gender', value_name='value')
                age1 = px.pie(df_sex, title="<b>Gender ratio in {}</b>".format(district_select), values='value',
                              color='Gender', hole=0.3, color_discrete_map={'total_male': '#325A9B', 'total_female': '#DA60CA'})
                st.plotly_chart(age1, use_container_width=True)
            with plot2:
                df_age3 = df_age_1[['commune', 'total_male', 'total_female']]
                df_age3melt = pd.melt(
                    df_age3, id_vars=['commune'], var_name='Gender', value_name='value')
                age3bar = px.bar(df_age3melt, title=' ', x='commune', y='value',
                                 color='Gender', color_discrete_sequence=['#325A9B', "#DA60CA"])
                age3bar.update_layout(
                    barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                st.plotly_chart(age3bar, use_container_width=True)
        if buttonplot == 'Education':
            df_edu = df_district[['district', 'commune', 'edu_primary',
                                  'edu_secondary', 'edu_high_school', 'edu_higher']]
            with plot1:
                df_edu1 = df_edu.groupby('district')[
                    ['edu_primary', 'edu_secondary', 'edu_high_school', 'edu_higher']].agg('sum').reset_index()
                df_edu1melt = pd.melt(
                    df_edu1, id_vars=['district'], var_name='Education level', value_name='value')
                edu1 = px.pie(df_edu1melt, title="<b>Educational stage in {}</b>".format(district_select), values='value', color='Education level', hole=0.3,
                              color_discrete_map={'edu_primary': '#00CC96', 'edu_secondary': '#FECB52', 'edu_high_school': '#FC6955', 'edu_higher': 'rgb(29, 105, 150)'})
                st.plotly_chart(edu1, use_container_width=True)
            with plot2:
                df_edu2 = df_edu[['commune', 'edu_primary',
                                  'edu_secondary', 'edu_high_school', 'edu_higher']]
                df_edu2melt = pd.melt(
                    df_edu2, id_vars=['commune'], var_name='Education level', value_name='value')
                edu2bar = px.bar(df_edu2melt, title=' ', x='commune', y='value', color='Education level',
                                 color_discrete_sequence=['#00CC96', '#FECB52', '#FC6955', 'rgb(29, 105, 150)'])
                edu2bar.update_layout(
                    barmode='stack', xaxis_tickangle=-30, xaxis_title='', yaxis_title=' ')
                st.plotly_chart(edu2bar, use_container_width=True)

path = ('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/bank_fixx.csv')


@st.cache_resource
def m2_bank_fixx():
    dtframe = pd.read_csv(path)
    bank_level_map = {'Big': 50, 'Medium': 25, 'Small': 10}
    dtframe['bank_label'] = dtframe['bank_level'].map(bank_level_map)
    return dtframe


df1 = m2_bank_fixx()

#-----------------------------------------3.2. SECTOR---------------------------------------
if button == 'Sector':
    st.markdown("<h3 style = 'font-weight: bold;color: #AD2A1A;'>Banking sector geo-location analysis</h2>",
                unsafe_allow_html=True)
    st.markdown("<h4 style = 'color:firebrick';>First glance at business sector distribution.</h4>",
                unsafe_allow_html=True)
    st.markdown("<h6 style = 'font-style: italic;color: #CD594A';>This section shows all the communes with highest/lowest number of bank outlets. Choosing these filters below to execute demands.The choropleth map displays the location and you can find the actual data on the left.</h6>", unsafe_allow_html=True)
    st.write('')
    r1, r2, r3, r4, _ = st.columns((0.3, 0.2, 0.4, 0.15, 0.3))
    file = ('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hn_qn_hcm.csv') 

    @st.cache_data()
    def get_data():
        r = pd.read_csv(file)
        r['atm_dens'] = r['population'].divide(r['atm']).round(decimals=2)
        r['branch_dens'] = r['population'].divide(
            r['branch']).round(decimals=2)
        r.replace([np.inf, -np.inf], np.nan, inplace=True)
        return r
    df_count = get_data()

    with r1:
        value = st.selectbox('Select data type', options=[
                             'Top biggest quantity', 'Top smallest quantity', 'Top biggest capacity', 'Top smallest capacity'])
    with r2:
        outlettype = st.selectbox('Type of outlet', options=['atm', 'branch'])
    with r3:
        prov = st.selectbox('Select province',
                            options=df_count['province'].unique())
        df_prov = df_count[df_count['province'] == prov]

    s1, s2 = st.columns((2, 2))
    with s1:
        # st.markdown("<h5 style = 'font-style: italic;color:#CD594A;'>Communes with .</h5>", unsafe_allow_html= True)
        if prov == 'Thành phố Hồ Chí Minh':
            @st.cache_data()
            def get_data_hcm():
                df = pd.read_csv('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hn_qn_hcm.csv') 
                df1_hcm = df[df['province'] ==
                             'Thành phố Hồ Chí Minh'].reset_index()
                df1_hcm.drop(columns='index', inplace=True)
                df1_hcm['commune_code'] = df1_hcm['commune_code'].astype('str')
                return df1_hcm
            df1_hcm = get_data_hcm()

            @st.cache_data()
            def get_json_hcm():
                with open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hcm.json', encoding='utf-8') as f:
                    data_hcm = json.load(f)
                features_hcm = data_hcm['features']
                for y in range(len(features_hcm)):
                    for x in range(len(df1_hcm.index)):
                        if (df1_hcm.loc[x, 'commune'] == features_hcm[y]["properties"]["Name"]) and (df1_hcm.loc[x, 'district'] == features_hcm[y]["properties"]["Quan"]):
                            features_hcm[y]["id"] = df1_hcm.loc[x,
                                                                'commune_code']
                return data_hcm
            data_hcm = get_json_hcm()
            px.set_mapbox_access_token(mapbox_access_token)

    #         fig_2_hcm = px.choropleth_mapbox(df1_hcm, geojson=data_hcm, locations='commune_code', hover_name = df1_hcm['commune'],
    #                                         color = 'atm', center={'lat': 10.8113261802206, 'lon': 106.69930197020958},
    #                                         color_continuous_scale=px.colors.sequential.Viridis,
    #                                         zoom=8.2, opacity = 0.5
    #                                 )
    #         fig_2_hcm.update_layout(showlegend = False,
    #         # legend=dict(
    #         #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
    #                 mapbox_style='light', width=800, height=420, margin={"r":0,"t":0,"l":0,"b":0})
    #         fig_2_hcm.update_traces(marker_line=dict(width=1, color='white'))
    #         fig_2_hcm.update_layout(coloraxis_showscale=False)
    #         st.plotly_chart(fig_2_hcm, use_container_width = True)
        if prov == 'Tỉnh Quảng Ninh':
            @st.cache_data()
            def get_data_qn():
                df = pd.read_csv('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hn_qn_hcm.csv')
                df2_qn = df[df['province'] == 'Tỉnh Quảng Ninh'].reset_index()
                df2_qn.drop(columns='index', inplace=True)
                df2_qn['commune_code'] = df2_qn['commune_code'].astype('str')
                return df2_qn
            df2_qn = get_data_qn()

            @st.cache_data()
            def get_json_qn():
                with open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/quang_ninh.json', encoding='utf-8') as f:
                    data_qn = json.load(f)
                features_qn = data_qn['features']
                for y in range(len(features_qn)):
                    for x in range(len(df2_qn.index)):
                        if (df2_qn.loc[x, 'commune'] == features_qn[y]["properties"]["Name"]) and (df2_qn.loc[x, 'district'] == features_qn[y]["properties"]["Quan"]):
                            features_qn[y]["id"] = df2_qn.loc[x,
                                                              'commune_code']
                return data_qn
            data_qn = get_json_qn()
            px.set_mapbox_access_token(mapbox_access_token)

    #         fig_2_qn = px.choropleth_mapbox(df2_qn, geojson=data_qn, locations='commune_code', hover_name = df2_qn['commune'],
    #                                         color = 'atm', center={'lat': 21.15501881057594, 'lon': 107.52860999453615},
    #                                         color_continuous_scale=px.colors.sequential.Viridis,
    #                                         zoom=7.1, opacity = 0.5
    #                                 )
    #         fig_2_qn.update_layout(showlegend = False,
    #             # legend=dict(
    #             #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
    #                     mapbox_style='light', width=800, height=420, margin={"r":0,"t":0,"l":0,"b":0})
    #         fig_2_qn.update_traces(marker_line=dict(width=1, color='white'))
    #         fig_2_qn.update_layout(coloraxis_showscale=False)
    #         st.plotly_chart(fig_2_qn, use_container_width = True)
        if prov == 'Thành phố Hà Nội':
            @st.cache_data()
            def get_data_hanoi():
                df = pd.read_csv('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/hn_qn_hcm.csv')
                df3_hn = df[df['province'] == 'Thành phố Hà Nội'].reset_index()
                df3_hn.drop(columns='index', inplace=True)
                df3_hn['commune'] = df3_hn['commune'].apply(unidecode)
                df3_hn['commune_code'] = df3_hn['commune_code'].astype('str')
                return df3_hn
            df3_hn = get_data_hanoi()

            @st.cache_data()
            def get_json_hanoi():
                with open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/ha_noi.json', encoding='utf-8') as f:
                    data_hn = json.load(f)
                features_hn = data_hn['features']
                for y in range(len(features_hn)):
                    for x in range(len(df3_hn.index)):
                        if (df3_hn.loc[x, 'commune'] == features_hn[y]["properties"]["Name"]) and (df3_hn.loc[x, 'district'] == features_hn[y]["properties"]["Quan"]):
                            features_hn[y]["id"] = df3_hn.loc[x,
                                                              'commune_code']
                return data_hn
            data_hn = get_json_hanoi()
            px.set_mapbox_access_token(mapbox_access_token)

    #         fig_2_hn = px.choropleth_mapbox(df3_hn, geojson=data_hn, locations='commune_code', hover_name = df3_hn['commune'],
    #                                         color = 'atm', center={'lat': 21.04501881057594, 'lon': 105.84860999453615},
    #                                         color_continuous_scale=px.colors.sequential.Viridis,
    #                                         zoom=8.2, opacity = 0.5
    #                                 )
    #         fig_2_hn.update_layout(showlegend = False,
    #             # legend=dict(
    #             #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
    #                     mapbox_style='light', width=800, height=420, margin={"r":0,"t":0,"l":0,"b":0})
    #         fig_2_hn.update_traces(marker_line=dict(width=1, color='white'))
    #         fig_2_hn.update_layout(coloraxis_showscale=False)
    #         st.plotly_chart(fig_2_hn, use_container_width = True)

        @st.cache_data()
        def get_viz(dataset, geo, center):
            dist_fig = px.choropleth_mapbox(dataset, geojson=geo, locations='commune_code', hover_name='commune', hover_data=["district"],
                                            color='atm', center=center,
                                            color_continuous_scale=px.colors.sequential.Viridis,
                                            zoom=10, opacity=0.9
                                            )
            dist_fig.update_layout(showlegend=False,
                                   # legend=dict(
                                   #         yanchor='top', xanchor='right', y=1, x=1, orientation='v'),
                                   mapbox_style='light', width=800, height=420, margin={"r": 0, "t": 0, "l": 0, "b": 0})
            dist_fig.update_traces(marker_line=dict(width=1, color='white'))
            dist_fig.update_layout(coloraxis_showscale=False)
            return dist_fig

    with s2:
        if value == 'Top biggest quantity':
            @st.cache_data()
            def top_10_count_max(prov, outlettype):
                return df_prov.sort_values(outlettype, ascending=False).head(10)
            df_count_1 = top_10_count_max(prov, outlettype)

            if prov == 'Thành phố Hồ Chí Minh':
                df1_hcm_big = df1_hcm[df1_hcm['commune_code'].isin(
                    df_count_1['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df1_hcm_big, data_hcm, {
                                    'lat': 10.8113261802206, 'lon': 106.69930197020958}), use_container_width=True)

            if prov == 'Thành phố Hà Nội':
                df3_hanoi_big = df3_hn[df3_hn['commune_code'].isin(
                    df_count_1['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df3_hanoi_big, data_hn, {
                                    'lat': 21.04501881057594, 'lon': 105.84860999453615}))

            if prov == 'Tỉnh Quảng Ninh':
                df2_qn_big = df2_qn[df2_qn['commune_code'].isin(
                    df_count_1['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df2_qn_big, data_qn, {
                                    'lat': 20.98270863106981, 'lon': 107.01471001641096}))

            figc1 = px.bar(df_count_1, x='commune', y=outlettype, hover_data=['district'], color=outlettype, color_continuous_scale=px.colors.sequential.Viridis,
                           labels={outlettype: 'Number of {}'.format(outlettype), 'commune': ''}, height=400)
            figc1.update_layout(xaxis_tickangle=-35, width=600, height=450)
            figc1.update_layout(
                title_text='<b>Communes in {} with the most number of {}</b>'.format(prov, outlettype))
            st.plotly_chart(figc1)

        if value == 'Top smallest quantity':
            @st.cache_data()
            def get_min(outlettype):
                df_min = pd.DataFrame({'{}_0'.format(outlettype): df_prov[df_prov[outlettype] == 0].groupby('district').size(), '{}_1'.format(outlettype): df_prov[df_prov[outlettype] == 1].groupby(
                    'district').size(), '{}>1'.format(outlettype): df_prov[df_prov[outlettype] > 1].groupby('district').size()}).reset_index().sort_values('{}_0'.format(outlettype), ascending=False)
                df_min = df_min.fillna(0)
                return df_min
            df_min = get_min(outlettype)

            @st.cache_data()
            def get_all_min(outlettype):
                df_all_min = df_prov[(df_prov[outlettype] == 0) | (
                    df_prov[outlettype] == 1)]
                return df_all_min
            df_all_min = get_all_min(outlettype)

            if prov == 'Thành phố Hồ Chí Minh':
                df1_hcm_small = df1_hcm[df1_hcm['commune_code'].isin(
                    df_all_min['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df1_hcm_small, data_hcm, {
                                    'lat': 10.8113261802206, 'lon': 106.69930197020958}), use_container_width=True)

            if prov == 'Thành phố Hà Nội':
                df3_hanoi_small = df3_hn[df3_hn['commune_code'].isin(
                    df_all_min['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df3_hanoi_small, data_hn, {
                                    'lat': 21.04501881057594, 'lon': 105.84860999453615}))

            if prov == 'Tỉnh Quảng Ninh':
                df2_qn_small = df2_qn[df2_qn['commune_code'].isin(
                    df_all_min['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df2_qn_small, data_qn, {
                                    'lat': 21.15501881057594, 'lon': 107.52860999453615}))

            figc2 = go.Figure(data=[
                go.Bar(name='{}=0'.format(outlettype), x=df_min['district'], y=df_min['{}_0'.format(
                    outlettype)], marker_color='#FECB52', text=df_min['{}_0'.format(outlettype)].tolist(), textposition='inside', texttemplate='%{text:.0f}'),
                go.Bar(name='{}=1'.format(outlettype), x=df_min['district'], y=df_min['{}_1'.format(
                    outlettype)], marker_color='rgb(27,158,119)'),
                go.Bar(name='{}>1'.format(outlettype), x=df_min['district'], y=df_min['{}>1'.format(
                    outlettype)], marker_color='rgb(128,177,211)'),
            ])

            # figc2 = px.bar(df_min, x=df_min['district'], y=['{}_0'.format(outlettype), '{}_1'.format(outlettype), '{}>1'.format(outlettype)])
            # Change the bar mode
            figc2.update_layout(
                title_text='<b>Number of communes in each district with the smallest number of {}</b>'.format(outlettype))
            figc2.update_layout(barmode='stack', legend=dict(orientation='h',
                                                             x=0.6,
                                                             y=1.05,
                                                             bgcolor='rgba(255, 255, 255, 0)',
                                                             bordercolor='rgba(255, 255, 255, 0)'
                                                             ))
            figc2.update_layout(xaxis_tickangle=-35, font=dict(size=11),
                                width=650, height=450, yaxis_title="Number of communes")
            # figc2.update_xaxes(title_font_family="Roboto")
            st.plotly_chart(figc2)

        if value == 'Top biggest capacity':
            @st.cache_data()
            def top_10_capa_max(prov, outlettype):
                return df_prov.sort_values('{}_dens'.format(outlettype), ascending=False).head(10)
            df_count_4 = top_10_capa_max(prov, outlettype)

            figc3 = px.bar(df_count_4, x='commune', y='{}_dens'.format(outlettype), hover_data=['district'], color='{}_dens'.format(outlettype), color_continuous_scale=px.colors.sequential.Viridis,
                           labels={'{}_dens'.format(outlettype): 'Density of {}'.format(outlettype), 'commune': ''}, width=600, height=450)
            figc3.update_layout(
                title_text='<b>Communes in {} with the highest capacity of {}</b>'.format(prov, outlettype))
            st.plotly_chart(figc3)

            if prov == 'Thành phố Hồ Chí Minh':
                df1_hcm_big_capa = df1_hcm[df1_hcm['commune_code'].isin(
                    df_count_4['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df1_hcm_big_capa, data_hcm, {
                                    'lat': 10.8113261802206, 'lon': 106.69930197020958}), use_container_width=True)

            if prov == 'Thành phố Hà Nội':
                df3_hanoi_big_capa = df3_hn[df3_hn['commune_code'].isin(
                    df_count_4['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df3_hanoi_big_capa, data_hn, {
                                    'lat': 21.04501881057594, 'lon': 105.84860999453615}))

            if prov == 'Tỉnh Quảng Ninh':
                df2_qn_big_capa = df2_qn[df2_qn['commune_code'].isin(
                    df_count_4['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df2_qn_big_capa, data_qn, {
                                    'lat': 21.15501881057594, 'lon': 107.52860999453615}))

        if value == 'Top smallest capacity':
            @st.cache_data()
            def top_10_capa_min(prov, outlettype):
                return df_prov.sort_values('{}_dens'.format(outlettype), ascending=True).head(10)
            df_count_5 = top_10_capa_min(prov, outlettype)

            if prov == 'Thành phố Hồ Chí Minh':
                df1_hcm_small_capa = df1_hcm[df1_hcm['commune_code'].isin(
                    df_count_5['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df1_hcm_small_capa, data_hcm, {
                                    'lat': 10.8113261802206, 'lon': 106.69930197020958}), use_container_width=True)

            if prov == 'Thành phố Hà Nội':
                df3_hanoi_small_capa = df3_hn[df3_hn['commune_code'].isin(
                    df_count_5['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df3_hanoi_small_capa, data_hn, {
                                    'lat': 21.04501881057594, 'lon': 105.84860999453615}))

            if prov == 'Tỉnh Quảng Ninh':
                df2_qn_small_capa = df2_qn[df2_qn['commune_code'].isin(
                    df_count_5['commune_code'].astype(str))]
                with s1:
                    st.plotly_chart(get_viz(df2_qn_small_capa, data_qn, {
                                    'lat': 21.15501881057594, 'lon': 107.52860999453615}))

            figc4 = px.bar(df_count_5, x='commune', y='{}_dens'.format(outlettype), hover_data=['district'], color='{}_dens'.format(outlettype), color_continuous_scale=px.colors.sequential.Viridis,
                           labels={'{}_dens'.format(outlettype): 'Density of {}'.format(outlettype), 'commune': ''}, width=600, height=450)
            figc4.update_layout(
                title_text='<b>Communes in {} with the smallest capacity of {}</b>'.format(prov, outlettype))
            st.plotly_chart(figc4)

    st.markdown("<h4 style = 'color:firebrick;'>Gaining more in-depth understanding about business sector with visualizations.</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style = 'font-style: italic;color: #CD594A';>Each filter on the left is for selecting location on the map while the filter on the right is a hierarchical filter sort through some criteria. There are 2 types of information in this section: by each commune or each bank operating in this area. Display all presents all the values available and Top 5 just sorts 5 most remarkable values. With the above filter, criteria supported includes number of outlets and number of people being served by the outlet. </h6>", unsafe_allow_html=True)
    st.write('')
    bt3, bt4, _, _, _, bt5, bt6, bt7 = st.columns(
        (0.7, 0.7, 0.5, 0.3, 0.1, 2/3, 2/3, 2/3))
    with bt3:
        province_select = st.selectbox(
            'Choosing province', options=df2['province_name_vi'].unique())
    with bt4:
        df_province = df2[df2['province_name_vi'] == province_select]
        district_select = st.selectbox(
            'Choosing district', options=df_province['district'].unique())
    with bt5:
        type1 = st.selectbox('Type of information:', options=[
                             'Display all', 'Top 10'])
    if type1 == 'Display all':
        with bt6:
            type2 = st.selectbox('Type of display', options=[
                                 'Commune', 'Bank'])
        with bt7:
            cri_select = st.selectbox('Criteria to display', options=[
                                      'Outlet', 'Outlet capacity'])
    if type1 == 'Top 10':
        with bt6:
            type2 = st.selectbox('Type of display', options=['Bank'])
        with bt7:
            cri_select = st.selectbox('Criteria to display', options=[
                                      'Outlet', 'Outlet capacity'])

    df_district = df_province[df_province['district'] == district_select]

    @st.cache_data()
    def get_df_age():
        df_age_total = df_district[['district', 'commune', 'total_male', 'm0_14', 'm15_60', 'm60+',
                                    'total_female', 'f0_14', 'f15_55', 'f55+']]
        df_age_total = df_age_total.copy()
        df_age_total['0_14'] = df_age_total['m0_14']+df_age_total['f0_14']
        df_age_total['15_60'] = df_age_total['m15_60']+df_age_total['f15_55']
        df_age_total['60+'] = df_age_total['m60+']+df_age_total['f55+']
        return df_age_total
    df_age_1 = get_df_age()

    df1_1 = df1[df1['district'] == district_select]
    map_image, _, analysis_chart = st.columns((1.9, 0.1, 2))
    with map_image:
        # st.markdown("<h2 style='text-align: left; color: firebrick;'>Banks distribution scatter map</h2>", unsafe_allow_html=True)
        st.markdown("<h5 style = 'font-style: italic;color:#CD594A;'>Bank outlets are scatters placing on top of a choropleth map. Hover over the points to get the type of outlet.</h5>", unsafe_allow_html=True)
        st.write(' ')
        dfff = df4[df4.index == district_select]

        fig = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=dfff['id_district'],
                                            z=dfff['id_district'],
                                            zmin=0, zmax=1,
                                            coloraxis='coloraxis',
                                            marker_opacity=0.3, marker_line_width=1.5))
        fig.add_scattermapbox(lat=df1_1['latitude'],
                              lon=df1_1['longitude'],
                              text="Bank name:" + df1_1.bank.astype(str) + "<br>Type:" + df1_1.type_id.astype(
                                  str) + "<br>Index:"+df1_1.index.astype(str),
                              hoverinfo='text',
                              below='',
                              marker_size=9, opacity=0.8, marker_color='rgb(27,158,119)',
                              )

        fig.update_layout(coloraxis_showscale=False)
        fig.update_layout(mapbox_style='light', width=530,
                          height=400, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_layout(mapbox=dict(
            accesstoken=mapbox_access_token,
            zoom=11,  # change this value correspondingly, for your map
            style="light")  # set your preferred mapbox style
        )
        fig.update_mapboxes(center_lon=dfff['lon'].values[0],
                            center_lat=dfff['lat'].values[0],
                            zoom=12)
        st.plotly_chart(fig)

    with analysis_chart:
        # st.markdown("<h2 style='color: firebrick;'>  District analysis</h2>", unsafe_allow_html=True)
        st.markdown("<h5 style = 'margin-left: 30px;font-style: italic;color:#CD594A;'>   Bar chart represents the information collected from the map. Click on the legend to isolate the trace.</h5>", unsafe_allow_html=True)
        if type1 == 'Display all':
            if type2 == 'Commune':
                if cri_select == 'Outlet capacity':
                    df2_capa_pre = df_district[[
                        'commune', 'population', 'outlet']]
                    df2_capa_pre = df2_capa_pre.copy()
                    df2_capa_pre['outlet_capa'] = df2_capa_pre['population'].divide(
                        df2_capa_pre['outlet'])
                    df2_capa = df2_capa_pre[['commune', 'outlet_capa']].sort_values(
                        'outlet_capa', ascending=True)

                    bar = go.Figure()
                    bar.add_trace(go.Bar(
                        x=df2_capa['commune'],
                        y=df2_capa['outlet_capa'],
                        name='Outlet capacity',
                        marker_color='#00CC96', text=df2_capa['outlet_capa']
                    ))
                    bar.update_layout(yaxis_title='Number of people being served', xaxis_tickangle=-35,
                                      width=630,  height=450, title_text='<b>Outlet capacity of each commune</b>')

                    bar.update_traces(
                        texttemplate='%{text:.2s}', textposition='outside')
                    st.plotly_chart(bar)

                else:
                    df2_outlet = pd.melt(df_district[['commune', 'atm', 'branch']], id_vars=[
                                         'commune'], var_name='type', value_name='count')
                    bar = px.bar(df2_outlet, x="commune", y="count", color='type', color_discrete_sequence=px.colors.qualitative.D3_r, labels={
                                 'commune': '', 'count': 'Number of outlet'})
                    bar.update_layout(xaxis_tickangle=-45, width=650,  height=450,
                                      legend=dict(
                                          x=0.02,
                                          y=1.0,
                                          bgcolor='rgba(255, 255, 255, 0)',
                                          bordercolor='rgba(255, 255, 255, 0)'
                                      ), xaxis_tickfont_size=11,
                                      title_text='<b>Number of outlet in each commune</b>')
                    # bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                    st.plotly_chart(bar)

            if type2 == 'Bank':
                if cri_select == 'Outlet':
                    df3_outlet_df = df1_1.groupby('bank')[['atm', 'branch', 'office']].agg(
                        'sum').reset_index().sort_values('atm', ascending=False)
                    df3_outlet = pd.melt(df3_outlet_df, id_vars=[
                                         'bank'], var_name='type', value_name='count')
                    bar = px.bar(df3_outlet, x="bank", y="count", color='type', color_discrete_sequence=px.colors.qualitative.D3_r, labels={
                                 'bank': '', 'count': 'Number of banks'}, hover_name='bank')
                    bar.update_layout(xaxis_tickangle=-45, width=650,  height=450, title_text='<b>Number of bank outlet</b>',
                                      legend=dict(
                                          x=0.8,
                                          y=1.0,
                                          bgcolor='rgba(255, 255, 255, 0)',
                                          bordercolor='rgba(255, 255, 255, 0)'
                                      ), xaxis_tickfont_size=11)
                    st.plotly_chart(bar)

                elif cri_select == 'Outlet capacity':
                    df1_2 = df1_1[['bank', 'ward', 'ward_pop']].drop_duplicates(keep='first').groupby(
                        'bank')['ward_pop'].agg('sum').reset_index()        # if cri_select == 'Branch capacity':
                    df1_3 = df1_1[['bank', 'bank_level', 'outlet']].groupby(
                        ['bank', 'bank_level'])['outlet'].agg('sum').reset_index()  # df3
                    df1_4 = pd.merge(df1_2, df1_3, on='bank')
                    df1_4['outlet_capacity'] = (df1_4['ward_pop'].divide(
                        df1_4['outlet'])).round(decimals=2)
                    df1_capa = df1_4[['bank', 'bank_level', 'outlet_capacity']].sort_values(
                        'outlet_capacity', ascending=True)

                    bar = px.bar(df1_capa, x="bank", y="outlet_capacity",
                                 category_orders={"bank_level": [
                                     'Big', 'Medium', 'Small']},
                                 color='bank_level', color_discrete_sequence=px.colors.qualitative.Bold,
                                 labels={'bank': '', 'outlet_capacity': 'Number of people being served'}, hover_name='bank')
                    bar.update_layout(xaxis_tickangle=-45, width=630,  height=450, title_text='<b>Outlet capacity of banks</b>',
                                      legend=dict(
                                          x=0.05,
                                          y=1.0,
                                          bgcolor='rgba(255, 255, 255, 0)',
                                          bordercolor='rgba(255, 255, 255, 0)'
                                      ), xaxis_tickfont_size=11)
                    st.plotly_chart(bar)
# https://medium0.com/m/global-identity?redirectUrl=https%3A%2F%2Ftowardsdatascience.com%2Fmake-your-machine-learning-models-come-alive-with-streamlit-48e6eb8e3004

        if type1 == 'Top 10':
            if type2 == 'Bank':
                if cri_select == 'Outlet':
                    df3_outlet_df = df1_1.groupby('bank')[['atm', 'branch', 'office']].agg(
                        'sum').reset_index().sort_values('atm', ascending=False).head(10)
                    df3_outlet = pd.melt(df3_outlet_df, id_vars=[
                                         'bank'], var_name='type', value_name='count')
                    bar = px.bar(df3_outlet, x="bank", y="count", color='type', color_discrete_sequence=px.colors.qualitative.D3_r, labels={
                                 'bank': '', 'count': 'Number of banks'}, hover_name='bank')
                    bar.update_layout(xaxis_tickangle=-45, width=650,  height=450, title_text='<b>Top 10 with the biggest number of outlet</b>',
                                      legend=dict(
                                          x=0.8,
                                          y=1.0,
                                          bgcolor='rgba(255, 255, 255, 0)',
                                          bordercolor='rgba(255, 255, 255, 0)'
                                      ), xaxis_tickfont_size=11)
                    st.plotly_chart(bar)

                elif cri_select == 'Outlet capacity':
                    df1_2 = df1_1[['bank', 'ward', 'ward_pop']].drop_duplicates(keep='first').groupby(
                        'bank')['ward_pop'].agg('sum').reset_index()      # if cri_select == 'Branch capacity':
                    df1_3 = df1_1[['bank', 'bank_level', 'outlet']].groupby(
                        ['bank', 'bank_level'])['outlet'].agg('sum').reset_index()  # df3
                    df1_4 = pd.merge(df1_2, df1_3, on='bank')
                    df1_4['outlet_capacity'] = (df1_4['ward_pop'].divide(
                        df1_4['outlet'])).round(decimals=2)
                    df1_capa = df1_4[['bank', 'bank_level', 'outlet_capacity']].sort_values(
                        'outlet_capacity').head(10)

                    bar = px.bar(df1_capa, x="bank", y="outlet_capacity",
                                 category_orders={"bank_level": [
                                     'Big', 'Medium', 'Small']},
                                 color='bank_level', color_discrete_sequence=px.colors.qualitative.Bold,
                                 labels={'bank': '', 'outlet_capacity': 'Number of people being served'}, hover_name='bank')
                    bar.update_layout(xaxis_tickangle=-45, width=630,  height=450, title_text='<b>Top 10 banks with the smallest number of bank capacity</b>',
                                      legend=dict(
                                          x=0.05,
                                          y=1.0,
                                          bgcolor='rgba(255, 255, 255, 0)',
                                          bordercolor='rgba(255, 255, 255, 0)'
                                      ), xaxis_tickfont_size=11)
                    st.plotly_chart(bar)


###--------------------------Geodesic buffer map---------------------------
    st.markdown("<h3 style = 'font-weight: bold; color: #AD2A1A;'>Geodesic buffer map</h2>",
                unsafe_allow_html=True)
###--------------------------Calculating distance from a specific point----
    st.markdown("<h4 style = 'color:firebrick;'>Calculating distance from a specific point (outlet). </h4>",
                unsafe_allow_html=True)
    st.markdown("<h6 style = 'font-style: italic;color: #CD594A;'>By selecting information in each filter, you choose the center point (red point) to calculate distance. Then the map displays all the points (green ones) around the center point within the radius. Total of points and top listed banks are computing on the right. For more details, you can look up to the full table underneath. </h6>", unsafe_allow_html=True)
    st.write('')

    line1, line2, line3, line4, line5, line6 = st.columns(
        (0.7, 1, 1.2, 1.2, 2.5, 1.2))
    with line1:
        type = st.selectbox(
            'Choose type',  options=df1['type_id'].unique(), index=0)
        df_type = df1[df1['type_id'] == type]
    with line2:
        bank = st.selectbox(
            'Choose bank', options=df_type['bank'].unique(), index=6)
        df_bank = df_type[df_type['bank'] == bank]
    with line3:
        dist = st.selectbox('Choose district',
                            options=df_bank['district'].unique(), index=11)
        df_dist = df_bank[df_bank['district'] == dist]
    with line4:
        commune = st.selectbox(
            'Choose commune', options=df_dist['ward'].unique())
        df_com = df_dist[df_dist['ward'] == commune]
    with line5:
        address = st.selectbox(
            'Choose outlet', options=df_com['dia_chi_cu_the'].unique())
        df_address = df_com[df_com['dia_chi_cu_the'] == address]
    with line6:
        buffer = st.number_input(
            'Radius (km)', min_value=0.0, max_value=20.0, value=0.5, step=0.1, format="%f")

    map1, _, map2 = st.columns((2, 0.1, 2))
    with map1:
        st.write('')
        lat = df_address['latitude']
        lon = df_address['longitude']

        @st.cache_data()
        def buffer_map():
            # %timeit
            df1['distance'] = 6367 * 2 * np.arcsin(np.sqrt(np.sin((np.radians(df1['latitude']) - math.radians(lat))/2)**2 + math.cos(
                math.radians(lat)) * np.cos(np.radians(df1['latitude'])) * np.sin((np.radians(df1['longitude']) - math.radians(lon))/2)**2))
            df1_pick = df1[(df1['distance'] != 0) & (
                df1['distance'] <= buffer) & (df1['type_id'] == type)]
            return df1_pick
        df1_pick = buffer_map()

        @st.cache_data()
        def buffer_map_0():
            # %timeit
            df1['distance'] = 6367 * 2 * np.arcsin(np.sqrt(np.sin((np.radians(df1['latitude']) - math.radians(lat))/2)**2 + math.cos(
                math.radians(lat)) * np.cos(np.radians(df1['latitude'])) * np.sin((np.radians(df1['longitude']) - math.radians(lon))/2)**2))
            df1_pick_0 = df1[(df1['distance'] == 0) & (df1['type_id'] == type)]
            return df1_pick_0
        df1_pick_0 = buffer_map_0()

        df5 = df4[df4.index.isin(df1_pick['district'].unique())]

        fig = go.Figure()
        fig2 = px.choropleth_mapbox(df5, geojson=geojson, locations='id_district', hover_name=df5.index,
                                    # center={'lat':df5['lat'].values[1], 'lon':df5['lon'].values[0]},
                                    color='id_district',
                                    color_discrete_sequence=px.colors.qualitative.Pastel,
                                    zoom=8, opacity=0.6
                                    )

        # fig2 = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=df5['id_district'], z=df5['id_district'],
        #                                     colorscale="Viridis", zmin=0, zmax=12,
        #                                     marker_opacity=0.5, marker_line_width=0))

        fig2.add_trace(go.Scattermapbox(lat=df1_pick[df1_pick['distance'] != 0]['latitude'],
                                        lon=df1_pick[df1_pick['distance']
                                                     != 0]['longitude'],
                                        text="Bank name:" + df1_pick[df1_pick['distance'] != 0].bank.astype(str) + "<br>Type:" + df1_pick[df1_pick['distance'] != 0].type_id.astype(
                                            str) + "<br>Address:" + df1_pick[df1_pick['distance'] != 0].ward.astype(str) + "," + "<br>" + df1_pick[df1_pick['distance'] != 0].district.astype(str),
                                        hoverinfo='text',
                                        below='', opacity=0.7,
                                        marker_size=9, marker_color='rgb(27,158,119)',
                                        # marker = {"color": 'red'}
                                        ))
        fig2.add_trace(go.Scattermapbox(lat=df1_pick_0['latitude'],
                                        lon=df1_pick_0['longitude'],
                                        text="Bank name:" + df1_pick_0.bank.astype(str) + "<br>Type:" + df1_pick_0.type_id.astype(
                                            str) + "<br>Address:" + df1_pick_0.ward.astype(str) + "," + "<br>" + df1_pick_0.district.astype(str),
                                        hoverinfo='text',
                                        below='', opacity=0.8,
                                        marker_size=11, marker_color='red',))

        fig2.update_layout(coloraxis_showscale=False, showlegend=False)
        fig2.update_layout(mapbox_style='light', width=500,
                           height=400, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig2.update_layout(mapbox=dict(
            accesstoken=mapbox_access_token,
            zoom=6,  # change this value correspondingly, for your map
            style="light")  # set your preferred mapbox style
        )
        fig2.update_mapboxes(center_lon=df1_pick['longitude'].values[0],
                             center_lat=df1_pick['latitude'].values[0],
                             zoom=11)
        st.plotly_chart(fig2, use_container_width=True)

        distance = st.expander('See full table')
        with distance:
            df_show = df1_pick[['bank', 'ward', 'district',
                                'distance', 'dia_chi_cu_the']].sort_values(by='distance')
            df_show['distance'] = df_show['distance'].round(decimals=2)
            # sort by distance and groupby bank
            components.html(df_show.set_index('bank').to_html(),
                            height=350, scrolling=True)

    with map2:
        st.write('')
        st.markdown("<h4 style = 'margin-left: 20px;color:firebrick;'>👉 Number of points: %s</h4>" %
                    (len(df1_pick['bank'].index)), unsafe_allow_html=True)
        dfx = pd.DataFrame({'count': df1_pick.groupby('bank').size()}).reset_index(
        ).sort_values(by='count', ascending=False).head(10)
        fig3 = px.bar(dfx, x='bank', y='count', text='count', labels={
                      'count': 'Total of outlets', 'bank': ''}, height=450, width=580, color='count', color_continuous_scale='Sunset')
        fig3.update_layout(title_text='<b>Top 10 banks with most outlets around the center point</b>',
                           xaxis_tickangle=-40, xaxis_tickfont_size=11)
        st.plotly_chart(fig3)


    ###--------------------------Calculating distance from a random longitude/latitide----
    st.markdown("<h4 style = 'color:firebrick;'>Calculating distance from a random point (longitude/latitude). </h4>",
                unsafe_allow_html=True)
    
    # st.markdown("check out this [link](%s)" % url)
    # st.markdown("<h6 style = 'font-style: italic;color: #CD594A;'>Typing longitude and latitude of your desired location (searching for longitude and latitude by using [Google Map](https://www.google.com/maps/place/H%C3%A0+N%E1%BB%99i,+Ho%C3%A0n+Ki%E1%BA%BFm,+H%C3%A0+N%E1%BB%99i,+Vi%E1%BB%87t+Nam/@21.0227387,105.8194541,14z/data=!3m1!4b1!4m5!3m4!1s0x3135ab9bd9861ca1:0xe7887f7b72ca17a9!8m2!3d21.0277644!4d105.8341598)) , you choose the center point (red point) to calculate distance. Then the map displays all the points (green ones) around the center point within the radius. Total of points and top listed banks are computing on the right. For more details, you can look up to the full table underneath. </h6>", unsafe_allow_html=True)


    st.write("Typing longitude and latitude of your desired location (searching for longitude and latitude by using [Google Map](https://www.google.com/maps/place/H%C3%A0+N%E1%BB%99i,+Ho%C3%A0n+Ki%E1%BA%BFm,+H%C3%A0+N%E1%BB%99i,+Vi%E1%BB%87t+Nam/@21.0227387,105.8194541,14z/data=!3m1!4b1!4m5!3m4!1s0x3135ab9bd9861ca1:0xe7887f7b72ca17a9!8m2!3d21.0277644!4d105.8341598)) , you choose the center point (red point) to calculate distance. Then the map displays all the points (green ones) around the center point within the radius. Total of points and top listed banks are computing on the right. For more details, you can look up to the full table underneath.")
    
    st.write('')

    line11, line12, line13 = st.columns(
        (2, 2, 2))
    # Latitude and longitude coordinates are: 21.028511, 105.804817.   
    
    # Max min Latitude
    # 21.026741844340318, 105.79696595534837   
    # 21.00318603149055, 105.87610184471265
    # 
    # max min logitude
    # 21.05053831892403, 105.81343503157282
    # 20.995307480312338, 105.85648392352685
#--------------------------------
    with line11:
        latitude_choose = st.number_input(
            'Latitude', min_value=21.00318, max_value=21.02674, value=21.02578, step=0.00001, format="%f")

    with line12:
        longitude_choose = st.number_input(
            'Longitude', min_value=105.81343, max_value=105.85648, value=105.8532, step=0.00001, format="%f")

    with line13:
        radius_choose = st.number_input(
            'Radius (km) ', min_value=0.0, max_value=20.0, value=0.5, step=0.1, format="%f")

    map3, _, map4 = st.columns((2, 0.1, 2))
    with map3:
        st.write('')
        lat = latitude_choose
        lon = longitude_choose

        @st.cache_data()
        def buffer_map_2():
            # %timeit
            df1['distance_2'] = 6367 * 2 * np.arcsin(np.sqrt(np.sin((np.radians(df1['latitude']) - math.radians(lat))/2)**2 + math.cos(
                math.radians(lat)) * np.cos(np.radians(df1['latitude'])) * np.sin((np.radians(df1['longitude']) - math.radians(lon))/2)**2))
            df1_pick_2 = df1[(df1['distance_2'] != 0) & (
                df1['distance_2'] <= radius_choose)]
            return df1_pick_2
        df1_pick_2 = buffer_map_2()


        @st.cache_data()
        def buffer_map_3():
            # %timeit
            df1['distance_3'] = 6367 * 2 * np.arcsin(np.sqrt(np.sin((np.radians(df1['latitude']) - math.radians(lat))/2)**2 + math.cos(
                math.radians(lat)) * np.cos(np.radians(df1['latitude'])) * np.sin((np.radians(df1['longitude']) - math.radians(lon))/2)**2))
            df1_pick_3 = df1[(df1['distance_3'] <= 0.1)]
            return df1_pick_3
        df1_pick_3 = buffer_map_3()
  


        df_random_location = df4[df4.index.isin(df1_pick_2['district'].unique())]
        
        fig = go.Figure()
        fig4 = px.choropleth_mapbox(df_random_location, geojson=geojson, locations='id_district', hover_name=df_random_location.index,
                                    # center={'lat':df5['lat'].values[1], 'lon':df5['lon'].values[0]},
                                    color='id_district',
                                    color_discrete_sequence=px.colors.qualitative.Pastel,
                                    zoom=8, opacity=0.6
                                    )
        
        # fig2 = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=df5['id_district'], z=df5['id_district'],
        #                                     colorscale="Viridis", zmin=0, zmax=12,
        #                                     marker_opacity=0.5, marker_line_width=0))

        fig4.add_trace(go.Scattermapbox(lat=df1_pick_2[df1_pick_2['distance'] != 0]['latitude'],
                                        lon=df1_pick_2[df1_pick_2['distance']
                                                     != 0]['longitude'],
                                        text="Bank name:" + df1_pick_2[df1_pick_2['distance'] != 0].bank.astype(str) + "<br>Type:" + df1_pick_3[df1_pick_3['distance'] != 0].type_id.astype(
                                            str) + "<br>Address:" + df1_pick_2[df1_pick_2['distance'] != 0].ward.astype(str) + "," + "<br>" + df1_pick_3[df1_pick_3['distance'] != 0].district.astype(str),
                                        hoverinfo='text',
                                        below='', opacity=0.7,
                                        marker_size=9, marker_color='rgb(27,158,119)',
                                        # marker = {"color": 'red'}
                                        ))
        fig4.add_trace(go.Scattermapbox(lat=df1_pick_3['latitude'],
                                        lon=df1_pick_3['longitude'],
                                        text="Bank name:" + df1_pick_3.bank.astype(str) + "<br>Type:" + df1_pick_3.type_id.astype(
                                            str) + "<br>Address:" + df1_pick_3.ward.astype(str) + "," + "<br>" + df1_pick_3.district.astype(str),
                                        hoverinfo='text',
                                        below='', opacity=0.8,
                                        marker_size=11, marker_color='red',))

        fig4.update_layout(coloraxis_showscale=False, showlegend=False)
        fig4.update_layout(mapbox_style='light', width=500,
                           height=400, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig4.update_layout(mapbox=dict(
            accesstoken=mapbox_access_token,
            zoom=6,  # change this value correspondingly, for your map
            style="light")  # set your preferred mapbox style
        )
        fig4.update_mapboxes(center_lon=df1_pick_3['longitude'].values[0],
                             center_lat=df1_pick_3['latitude'].values[0],
                             zoom=11)
        st.plotly_chart(fig4, use_container_width=True)

        distance = st.expander('See full table')
        with distance:
            df_show_3 = df1_pick_3[['bank', 'ward', 'district',
                                'distance', 'dia_chi_cu_the']].sort_values(by='distance')
            df_show_3['distance'] = df_show_3['distance'].round(decimals=2)
            # sort by distance and groupby bank
            components.html(df_show.set_index('bank').to_html(),
                            height=350, scrolling=True)

    with map4:
        st.write('')
        st.markdown("<h4 style = 'margin-left: 20px;color:firebrick;'>👉 Number of points: %s</h4>" %
                    (len(df1_pick_2['bank'].index)), unsafe_allow_html=True)
        dfx_2 = pd.DataFrame({'count': df1_pick_2.groupby('bank').size()}).reset_index(
        ).sort_values(by='count', ascending=False).head(10)
        fig5 = px.bar(dfx_2, x='bank', y='count', text='count', labels={
                      'count': 'Total of outlets', 'bank': ''}, height=450, width=580, color='count', color_continuous_scale='Sunset')
        fig5.update_layout(title_text='<b>Top 10 banks with most outlets around the center point</b>',
                           xaxis_tickangle=-40, xaxis_tickfont_size=11)
        st.plotly_chart(fig5)





#-----------------------------------------3.3. METHODOLOGY----------------------------------

# https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/media
if button == 'Methodology':
    st.subheader('**Introduction**')
    st.write('Vietnam Index for Trade Analytics by Locations (VITAL) is a set of geo-demographic segments for Vietnam, developed by Trade Analystics Company. VITAL classifies every Vietnam ward in big cities into 41 segments based on its outstanding demographic characteristics. VITAL offers a complete set of ancillary databases and links to third-party data, allowing marketers to use data outside of their own customer files to pinpoint products and services that their best customers are most likely to use, as well as locate their best customers on the ground.')
    st.write('These 41 segments are numbered according to their lifestage and affluence scores, then categorized into 9 groups based on the criteria of life stage and affluences.')
    st.subheader('**Methodology**')
    # st.markdown("<h3 style='font-weight: bold;text-align: left; color:firebrick;'>Segment details</h3>", unsafe_allow_html=True)
    st.write('*Choosing filter to view. You can either choose to view by groups of segmentation divided based on the criteria of **life stage** (Younger years, Family life and Mature years), and **affluence** (High, Medium or Low) or to view all the segments belongs to them.*')
    lst,_,_,_ = st.columns((1,1,0.1,2))
    with lst:
        list  = st.selectbox('Level of segment', options = ['Groups', 'All segments'])
    st.write('')
    if list == 'All segments':
        for i in range(19,60):
            image = Image.open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/media/vital_brochure (1)1024_{}.jpg'.format(i))
            st.image(image)

    if list == 'Groups':
        image11 = Image.open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/media/young2.png')
        st.image(image11)
        image12 = Image.open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/media/fam5.png')
        st.image(image12)
        image13 = Image.open('https://raw.githubusercontent.com/thuthuy119/banking-sector-2024/main/media/mar4.png')
        st.image(image13)


#streamlit run 'C:/Users/admin/OneDrive/Máy tính/Vital project/web_demo.py'




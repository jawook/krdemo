# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:12:31 2022

@author: wilkijam
"""

# To execute this locally from terminal: 
# cd C:\Users\wilkijam\Personal GDrive\My Drive\Data Science Random\KiteRight Streamlit\krdemo
# streamlit run krDash.py

import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request, json

px.defaults.color_discrete_sequence = px.colors.qualitative.Vivid

@st.cache
def loadMerge():
    cust = pd.read_csv('KiteRight Customers.csv', encoding_errors='ignore')
    cust['BirthDate'] = pd.to_datetime(cust['BirthDate'])
    cust['Income'] = cust['Income'].str.replace(r'[$,]', '', regex=True)
    cust['FullName'] = (cust['FirstName'].str.title() + ' ' + 
                        cust['LastName'].str.title())
    
    sales = pd.read_csv('KiteRight Sales.csv')
    sales['InventoryDate'] = pd.to_datetime(sales['InventoryDate'])
    sales['SoldDate'] = pd.to_datetime(sales['SoldDate'])
    sales['SoldISOWeek'] = sales['SoldDate'].dt.isocalendar().week
    sales['SoldISOYear'] = sales['SoldDate'].dt.isocalendar().year
    sales['SoldISODoW'] = sales['SoldDate'].dt.dayofweek
    sales['SoldFDoW'] = sales['SoldDate'] - pd.TimedeltaIndex(sales['SoldDate'].dt.dayofweek, unit='d')
    sales['SoldYear'] = sales['SoldDate'].dt.year
    
    regs = pd.read_csv('KiteRight Regions.csv')
    
    cats = pd.read_csv('KiteRight Categories.csv')
    
    prods = pd.read_csv('KiteRight Products.csv')
    prods = pd.merge(left=prods, right=cats, on='CategoryKey', how='left')
    prods['Twintip'] = [1 if j.endswith('cm') else 0 for j in prods['Size']]
    prods['Surfboard'] = [1 if j.endswith('"') else 0 for j in prods['Size']]
        
    merge = sales.copy()
    merge = pd.merge(left=sales, right=cust, on='CustomerKey', how='left')
    merge = pd.merge(left=merge, right=prods, on='ProductKey', how='left')
    merge = pd.merge(left=merge, right=regs, on='RegionKey', how='left')
    
    return merge

merge = loadMerge()

#%% Get get lat/lon coordinates for mapping later
def getCoJson():
    urlCo = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries.json"
    with urllib.request.urlopen(urlCo) as url:
        jsonCo = pd.DataFrame(json.loads(url.read().decode()))
    jsonCo = jsonCo[['name', 'latitude', 'longitude']]
    jsonCo.rename(columns={'name': 'Country'},
                  inplace=True)
    jsonCo['latitude'] = jsonCo['latitude'].astype(float)
    jsonCo['longitude'] = jsonCo['longitude'].astype(float)
    return jsonCo
    
def getProvJson():
    urlProv = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/states.json"
    with urllib.request.urlopen(urlProv) as url:
        jsonProv = pd.DataFrame(json.loads(url.read().decode()))
    jsonProv = jsonProv[['name', 'latitude', 'longitude']]
    jsonProv.rename(columns={'name': 'Province'},
                    inplace=True)
    jsonProv['latitude'] = jsonProv['latitude'].astype(float)
    jsonProv['longitude'] = jsonProv['longitude'].astype(float)
    return jsonProv

jsonProv = getProvJson()
jsonCo = getCoJson()

#%% Constraints for page
mindate = st.sidebar.date_input('First date shown: ', 
                                min(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))

maxdate = st.sidebar.date_input('Last date shown: ', 
                                max(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))

catSel = st.sidebar.multiselect('Selected category for category limited visuals', 
                                merge['CategoryName'].unique())

#%% Global date data limitation
dtLimitMerge = merge[(merge['SoldDate'].dt.date >= mindate) & 
                   (merge['SoldDate'].dt.date <= maxdate)]

#%% Creation of date-limited figures
# cs = px.colors.qualitative.Vivid

kiteData = dtLimitMerge[dtLimitMerge['CategoryName'] =='Kites'].groupby(by='Size')
kiteFig = px.bar(kiteData['SoldQuantity'].sum().sort_values(),
                 orientation='v', title='Kite Quantity Sold by Size')
kiteFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")

sBrdData = dtLimitMerge[(dtLimitMerge['CategoryName'] =='Boards') &
                      (dtLimitMerge['Surfboard'] == 1)].groupby(by='Size')
sBrdFig = px.bar(sBrdData['SoldQuantity'].sum().sort_values(),
                 orientation='v', title='Surfboard Quantity Sold by Size')
sBrdFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")

tTipData = dtLimitMerge[(dtLimitMerge['CategoryName'] =='Boards') &
                      (dtLimitMerge['Twintip'] == 1)].groupby(by='Size')
tTipFig = px.bar(tTipData['SoldQuantity'].sum().sort_values(),
                 orientation='v', title='Twintip Quantity Sold by Size')
tTipFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")

clthData = dtLimitMerge[(dtLimitMerge['CategoryName'] == 
                       'Clothing')].groupby(by='Size')
clthFig = px.bar(clthData['SoldQuantity'].sum().sort_values(),
                 orientation='v', title='Clothing Quantity Sold by Size')
clthFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")

trmpFig = px.treemap(dtLimitMerge, 
                     path=[px.Constant("All"), 'CategoryName'], 
                     values='SoldQuantity', 
                     title='Quantity Sold by Product Category')

#%% Creation of date and category limited figures

@st.cache
def limCat(catList, dfin):
    if catList==[]:
        dcLimitMerge = dfin.copy()
    else:
        dcLimitMerge = dfin[dfin['CategoryName'].isin(catList)]
    return dcLimitMerge

dcLimitMerge = limCat(catSel, dtLimitMerge)

wkSalesData = dcLimitMerge.groupby(by=['SoldFDoW', 'CategoryName']).sum()['SoldQuantity'].unstack()
wkSalesFig = px.bar(wkSalesData)
wkSalesFig.layout.update(showlegend=False, yaxis_tickformat=",.0d")

sumTblData = dcLimitMerge.groupby(by=['CategoryName', 'Model']
                                  ).agg({'SoldQuantity': 'sum',
                                         'Price': 'mean'})
sumTblData.sort_values('SoldQuantity', inplace=True, ascending=False)
sumTblData = sumTblData.reset_index()
sumTblData.rename(columns={'CategoryName': 'Category',
                           'SoldQuantity': 'Quantity Sold',
                           'Price': 'Avg. Price'},
                  inplace=True)

@st.cache
def mapDriver(option):
    if option == 'Province':
        mapData = dcLimitMerge.groupby(by='Province'
                                    ).agg({'SoldQuantity': 'sum'}
                                              ).reset_index()
        mapData = pd.merge(left=mapData, right=jsonProv, 
                        on='Province', how='left')
    else:
        mapData = dcLimitMerge.groupby(by='Country'
                                       ).agg({'SoldQuantity': 'sum'}
                                             ).reset_index()
        mapData = pd.merge(left=mapData, right=jsonCo, 
                        on='Country', how='left')
    mapData.dropna(inplace=True)
    return mapData

#%% Dashboard construction
st.header('KiteRight: Analysis of Product Orders')
st.subheader('Sales Quantity by Product Category')

st.plotly_chart(trmpFig, use_container_width=True)

quadChartL, quadChartR = st.columns(2)
with quadChartL:
    st.plotly_chart(kiteFig, use_container_width=True)
    st.plotly_chart(sBrdFig, use_container_width=True)
    
with quadChartR:
    st.plotly_chart(tTipFig, use_container_width=True)
    st.plotly_chart(clthFig, use_container_width=True)

st.subheader('Weekly Orders')    
st.plotly_chart(wkSalesFig)

st.subheader('Top Selling Models')
st.table(sumTblData.style.format({'Quantity Sold': "{:,}",
                                  'Avg. Price': "${:,.2f}"}))

st.subheader('Orders by Region')
radioMap = st.radio('Which geography level would you like to show?', 
                    ['Country', 'Province'])
mapData = mapDriver(radioMap)
# mapFig = st.map(mapData)
# mapFig
mapFig2 = px.scatter_geo(mapData, lat='latitude', lon='longitude', 
                         size='SoldQuantity', hover_name=radioMap)
mapFig2
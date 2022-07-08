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
cs = px.colors.qualitative.Vivid

kiteData = dtLimitMerge[dtLimitMerge['CategoryName'] =='Kites'].groupby(by='Size')
kiteFig = px.bar(kiteData['SoldQuantity'].sum().sort_values(),
                 orientation='h', title='Kite Quantity Sold by Size',
                 color_discrete_sequence=cs)
kiteFig.layout.update(showlegend=False)

sBrdData = dtLimitMerge[(dtLimitMerge['CategoryName'] =='Boards') &
                      (dtLimitMerge['Surfboard'] == 1)].groupby(by='Size')
sBrdFig = px.bar(sBrdData['SoldQuantity'].sum().sort_values(),
                 orientation='h', title='Surfboard Quantity Sold by Size',
                 color_discrete_sequence=cs)
sBrdFig.layout.update(showlegend=False)

tTipData = dtLimitMerge[(dtLimitMerge['CategoryName'] =='Boards') &
                      (dtLimitMerge['Twintip'] == 1)].groupby(by='Size')
tTipFig = px.bar(tTipData['SoldQuantity'].sum().sort_values(),
                 orientation='h', title='Twintip Quantity Sold by Size',
                 color_discrete_sequence=cs)
tTipFig.layout.update(showlegend=False)

clthData = dtLimitMerge[(dtLimitMerge['CategoryName'] == 
                       'Clothing')].groupby(by='Size')
clthFig = px.bar(clthData['SoldQuantity'].sum().sort_values(),
                 orientation='h', title='Clothing Quantity Sold by Size',
                 color_discrete_sequence=cs)
clthFig.layout.update(showlegend=False)

trmpFig = px.treemap(dtLimitMerge, 
                     path=[px.Constant("All"), 'CategoryName'], 
                     values='SoldQuantity', 
                     title='Quantity Sold by Product Category',
                     color_discrete_sequence=cs)

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

wkSalesFig = px.bar(wkSalesData,
                    title='Orders by Week',
                    # x='SoldFDoW', y='SoldQuantity', color='CategoryName',
                    color_discrete_sequence=cs)
wkSalesFig.layout.update(showlegend=False)

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
    
st.plotly_chart(wkSalesFig)
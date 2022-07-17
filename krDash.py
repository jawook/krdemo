# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:12:31 2022

@author: wilkijam
"""
#!! MAKE A CUSTOMER SELECTOR THAT INCLUDES A FEW PIECES OF DETAIL!!
# To execute this locally from terminal: 
# cd C:\Users\wilkijam\Personal GDrive\My Drive\Data Science Random\KiteRight Streamlit\krdemo
# streamlit run krDash.py

#%% Load required packages and set defaults
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import numpy as np

px.defaults.color_discrete_sequence = px.colors.qualitative.Vivid

#%% Load & merge data
@st.cache
def loadMerge():
    cust = pd.read_csv('KiteRight Customers.csv', encoding_errors='ignore')
    cust['BirthDate'] = pd.to_datetime(cust['BirthDate'])
    cust['Income'] = cust['Income'].str.replace(r'[$,]', '', regex=True).astype(int)
    cust['FullName'] = (cust['FirstName'].str.title() + ' ' + 
                        cust['LastName'].str.title())
    cust['Age'] = np.floor((dt.datetime.today() - 
                            pd.to_datetime(cust['BirthDate'])).dt.days /
                           365.25)
    incLabels = ['Low', 'Average', 'High', 'Very High']
    incBins = [0, 60000, 100000, 150000, 1000000]
    cust['IncLevel'] = pd.cut(cust['Income'], bins=incBins,
                              labels=incLabels)
    cust['login'] = [x.split('@')[0] for x in cust['Email']]
    cust['listValue'] = (cust['FullName'] + ' - ' + cust['login'] + 
                         ' - ' + cust['CustomerKey'].astype(str))

    sales = pd.read_csv('KiteRight Sales.csv')
    sales['InventoryDate'] = pd.to_datetime(sales['InventoryDate'])
    sales['SoldDate'] = pd.to_datetime(sales['SoldDate'])
    sales['SoldISOWeek'] = sales['SoldDate'].dt.isocalendar().week
    sales['SoldISOYear'] = sales['SoldDate'].dt.isocalendar().year
    sales['SoldISODoW'] = sales['SoldDate'].dt.dayofweek
    sales['SoldFDoW'] = (sales['SoldDate'] - 
                         pd.TimedeltaIndex(sales['SoldDate'].dt.dayofweek, 
                                           unit='d'))
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

    merge['Revenue'] = merge['Price'] * merge['SoldQuantity']
    merge['COGS'] = merge['Cost'] * merge['SoldQuantity']
    
    lst = merge, cust, sales, regs, cats, prods
    
    return lst

(merge, cust, sales, regs, cats, prods) = loadMerge()

jsonCo = pd.read_csv('jsonCo.csv')
jsonProv = pd.read_csv('jsonProv.csv')
    
#%% Sidebar

pagePick = st.sidebar.radio('Select a page to show', 
                            ['Overview of Units Sold',
                             'Customer Overview',
                             'Customer Detail'])

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

@st.cache
def kiteFig(df):
    kiteData = df[df['CategoryName'] =='Kites'].groupby(by=['Size', 'Colour'])
    kiteFig = px.bar(kiteData.sum().sort_values(by='Size').unstack(), color='Colour',
                     orientation='v', title='Kite Quantity Sold by Size')
    kiteFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return kiteFig

@st.cache
def sBrdFig(df):
    sBrdData = df[(df['CategoryName'] =='Boards') &
                  (df['Surfboard'] == 1)].groupby(by='Size')
    sBrdFig = px.bar(sBrdData['SoldQuantity'].sum().sort_values(),
                     orientation='v', title='Surfboard Quantity Sold by Size')
    sBrdFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return sBrdFig

@st.cache
def tTipFig(df):
    tTipData = df[(df['CategoryName'] =='Boards') &
                  (df['Twintip'] == 1)].groupby(by='Size')
    tTipFig = px.bar(tTipData['SoldQuantity'].sum().sort_values(),
                     orientation='v', title='Twintip Quantity Sold by Size')
    tTipFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return tTipFig

@st.cache
def clthFig(df):
    clthData = dtLimitMerge[(df['CategoryName'] == 
                           'Clothing')].groupby(by='Size')
    clthFig = px.bar(clthData['SoldQuantity'].sum().sort_values(),
                     orientation='v', title='Clothing Quantity Sold by Size')
    clthFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return clthFig

@st.cache
def trmpFig(df): 
    trmpFig = px.treemap(df, 
                         path=[px.Constant("All"), 'CategoryName', 'Manufacturer', 'Model'], 
                         values='SoldQuantity', 
                         title='Quantity Sold by Product Category')
    return trmpFig

#%% Creation of date and category limited figures

@st.cache
def limCat(catList, dfin):
    if catList==[]:
        dcLimitMerge = dfin.copy()
    else:
        dcLimitMerge = dfin[dfin['CategoryName'].isin(catList)]
    return dcLimitMerge

dcLimitMerge = limCat(catSel, dtLimitMerge)

@st.cache(allow_output_mutation=True)
def wkSalesFig(df):
    wkSalesData = df.groupby(by=['SoldFDoW', 
                                 'CategoryName']).sum()['SoldQuantity'].unstack()
    wkSalesFig = px.bar(wkSalesData)
    wkSalesFig.layout.update(showlegend=False, yaxis_tickformat=",.0d")
    return wkSalesFig

@st.cache
def sumTblData(df):
    sumTblData = df.groupby(by=['CategoryName', 'Model']
                                      ).agg({'SoldQuantity': 'sum',
                                             'Price': 'mean'})
    sumTblData.sort_values('SoldQuantity', inplace=True, ascending=False)
    sumTblData = sumTblData.reset_index()
    sumTblData.rename(columns={'CategoryName': 'Category',
                               'SoldQuantity': 'Quantity Sold',
                               'Price': 'Avg. Price'},
                      inplace=True)
    return sumTblData

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

@st.cache(allow_output_mutation=True)
def mapFig(df, sel):
    mapFig = px.scatter_geo(df, lat='latitude', lon='longitude', 
                            size='SoldQuantity', hover_name=sel,
                            size_max=40)
    return mapFig

#%% Customer overview calculations & figures
numCusts = len(pd.unique(cust['CustomerKey']))
aveAge = cust['Age'].mean()
aveInc = cust['Income'].mean()

@st.cache
def ordByGendFig():
    ordByGendData = dcLimitMerge.groupby(by='Gender').agg({'SoldQuantity': 'sum'})
    ordByGendData.sort_values(by='SoldQuantity', ascending=False, inplace=True)
    ordByGendFig = px.bar(ordByGendData, orientation='v',
                          title='Units Sold by Gender')
    ordByGendFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return ordByGendFig

@st.cache
def ordByIncFig():
    ordByIncData = dcLimitMerge.groupby(by='IncLevel').agg({'SoldQuantity': 'sum'})
    ordByIncData.sort_values(by='SoldQuantity', ascending=False, inplace=True)
    ordByIncFig = px.bar(ordByIncData, orientation='v',
                         title='Units Sold by Income Category')
    ordByIncFig.layout.update(showlegend=False, yaxis_title='', yaxis_tickformat=",.0d")
    return ordByIncFig

@st.cache
def ordByChildFig():
    ordByChildData = dcLimitMerge.groupby(by='Children').agg({'SoldQuantity': 'sum'})
    ordByChildData.sort_values(by='SoldQuantity', ascending=False, inplace=True)
    ordByChildFig = px.bar(ordByChildData, orientation='v',
                         title='Units Sold by # of Children')
    ordByChildFig.layout.update(showlegend=False, yaxis_title='', 
                                yaxis_tickformat=",.0d", xaxis_dtick=1)
    return ordByChildFig

def topCustTable(df):
    topCustData = df.groupby(by='CustomerKey').agg({'FullName': 'first',
                                                    'SoldQuantity': 'sum',
                                                    'Revenue': 'sum'})
    topCustData.sort_values(by='Revenue', ascending=False, inplace=True)
    topCustData.reset_index()
    topCustData.rename(columns={'FullName': 'Name',
                                'Sold Quantity': 'Units Bought'},
                       inplace=True)
    return topCustData
    
#%% Customer detail calculations

# Build a list for the selectbox that contains customerID
custList = cust['listValue'].sort_values()

@st.cache
def pullCustData(df, sel):
    custData = df[df['listValue']==sel]
    return custData

@st.cache
def pullCustProds(df):
    custProds = df.groupby(by=['CategoryName', 'Model']).agg({'SoldQuantity': 'sum',
                                                              'Revenue': 'sum'})
    custProds = custProds.reset_index()
    custProds.rename(columns={'CategoryName': 'Category',
                              'SoldQuantity': 'Units Bought'},
                     inplace=True)
    return custProds

#%% Dashboard construction
def pgSold():
    st.header('KiteRight: Analysis of Product Orders')
    st.subheader('Sales Quantity by Product Category')
    
    st.plotly_chart(trmpFig(dtLimitMerge), use_container_width=True)
    
    quadChartL, quadChartR = st.columns(2)
    with quadChartL:
        st.plotly_chart(kiteFig(dtLimitMerge), use_container_width=True)
        st.plotly_chart(sBrdFig(dtLimitMerge), use_container_width=True)
        
    with quadChartR:
        st.plotly_chart(tTipFig(dtLimitMerge), use_container_width=True)
        st.plotly_chart(clthFig(dtLimitMerge), use_container_width=True)
    
    st.subheader('Weekly Orders')    
    st.plotly_chart(wkSalesFig(dcLimitMerge), use_container_width=True)
    
    st.subheader('Top Selling Models')
    st.table(sumTblData(dcLimitMerge).style.format({'Quantity Sold': "{:,}",
                                        'Avg. Price': "${:,.2f}"}))
    
    st.subheader('Orders by Region')
    radioMap = st.radio('Which geography level would you like to show?', 
                        ['Country', 'Province'])
    st.plotly_chart(mapFig(mapDriver(radioMap), radioMap), 
                    use_container_width=True)
    
def pgCustomers():
    st.header('KiteRight: Analysis of Customers')
    st.subheader('Key Statistics')
    
    st.markdown(('**Total Customers:** {:,}').format(numCusts))
    st.markdown(('**Average age:** {:,.0f}').format(aveAge))
    st.markdown(('**Average income:** ${:,.0f}').format(aveInc))

    keyStatsL, keyStatsR = st.columns(2)
    with keyStatsL:
        st.plotly_chart(ordByGendFig(), use_container_width=True)
        st.plotly_chart(ordByChildFig(), use_container_width=True)
    with keyStatsR:
        st.plotly_chart(ordByIncFig(), use_container_width=True)
    
    st.subheader('Top Customers Summary')
    st.table(topCustTable(dcLimitMerge)[:35].style.format({'Units Bought': "{:,}",
                                                           'Revenue': "${:,.2f}"}))
def pgCustDetail():
    st.header('KiteRight: Individual Customer Detail')
    selCust = st.selectbox('Selected customer: ', options=custList)
    custTrans = pullCustData(dcLimitMerge, selCust)
    custProds = pullCustProds(custTrans)
    
    st.subheader('Customer Details: ')
    if len(custTrans)==0:
        st.markdown('**No transactions for this customer under these filter criteria**')
    else:
        st.write(str(custTrans['FullName'].unique()[0]))
    
        custDetL, custDetR = st.columns(2)
        with custDetL:
            st.markdown('**Total Revenue:** ${:,.0f}'.format(sum(custTrans['Revenue'])))
            st.markdown('**Units Sold:** {:,.0f}'.format(sum(custTrans['SoldQuantity'])))
        with custDetR:
            st.markdown('**Income Level:** ' + str(custTrans['IncLevel'].unique()[0]))
            st.markdown('**Age :** {:,.0f}'.format(custTrans['Age'].unique()[0]))
        st.table(custProds.style.format({'Units Bought': "{:,}",
                                         'Revenue': "${:,.2f}"}))
            
if pagePick == 'Overview of Units Sold':
    pgSold()
elif pagePick == 'Customer Overview':
    pgCustomers()
elif pagePick == 'Customer Detail':
    pgCustDetail()
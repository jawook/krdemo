# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:12:31 2022

@author: wilkijam
"""

import streamlit as st
import pandas as pd

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

mindate = st.sidebar.date_input('First date shown: ', min(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))

maxdate = st.sidebar.date_input('Last date shown: ', max(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))

limitMerge = merge[(merge['SoldDate'].dt.date >= mindate) & 
                   (merge['SoldDate'].dt.date <= maxdate)]
kiteData = limitMerge[limitMerge['CategoryName'] =='Kites'].groupby(by='Size')
st.bar_chart(kiteData['SoldQuantity'].sum())
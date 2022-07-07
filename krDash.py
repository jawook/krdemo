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

merge = sales.copy()
merge = pd.merge(left=sales, right=cust, on='CustomerKey', how='left')
prods = pd.merge(left=prods, right=cats, on='CategoryKey', how='left')
merge = pd.merge(left=merge, right=prods, on='ProductKey', how='left')
merge = pd.merge(left=merge, right=regs, on='RegionKey', how='left')

maxdate = st.sidebar.date_input('Active Dates: ', max(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))
mindate = st.sidebar.date_input('Active Dates: ', min(merge['SoldDate']), 
                                max_value=max(merge['SoldDate']), 
                                min_value=min(merge['SoldDate']))
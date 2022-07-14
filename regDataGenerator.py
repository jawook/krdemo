# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 00:50:15 2022

@author: wilkijam
"""

import urllib.request
import pandas as pd
import json

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

jsonProv.to_csv('jsonProv.csv')
jsonCo.to_csv('jsonCo.csv')
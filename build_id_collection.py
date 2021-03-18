###Dependecies
import sqlite3
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time
import numpy as np
from config import skey
import json
import pprint as pp
from collections import OrderedDict 


#shoutout to my friend for supplying our starting user id
initial_id = "76561198048037824"

def build_collection(initial_id):
    friend_list_url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={skey}&steamid={initial_id}&relationship=friend"
    first_query = requests.get(friend_list_url).json()

    #initialize container for our steam ids
    steamid_collection = []
    for i in range(len(first_query["friendslist"]["friends"])):
        steamid_collection.append(first_query["friendslist"]["friends"][i].get("steamid"))
        
    #now to find friends of friends
    i = 0
    while len(steamid_collection) <= 20000:

        #reset query url for next steam id in collection
        friend_list_url = f"""http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={skey}&steamid={steamid_collection[i]}&relationship=friend"""


        #new query from extracted steam id
        try:
            friend_query = requests.get(friend_list_url).json()
            current_friendslist_length = len(friend_query["friendslist"]["friends"])
            #print(current_friendslist_length)
        except:
            "KeyError"

        #2nd loop for collecting current steam_id's friends
        for j in range(current_friendslist_length):
            try:
                steamid_collection.append(friend_query["friendslist"]["friends"][j].get("steamid"))
            except:
                "KeyError"
        i+=1

    steamid_collection = set(steamid_collection)
    steamid_collection = list(steamid_collection)
    total_ids_found = (len(steamid_collection))            
    print(f"total ids collected: {total_ids_found}")

    #print(steamid_collection[0])

    return steamid_collection
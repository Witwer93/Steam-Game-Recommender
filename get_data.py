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

# Retrieve page with the requests module
# executable_path = {'executable_path': ChromeDriverManager().install()}
# browser = Browser('chrome', **executable_path, headless=False)

#list for steamids_that returned no game data
bad_id_list = []
#dictionary to store game_titles and corresponding appids
app_ids = []
#function to identify each game from its appid
def demystify(appid):
    
    identifier = str(appid)

    #set base url for database that identifies games using appid
    base_appid_url = "https://steamdb.info/app/"
    
    #scrape the game title from steamdb.info
    browser.visit(base_appid_url + identifier)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    try:
        game_title = soup.find('h1').get_text()
    except:
        "KeyError"    
    game_ids.update({identifier : game_title})
    
    return game_title

#function to collect account name and profile url
def basic_user_data(steamid):
    
    #construct container for user profile
    user_dictionary = OrderedDict({"_id" : steamid})
    
    #api url for player summary
    player_summary_url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={skey}&steamids={steamid}"
                         )
    
    response = requests.get(player_summary_url).json()
    #extract data from json file
    try:
        user_dictionary.update({"current_account_name" : response['response']['players'][0].get("personaname")})
        user_dictionary.update({"original_account_name" : response['response']['players'][0].get("realname")})
        user_dictionary.update({"profile_url" : response['response']['players'][0].get("profileurl")})
    except:
        "KeyError"
        print(f"error at {steamid}")
    
    return user_dictionary

#function to collect specified users owned games and hours played for each game
# def advanced_user_data(steamid, user_dictionary):
    
#     #api url for user's game data
#     owned_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={skey}&steamid={steamid}&format=json"
#     game_list = requests.get(owned_games_url).json()
    
#     #print(f"found {game_list["response"]["game_count"]} total games for id: {steamid}"
#     #intialize temporary dictionary container
#     user_game_stats = {}
    
#     play_count = 0
#     for i in range(game_list["response"]["game_count"]):
    
#         #initialize temporary variables
#         appid = 0
        
#         try:
#             if game_list["response"]["games"][i].get("playtime_forever") != 0:
#                 play_count += 1
#                 #pull game id
#                 appid = game_list["response"]["games"][i].get("appid")
#                 identifier = str(appid)
                
#                 #identify the game
#                 if identifier not in game_ids:
#                     name_of_the_game = demystify(appid)
#                 elif identifier in game_ids:
#                     name_of_the_game = game_ids[appid]
                    
#                 hours_played = game_list["response"]["games"][i].get("playtime_forever")

#                 user_game_stats.update({name_of_the_game : {"appid" : appid,
#                                                             "hours played" : "{:.2f}".format(hours_played/60)}
#                                        })
#         except:
#             "KeyError"
               
            
#     user_dictionary.update({"total_games_played" : play_count})
#     user_dictionary.update({"user_game_data" : user_game_stats})
#     return user_dictionary
def advanced_user_data2(steamid, user_dictionary):
    
    #api url for user's game data
    owned_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={skey}&steamid={steamid}&format=json"
    game_list = requests.get(owned_games_url).json()

    #print(f"found {game_list['response']['game_count']} total games for id: {steamid}")
    
    #intialize temporary dictionary container
    user_game_stats = []
    try:
        user_dictionary.update({"total_games_owned" : game_list["response"]["game_count"]})
    except:
        "KeyError"
        bad_id_list.append(steamid)
        return None 
    
    play_count = 0
    for i in range(game_list["response"]["game_count"]):

        #initialize temporary variables
        appid = 0
        
        try:
            if game_list["response"]["games"][i].get("playtime_forever") != 0:
                play_count += 1
                #pull game id
                appid = str(game_list["response"]["games"][i].get("appid"))
                name_of_the_game = "game"+str(i)
                app_ids.append(appid)
                
                
                hours_played = game_list["response"]["games"][i].get("playtime_forever")
                
                game_info = {'app_id' : appid,
                             'hours_played' : "{:.2f}".format(hours_played/60),
                             'game_title' : name_of_the_game}
                
                user_game_stats.append(game_info)

        except:
            "KeyError"
            
    user_dictionary.update({"total_games_played" : play_count})
    user_dictionary.update({"user_game_data" : user_game_stats})
    return user_dictionary

def all_user_data(steamid):

    user_dictionary = basic_user_data(steamid)
    
    final_user_dictionary = advanced_user_data2(steamid, user_dictionary)
    
    return final_user_dictionary


from urllib import request
from flask import Flask,render_template, request
import pickle


import os
import numpy as np
import pandas as pd
from surprise import Reader
from surprise import Dataset
from surprise.model_selection import train_test_split
#from sklearn.model_selection import train_test_split
from surprise import KNNBasic
from surprise import accuracy
import random

#Para garantizar reproducibilidad en resultados
seed = 10
random.seed(seed)
np.random.seed(seed)  


app=Flask(__name__)


pkl_filename = "usa_model_item_item_k10.pkl" ##Modelo

all_users=pd.read_csv("all_users.csv")
all_artist=pd.read_csv("all_artist.csv")

with open(pkl_filename, 'rb') as file:
    pickle_model = pickle.load(file)

@app.route('/')
def index():
    titulo= " Taller 1 Sistemas de Recomendación"
    Countries=['USA','Japan','Germany']
    return render_template("index.html", title=titulo,Country=Countries)


@app.route('/login')
def new_users():
    titulo= " Taller 1 Sistemas de Recomendación"
    Countries=['USA','Japan','Germany']
    return render_template("results.html", title=titulo,Country=Countries)

@app.route('/form', methods=["POST"])
def form():
    user=request.form.get("user_id")
    artist=request.form.get("artist_name")
    titulo= "Taller 1 Sistemas de Recomendación"

    if not  user or not artist:
        error_statement='Debes llenar ambos campos... intenta de nuevo'
        return render_template("error_form.html", error_statement=error_statement) 
    

    selected_user=all_users[all_users["User_id"]==user]
    selected_artist=all_artist[all_artist["Artist_Name"]==artist]

    is_user=1==selected_user.shape[0]
    is_artist=1==selected_artist.shape[0]

    if is_user==False or is_artist==False:
        error_statement='El artista o el usuario no existen, intenta de nuevo'
        return render_template("error_form.html", error_statement=error_statement) 

    country_user=selected_user['country'].to_list()
    country_user=country_user[0]
    v=pd.read_csv("valid_c_f.csv")
    valid_country=1==(v[v['Country']==country_user].shape[0])

    if valid_country==False:
        error_statement=f'El país de este usuario {country_user} no tiene suficiente información, intenta de nuevo'
        return render_template("error_form.html", error_statement=error_statement) 

    
    
    nombre_file=v[v['Country']==country_user]['file'].to_list()
    nombre_file=nombre_file[0]
    artist_id=selected_artist['Artist_Id'].to_list()
    artist_id=artist_id[0]

    with open(nombre_file, 'rb') as file:
        pickle_model = pickle.load(file)

    p=pickle_model.predict(user,artist_id)
    p=p.est

    if p>= 2:
        likehood=f'Basados en tus  gustos {user} este artista  {artist} seguro entra a tus favoritos!'
    elif p >=1:
        likehood=f'Basados en tus gustos {user}  este artista {artist} te gustaría'
    elif p > 0.5:
        likehood=f'Basados en tus gustos {user} este artista {artist} no debe ser de tus favoritos'
    else:
        likehood=f'Basados en tus gustos  {user} este artista {artist} es probable que no te guste'

    return render_template("form.html", title=titulo
    ,user=user
    ,artis=artist
    ,gusto=likehood)
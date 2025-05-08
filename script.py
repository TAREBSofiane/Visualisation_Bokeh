import pandas as pd
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Tabs, TabPanel, Div
from bokeh.palettes import Set1
from bokeh.transform import factor_cmap
from bokeh.layouts import row, column
import os
import numpy as np
import json


## Converts decimal longitude/latitude to Web Mercator format
def coor_wgs84_to_web_mercator(v, type):
    k = 6378137
    if type == 'lon':
        return v * (k * np.pi/180.0)
    elif type == 'lat':
        return np.log(np.tan((90 + v) * np.pi/360.0)) * k


#### Importation et traitement des données

##############################################################################
## Ficher 1 : Données sur les lignes Star
file_path = os.path.join(os.getcwd(), "data/star_itineraires_actifs.csv")
df_itineraires = pd.read_csv(file_path, delimiter=";")

# suppression des lignes de type 'Spéciale' et 'BreizhGo' car trop nombreuses et peu pertinentes
to_del = df_itineraires['li_type'].isin(['Spéciale', 'BreizhGo'])
df_itineraires = df_itineraires[~to_del & (df_itineraires['iti_principal'] == 'oui')]

# Suppression des colonnes inutiles
df_itineraires = df_itineraires.rename(columns={'Geo Point': 'Geo_Point', 'Geo Shape': 'Geo_Shape'})
to_keep = ["li_type", "Geo_Shape", "Geo_Point", "li_num", "iti_nom", "li_type", "ap_adresse", "li_c", "li_couleur_hex"]
to_del = [col for col in df_itineraires.columns if col not in to_keep]
df_itineraires = df_itineraires.drop(columns=to_del)

# Conversion des coordonnées
df_itineraires['Geo_Shape'] = df_itineraires['Geo_Shape'].apply(lambda v: json.loads(v)["coordinates"][0])
df_itineraires['xs'] = df_itineraires["Geo_Shape"].apply(lambda v: [coor_wgs84_to_web_mercator(c[0], 'lon') for c in v])
df_itineraires['ys'] = df_itineraires["Geo_Shape"].apply(lambda v: [coor_wgs84_to_web_mercator(c[1], 'lat') for c in v])

##############################################################################
## Ficher 2 : Données sur les arrêts Star
file_path = os.path.join(os.getcwd(), "data/star_arrets_physiques_actifs.csv")
df_arrets = pd.read_csv(file_path, delimiter=";")

# Suppression des colonnes inutiles
df_arrets = df_arrets.rename(columns={"Commune (nom)": "Commune_nom"})
to_keep = ['Coordonnées', "date", 'Commune_nom', 'arret_num', 'ap_adresse']
to_del = [col for col in df_arrets.columns if col not in to_keep]
df_arrets = df_arrets.drop(columns=to_del)

# Conversion des coordonnées
df_arrets[['coordy', 'coordx']] = df_arrets['Coordonnées'].str.split(', ', expand=True).astype(float)
df_arrets['coordx'] = df_arrets['coordx'].apply(lambda v: coor_wgs84_to_web_mercator(v, 'lon'))
df_arrets['coordy'] = df_arrets['coordy'].apply(lambda v: coor_wgs84_to_web_mercator(v, 'lat'))

##############################################################################
## Ficher 3 : Données sur les fréquentations
file_path = os.path.join(os.getcwd(), "data/eco-counter-data.csv")
df_count = pd.read_csv(file_path, delimiter=";")

# Création de nouvelles colonnes heure, jour, mois et année
df_count['date'] = pd.to_datetime(df_count['date'], format='%Y-%m-%dT%H:%M:%S%z')
df_count['date'] = df_count['date'].apply(lambda x: x.tz_localize(None))
df_count['heure'] = df_count['date'].dt.hour
df_count['jour_du_mois'] = df_count['date'].dt.day
df_count['mois'] = df_count['date'].dt.month
df_count['annee'] = df_count['date'].dt.year

# Suppression des colonnes inutiles et des données manquantes
drop_list = ["isoDate", "status", "ID", "sens"]
df_count = df_count.drop(columns = drop_list)
df_count = df_count.loc[:, df_count.isna().sum() < 0.1*df_count.shape[0]]
df_count = df_count.dropna(axis=0)

df_count = df_count.sort_values(by="date")

# Création de Pandas Séries des données nécessaires pour notre affichage
df_heure = df_count.groupby(by = "heure")["counts"].mean()
df_mois = df_count.groupby(by = "mois")["counts"].mean()
df_annee = df_count.groupby(by = "annee")["counts"].mean()
df_place = df_count.groupby(by = "name")["counts"].sum()

# Conversion des coordonnées
boulevards = df_count[['geo', 'name']].drop_duplicates()
boulevards[['coordy', 'coordx']] = boulevards['geo'].str.split(', ', expand=True).astype(float)
boulevards['coordx'] = boulevards['coordx'].apply(lambda v: coor_wgs84_to_web_mercator(v, 'lon'))
boulevards['coordy'] = boulevards['coordy'].apply(lambda v: coor_wgs84_to_web_mercator(v, 'lat'))
boulevards["count"] = df_place.values
boulevards["count_size"] = df_place.values /80000
##############################################################################


#### Affichage

####################################### Fréquentation #######################################

## Histogrammes des moyennes des fréquentations par heure de la journée, par mois et par an
heures_journee = [f"{h:02d}:00" for h in range(25)]
f1 = figure(title="Moyennes des fréquentations par heure", 
            x_axis_label= "Heure", y_axis_label="Moyenne des fréquentations", x_range=heures_journee)
f1.xaxis.major_label_orientation = "vertical"

l_mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
f2 = figure(title="Moyennes des fréquentations par mois",
            x_axis_label= "Mois", y_axis_label="Moyenne des fréquentations",
            x_range=l_mois)
f2.xaxis.major_label_orientation = "vertical"

f3 = figure(title="Moyennes des fréquentations par an",
            x_axis_label= "Année", y_axis_label="Moyenne des fréquentations")
f3.xaxis.major_label_orientation = "vertical"

f1.quad(left=df_heure.index +0.5, right=df_heure.index +1.5, top=df_heure, bottom=0, fill_color='navy', line_color='white', alpha=0.8)
f2.quad(left=df_mois.index -1, right=df_mois.index, top=df_mois, bottom=0, fill_color='navy', line_color='white', alpha=0.8)
f3.quad(left=df_annee.index, right=df_annee.index +1, top=df_annee, bottom=0, fill_color='navy', line_color='white', alpha=0.8)

tab_hist1 = TabPanel(child=f1, title="Par heure")
tab_hist2 = TabPanel(child=f2, title="Par mois")
tab_hist3 = TabPanel(child=f3, title="Par an")
tabs_hist = Tabs(tabs = [tab_hist1, tab_hist2, tab_hist3])

## Carte des capteurs sur les boulevards étudiés
carte_bd = figure(x_axis_type='mercator', 
            y_axis_type="mercator",
            title= "Fréquentation des boulevards",
            height=600, width=800)
carte_bd.add_tile('CartoDb Positron')

# Calculate the bounding box with some padding for a zoomed-out view
min_x = boulevards['coordx'].min()
max_x = boulevards['coordx'].max()
min_y = boulevards['coordy'].min()
max_y = boulevards['coordy'].max()

# Add 30% padding to make the map more zoomed out
padding_x = (max_x - min_x) * 0.3
padding_y = (max_y - min_y) * 0.3

carte_bd.x_range.start = min_x - padding_x
carte_bd.x_range.end = max_x + padding_x
carte_bd.y_range.start = min_y - padding_y
carte_bd.y_range.end = max_y + padding_y

carte_bd.scatter(x='coordx', y='coordy', source=ColumnDataSource(boulevards), size='count_size', color=factor_cmap('name', palette=Set1[3], factors=boulevards['name']), legend_group='name')
carte_bd.legend.title = 'Points de comptage'
carte_bd.legend.location = 'top_left'
carte_bd.add_tools(HoverTool(tooltips=[('Nom', '@name'), ('Comptage', '@count')]))



####################################### Carte reseau Star #######################################

## Carte du resau Star
source_arret = ColumnDataSource(df_arrets)

carte_reseau = figure(x_axis_type='mercator', 
            y_axis_type="mercator",
            title= "Réseau de lignes STAR",
            height=700, width=900)
carte_reseau.add_tile('CartoDb Positron')

# Ajout des lignes
types = df_itineraires['li_type'].unique()
for t in types:
    df = df_itineraires[df_itineraires['li_type'] == t]
    source_itineraires = ColumnDataSource(df)
    carte_reseau.multi_line(xs='xs',ys='ys', source=source_itineraires, line_width=2, color='li_couleur_hex', legend_label=t)

# Ajout des arrêts
carte_reseau.scatter(x='coordx', y='coordy', size=2, source=source_arret, color='black')

# Ajout d'un outil de survol pour afficher les informations sur les lignes
hover_tool = HoverTool(tooltips=[
    ('Ligne','@li_num - @iti_nom'),
    ("Type", "@li_type")])
carte_reseau.add_tools(hover_tool)
carte_reseau.legend.click_policy="hide"


## Histogramme du nombre de lignes par type
barplot_type = figure(title="Nombre de lignes par type", x_range=types, height=300, width=500)
types_count = df_itineraires.value_counts('li_type').reset_index(name='li_num')
barplot_type.vbar(x='li_type', top='li_num', source=ColumnDataSource(types_count), width=0.5, color='black', fill_color=factor_cmap('li_type', palette=Set1[7], factors=types))
barplot_type.xaxis.major_label_orientation = np.pi/6


## Histogramme du nombre de lignes par commune
communes = df_arrets['Commune_nom'].dropna().unique()
barplot_comm = figure(title="Nombre d'arrêts par commune", x_range=communes, height=400, width=500)
comm_count = df_arrets.value_counts('Commune_nom').reset_index(name='arret_num').sort_values('arret_num', ascending=False)
barplot_comm.vbar(x='Commune_nom', top='arret_num', source=ColumnDataSource(comm_count), width=0.8, fill_color='black')
barplot_comm.xaxis.major_label_orientation = 'vertical'

hover_tool_comm = HoverTool(tooltips=[('Commune', '@Commune_nom'),
                                      ("Nombere d'arrêts", '@arret_num')])
barplot_comm.add_tools(hover_tool_comm)



####################################### Mise en forme finale #######################################

## Création d'un widget Div pour le titre et le texte de l'en-tête
header = Div(text="""
    <h1>Se déplacer à Rennes</h1>
    <p>Cette page a pour but de représenter des données en rapport avec la circulation verte à Rennes :</p>
    <ul>
        <li>Le premier onglet comprend une cartographie du réseau de transport de la métropole et des statistiques sur les arrêts et ilgnes. Pour bien les visualiser, nous avons representé le réseau de lignes STAR (métro et bus) sur une carte interactive, où les lignes sont divisés en différentes catégories.</li>
        <li>Le deuxième onglet comprend les déplacements à vélo et à pied, pour les représenter nous avons le nombre de vélos/piétons captés à chaque heure par 3 bornes placés proche du centre ville depuis 2014. Avec
        ces données nous avons pu tracer les histogrammes de la fréquentation moyenne en fonction du mois, de l'année ou de l'heure. Ainsi qu'une carte indiquant l'emplacement des capteurs.</li>
    </ul>
""", height=170)

## Création d'un layout pour organiser les graphiques côte à côte
freq_pan = row(tabs_hist, carte_bd)
reseau_pan = row(carte_reseau, column(barplot_comm, barplot_type))


tabs = Tabs(tabs=[
    TabPanel(child=reseau_pan, title="Réseau STAR"),
    TabPanel(child=freq_pan, title="Fréquentation verte de grands boulevards")
])
page = column(header, tabs)

show(page)

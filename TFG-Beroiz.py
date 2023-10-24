import requests
import json
import pandas
import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pyproj
import warnings
warnings.filterwarnings("ignore")

fixed = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
url = '{}{}'.format(fixed,'sdg_05_60')
metadata = requests.get(url).json()
print(metadata['label'])
data = pandas.Series(metadata['value']).rename(index=int).sort_index()
n = 1 # Initialize the result to 1
for num in metadata['size']:
  n *= num
data = data.reindex(range(0,n),fill_value=0)
structure = [pandas.DataFrame({key:val for key,val in metadata['dimension'][dim]['category'].items()}).sort_values('index')['label'].values for dim in metadata['id']]
data.index = pandas.MultiIndex.from_product(structure,names=metadata['id'])
mydata = data.reset_index()
mydata = mydata[mydata['prof_pos']=='Executives']
mydata = mydata[['geo','time',0]]
mydata.rename(columns={0:'percentage'},inplace=True)
mydata.rename(columns={'geo':'ADMIN'},inplace=True)

mydata1 = mydata[mydata.time=='2022']
table = mydata.pivot(index='ADMIN',columns='time',values=['percentage']).reset_index()
table.columns = table.columns.droplevel(level=0)
table.rename(columns={'ADMIN':'GEO'},inplace=True)
table = table.rename_axis(columns=None)

world = geopandas.read_file('/content/TFG-Beroiz/ne_110m_admin_0_countries.zip')[['ADMIN','geometry']]
polygon = Polygon([(-25,35),(40,35),(40,75),(-25,75)])
europe = geopandas.clip(world,polygon)

mydata1 = mydata1.merge(europe,on='ADMIN',how='right')
mydata = geopandas.GeoDataFrame(mydata,geometry='geometry')
fig,ax = plt.subplots(1,figsize=(10,10))
mydata.plot(column='percentage',alpha=0.8,cmap='viridis',ax=ax,legend=True)
ax.set_title('Porcentage de mujeres en puestos de dirección en 2022 (source: Eurostat)')
ax.axis('off')

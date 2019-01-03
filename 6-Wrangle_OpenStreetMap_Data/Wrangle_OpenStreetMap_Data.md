
# Project: **Wrangle OpenStreetMap Data**


### 1. Map Area

* [Campina Grande, PB, Brazil](https://en.wikipedia.org/wiki/Campina_Grande)

This is the region where my parents live. The geometry start in Campina Grande going until the sea. I’m very interested to see what database querying reveals. I also wish to contribute to improve OpenStreetMap.org making this data chunck more useful for everyone.

### 2. Getting Data

To get the data used in this task:

1. OpenStreetMap: https://www.openstreetmap.org/relation/301079

2. Overpass API: http://overpass-api.de/query_form.html
    
3. Query Form: *(Using the same values given on the EXPORT page in OpenStreetMap)*

    ```ruby
    (
     node(-7.4775,-36.2357,-7.0641,-7.0641);
    <;
    );out meta;

    ```
    
4. Transform [OSM](https://github.com/zegildo/codereviewer/tree/master/6-Wrangle_OpenStreetMap_Data/osm) in [CSV](https://github.com/zegildo/codereviewer/tree/master/6-Wrangle_OpenStreetMap_Data/csvs) files using [script python](https://github.com/zegildo/codereviewer/tree/master/6-Wrangle_OpenStreetMap_Data/py)
5. Insert csv files in a relational database


### 3. Inserting Data on Relational Database

1. [Creating *nodes* and *ways* schema](https://github.com/zegildo/codereviewer/tree/master/6-Wrangle_OpenStreetMap_Data/sql)


```sql
create table nodes(
	id bigserial,
	lat numeric,
	lon numeric,
	user_name varchar(200),
	uid integer,
	version integer,
	changeset integer,
	timestamp timestamp,

	primary key(id)
);

create table nodes_tags(
	id bigserial,
	key varchar(200),
	type varchar(200),
	value varchar(200)
);

create table ways(
	id bigserial,
	user_name varchar(200),
	uid integer, 
	version integer,
	changeset integer, 
	timestamp timestamp
);

create table ways_tags(
	id bigserial, 
	key varchar(200),
	value varchar(2000), 
	type varchar(200)
);

create table ways_nodes(
	id bigserial,
	node_id bigserial, 
	position integer
);
```

2. Insert values:

```sql
COPY nodes(id,lat,lon,user_name,uid,version,changeset,timestamp) 
FROM '../csvs/nodes.csv' DELIMITER ',' CSV HEADER;

COPY nodes_tags(key,type,id,value) 
FROM '../csvs/nodes_tags.csv' DELIMITER ',' CSV HEADER;

COPY ways(id,user_name,uid,version,changeset,timestamp) 
FROM '../csvs/ways.csv' DELIMITER ',' CSV HEADER;

COPY ways_nodes(id,node_id,position) 
FROM '../csvs/ways_nodes.csv' DELIMITER ',' CSV HEADER;

COPY ways_tags(id,key,value,type) 
FROM '../csvs/ways_tags.csv' DELIMITER ',' CSV HEADER;
```

#### 3.1. Connecting with the database


```python
%matplotlib inline 
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:capacida@localhost:5432/stocks')
```

### 4. Problems Encountered in the Map
We are list some problems found in the map structure

### 4.1 Incorrect Registration

#### 4.1 {NODES,WAYS}\_TAGS with rare KEY registred

**SQL:**

```sql
SELECT key, count(*) 
       FROM (SELECT * FROM nodes_tags
               UNION ALL 
             SELECT * FROM ways_tags) tags GROUP BY key 
       HAVING count(*) <= 1 ORDER BY count DESC
```

**Python:**


```python
SQL = "SELECT key, count(*) "+\
      "FROM (SELECT * FROM nodes_tags "+\
               "UNION ALL "+\
             "SELECT * FROM ways_tags) tags GROUP BY key "+\
    "HAVING count(*) <= 15 ORDER BY count DESC"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["key", "count"])
keys = u', '.join(df.key.values).encode('utf-8').strip()
keys
```




    'delivery, conditional, dispensing, ele, country, right, direction, cycleway, state, left, AtcoCode, government, wall, supervised, postal_code, old_name, 4wd_only, width, converted_by, outdoor_seating, state_code, country_code, icao, forward, embankment, continent, email, pipeline, min_age, police, stars, male, drive_through, unit, bench, start_date, sound, industrial, motorcycle, button_operated, motorcar, FIXME, loc_name, noname, female, room, url, output:electricity, indoor, origin, point, building_1, created_by, bitcoin, wifi, maxweight, speciality, airmark, brand, manually, flag, border_type, ru, code, kk, water_level, building; recuos, covered, cable_submarine:name, position, length, ka, recycling_type, bg, is_in, iata, name_alt, phone_1, vegetarian, backward, diesel, int_name, local_ref, craft, ja, light:character, reef, light:colour, crop, landmark:category, eo, service_times, light:period, zh, landmark:function, license_classes, cutting, ko, vegan, protect_class, short_name, disposal, vehicle:car_repair, traffic_sign, disabled, lt, trees, produce, cash, light:height, admin_level, light:range, min_level, crossing_ref, sr, wpt_description, route, park_ride, civilization, memorial, wpt_symbol, biodiesel, castle_type, dish_washing, vehicle:electrical, debit_cards, vehicle:new_car_sales, Quadra, smoothness, light:reference, automated, tomb, ar, boat, picnic_benches, ruins, sanitary_dumpstation, Bearing, sh, mk, general_room, microbrewery, organic, site_type, octane_92, dinheiro, vehicle:oil_change, Qualquer_tampa_de_pl\xc3\xa1stico, be, platforms, power_supply, tg, lines, descri, bicycle_parking, shower, military, segregated, big_rigs, protection_title, inscription, cadeirante, laundry, nudism, attraction, collection_times, Dinheiro, bar, artwork_type, ssid, CNUC, fireplace, he, internet, site, dryer, drinking_water, tents, state_capital, content, e85, credit_card, Garrafas_de_iogurte, denomination_1, hy, toll, os, wreck:category, washing_machine, vehicle, uz, color, wiki, second_hand, luggage, bicycle_road, vehicle:motorbike, kitchen, camp_type, caravans, social_facility, restaurant, fa, posto de sa\xc3\xbade, pl, ethanol, uk, gasoline, cs, fence_type, lv, scale:imba, traffic, right:conditional, pets, de, mr, tank:category, diaper, related_law, vehicle:used_car_sales, swimming_pool, stroller, handrail, maritime, ramp, quality, comment, credit_cards'



It's probably that rare names used in 'keys' be better grouped in other 'keys'. Some of these 'keys' names means nothing and they was filled due an understanding error of openstreetmap structure.

Examples:
* fixme should be FIXME(patter);
* old_name, he, is_in, man_made, mr, ele, ruins, int_name, collection_times, be, comment: are apparently fill mistakes;
* historic, direction, continent, healthcare, motocar, motocycle: should be reclassify as name, type, source or other representative **key**.

#### 4.1  {NODES,WAYS}\_TAGS with good KEYS and  bad VALUES registred

For the major KEYS classes present in data, we checked the quality and sense of names used in VALUE attribute

**SQL:**

```sql
SELECT key, count(*) 
       FROM (SELECT * FROM nodes_tags
               UNION ALL 
             SELECT * FROM ways_tags) tags GROUP BY key  
       HAVING count(*) > 1000 ORDER BY count DESC
```

**Python:**


```python
SQL = "SELECT key, count(*) "+\
       "FROM (SELECT * FROM nodes_tags "+\
               "UNION ALL "+\
             "SELECT * FROM ways_tags) tags GROUP BY key "+\
    "HAVING count(*) > 1000 ORDER BY count DESC"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["key", "count"])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>key</th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>highway</td>
      <td>32283</td>
    </tr>
    <tr>
      <th>1</th>
      <td>source</td>
      <td>17346</td>
    </tr>
    <tr>
      <th>2</th>
      <td>name</td>
      <td>16794</td>
    </tr>
    <tr>
      <th>3</th>
      <td>building</td>
      <td>10276</td>
    </tr>
    <tr>
      <th>4</th>
      <td>power</td>
      <td>6297</td>
    </tr>
    <tr>
      <th>5</th>
      <td>oneway</td>
      <td>6133</td>
    </tr>
    <tr>
      <th>6</th>
      <td>surface</td>
      <td>5442</td>
    </tr>
    <tr>
      <th>7</th>
      <td>lit</td>
      <td>3629</td>
    </tr>
    <tr>
      <th>8</th>
      <td>maxspeed</td>
      <td>2526</td>
    </tr>
    <tr>
      <th>9</th>
      <td>lanes</td>
      <td>2182</td>
    </tr>
    <tr>
      <th>10</th>
      <td>natural</td>
      <td>2057</td>
    </tr>
    <tr>
      <th>11</th>
      <td>amenity</td>
      <td>1657</td>
    </tr>
    <tr>
      <th>12</th>
      <td>levels</td>
      <td>1656</td>
    </tr>
    <tr>
      <th>13</th>
      <td>ref</td>
      <td>1282</td>
    </tr>
    <tr>
      <th>14</th>
      <td>street</td>
      <td>1085</td>
    </tr>
  </tbody>
</table>
</div>



**SQL:**

```sql
SELECT key, value, count(*)
       FROM (SELECT * FROM nodes_tags
               UNION ALL
             SELECT * FROM ways_tags) tags GROUP BY key, value
HAVING key='source' ORDER BY count DESC
```

**Python:**


```python
SQL = "SELECT key, value, count(*) "+\
       "FROM (SELECT * FROM nodes_tags "+\
               "UNION ALL "+\
             "SELECT * FROM ways_tags) tags GROUP BY key, value "+\
    "HAVING key='source' ORDER BY count DESC"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["key", "value", "count"])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>key</th>
      <th>value</th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>source</td>
      <td>regular</td>
      <td>14159</td>
    </tr>
    <tr>
      <th>1</th>
      <td>source</td>
      <td>SEMOB</td>
      <td>1780</td>
    </tr>
    <tr>
      <th>2</th>
      <td>source</td>
      <td>IBGE</td>
      <td>908</td>
    </tr>
    <tr>
      <th>3</th>
      <td>source</td>
      <td>Bing</td>
      <td>128</td>
    </tr>
    <tr>
      <th>4</th>
      <td>source</td>
      <td>DigitalGlobe</td>
      <td>116</td>
    </tr>
    <tr>
      <th>5</th>
      <td>source</td>
      <td>Pref. Santa Rita</td>
      <td>55</td>
    </tr>
    <tr>
      <th>6</th>
      <td>source</td>
      <td>Bing; DigitalGlobe</td>
      <td>43</td>
    </tr>
    <tr>
      <th>7</th>
      <td>source</td>
      <td>wind</td>
      <td>38</td>
    </tr>
    <tr>
      <th>8</th>
      <td>source</td>
      <td>Yahoo Imagery</td>
      <td>29</td>
    </tr>
    <tr>
      <th>9</th>
      <td>source</td>
      <td>Pref. Conde</td>
      <td>27</td>
    </tr>
    <tr>
      <th>10</th>
      <td>source</td>
      <td>survey</td>
      <td>25</td>
    </tr>
    <tr>
      <th>11</th>
      <td>source</td>
      <td>Pref. João Pessoa</td>
      <td>13</td>
    </tr>
    <tr>
      <th>12</th>
      <td>source</td>
      <td>local_knowledge</td>
      <td>4</td>
    </tr>
    <tr>
      <th>13</th>
      <td>source</td>
      <td>oil</td>
      <td>4</td>
    </tr>
    <tr>
      <th>14</th>
      <td>source</td>
      <td>bing</td>
      <td>4</td>
    </tr>
    <tr>
      <th>15</th>
      <td>source</td>
      <td>Known place</td>
      <td>3</td>
    </tr>
    <tr>
      <th>16</th>
      <td>source</td>
      <td>GPS</td>
      <td>2</td>
    </tr>
    <tr>
      <th>17</th>
      <td>source</td>
      <td>survey; Bing</td>
      <td>2</td>
    </tr>
    <tr>
      <th>18</th>
      <td>source</td>
      <td>Survey</td>
      <td>1</td>
    </tr>
    <tr>
      <th>19</th>
      <td>source</td>
      <td>Local knowledge</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20</th>
      <td>source</td>
      <td>generator</td>
      <td>1</td>
    </tr>
    <tr>
      <th>21</th>
      <td>source</td>
      <td>DigitalGlobe; survey</td>
      <td>1</td>
    </tr>
    <tr>
      <th>22</th>
      <td>source</td>
      <td>Bing;survey</td>
      <td>1</td>
    </tr>
    <tr>
      <th>23</th>
      <td>source</td>
      <td>known place</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



Many **values** are repeated or rare: ** known place, Local knowledge, generator, Bing, bing, wind, local_knowledge, oil, GPS, Survey, DigitalGlobe;survey, Bing;DigitalGlobe** and this affects the data quality generate unreliable reports. The suggestion is reclassify these **values** using more representative **values** like **regular** or **IBGE**.


```python
SQL = "SELECT value, count(*) "+\
        "FROM nodes_tags "+\
        "WHERE key ='name' GROUP BY value ORDER BY count DESC"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["values", "count"])
df.head(10)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>values</th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>P</td>
      <td>198</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Subway</td>
      <td>10</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Banco do Brasil</td>
      <td>10</td>
    </tr>
    <tr>
      <th>3</th>
      <td>603</td>
      <td>8</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Centro</td>
      <td>7</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Pague Menos</td>
      <td>6</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Santander</td>
      <td>6</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Encanto Verde</td>
      <td>5</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Armazém Paraíba</td>
      <td>5</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Correios</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



The same problem happens with **KEY = 'name'**. In this case we have 198 nodes_tags when the **VALUE = 'P'** and **'P'** a **tag** with no meaning.

#### 4.2 Overabbreviated Street Names


**SQL:**

```sql
SELECT key, value
       FROM (SELECT * FROM nodes_tags
               UNION ALL 
             SELECT * FROM ways_tags) tags
where key='street' and value like '%.%';
```

**Python:**


```python
SQL = "SELECT key, value "+\
       "FROM (SELECT * FROM nodes_tags "+\
               "UNION ALL "+\
             "SELECT * FROM ways_tags) tags "+\
"WHERE key='street'"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["key", "value"])

df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>key</th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>street</td>
      <td>Avenida Joao Maurício</td>
    </tr>
    <tr>
      <th>1</th>
      <td>street</td>
      <td>Avenida Presidente Epitácio Pessoa</td>
    </tr>
    <tr>
      <th>2</th>
      <td>street</td>
      <td>Rua João da Luz</td>
    </tr>
    <tr>
      <th>3</th>
      <td>street</td>
      <td>Final da Av. Beira Rio, nº71</td>
    </tr>
    <tr>
      <th>4</th>
      <td>street</td>
      <td>Avenida Monsenhor Walfredo Leal</td>
    </tr>
  </tbody>
</table>
</div>



**Fixing Abbreviation problem:**


```python
PORTUGUESE_ABBRV = {'R.':'Rua', 'Av.':'Avenida', 'B.':'Bairro'}

for value in values:
    for k,v in PORTUGUESE_ABBRV.items():
        new_address = value.replace(k,v)
        print new_address
```

    Avenida Joao Maurício
    Avenida Joao Maurício
    Avenida Joao Maurício
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Rua João da Luz
    Rua João da Luz
    Rua João da Luz
    Final da Av. Beira Rio, nº71
    Final da Av. Beira Rio, nº71
    Final da Avenida Beira Rio, nº71
    Avenida Monsenhor Walfredo Leal
    Avenida Monsenhor Walfredo Leal
    Avenida Monsenhor Walfredo Leal
    Avenida Assis Chateaubriand
    Avenida Assis Chateaubriand
    Avenida Assis Chateaubriand
    Rua Ozório Milanez Filho
    Rua Ozório Milanez Filho
    Rua Ozório Milanez Filho
    Loteamento Cidade Balneário Novo Mundo
    Loteamento Cidade Balneário Novo Mundo
    Loteamento Cidade Balneário Novo Mundo
    Avenida Olinda
    Avenida Olinda
    Avenida Olinda
    Rua Virgolino de Souza Campos
    Rua Virgolino de Souza Campos
    Rua Virgolino de Souza Campos
    Rua Duque de Caxias
    Rua Duque de Caxias
    Rua Duque de Caxias
    Rua Barão do Abiaí
    Rua Barão do Abiaí
    Rua Barão do Abiaí
    BR-230
    BR-230
    BR-230
    BR-101
    BR-101
    BR-101
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    Rua Argemiro de Figueiredo
    Rua Argemiro de Figueiredo
    Rua Argemiro de Figueiredo
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Rua Severino Nicolau de Melo
    Rua Severino Nicolau de Melo
    Rua Severino Nicolau de Melo
    Avenida Artur Monteiro Paiva
    Avenida Artur Monteiro Paiva
    Avenida Artur Monteiro Paiva
    Rodovia Transamazônica
    Rodovia Transamazônica
    Rodovia Transamazônica
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Rua José Aires do Nascimento
    Rua José Aires do Nascimento
    Rua José Aires do Nascimento
    Avenida Dom Pedro II
    Avenida Dom Pedro II
    Avenida Dom Pedro II
    Rua Claudino Pereira
    Rua Claudino Pereira
    Rua Claudino Pereira
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Rua Luiz Alves Conserva
    Rua Luiz Alves Conserva
    Rua Luiz Alves Conserva
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Professor Francisco Lucas de Souza Rangel
    Rua Francisco Farias Braga
    Rua Francisco Farias Braga
    Rua Francisco Farias Braga
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Francisco de Londres Trindade
    Rua Francisco de Londres Trindade
    Rua Francisco de Londres Trindade
    Rua José Alves de Araújo
    Rua José Alves de Araújo
    Rua José Alves de Araújo
    Rua Davi A Câmara
    Rua Davi A Câmara
    Rua Davi A Câmara
    Travessa Marinez
    Travessa Marinez
    Travessa Marinez
    Avenida São Paulo
    Avenida São Paulo
    Avenida São Paulo
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Rua Domingos Trigueiro Castelo Branco
    Rua Domingos Trigueiro Castelo Branco
    Rua Domingos Trigueiro Castelo Branco
    Rua Francisco Alves Barbosa
    Rua Francisco Alves Barbosa
    Rua Francisco Alves Barbosa
    BR-230
    BR-230
    BR-230
    Rua Trinta de Dezembro
    Rua Trinta de Dezembro
    Rua Trinta de Dezembro
    Rua Fernando Pessoa
    Rua Fernando Pessoa
    Rua Fernando Pessoa
    Avenida Presidente joão Pessoa
    Avenida Presidente joão Pessoa
    Avenida Presidente joão Pessoa
    Rua Cônego Tranquilino
    Rua Cônego Tranquilino
    Rua Cônego Tranquilino
    Praça Epitácio Pessoa
    Praça Epitácio Pessoa
    Praça Epitácio Pessoa
    Rua Marieta Medeiros
    Rua Marieta Medeiros
    Rua Marieta Medeiros
    Rua Deputado Adauto de Lima
    Rua Deputado Adauto de Lima
    Rua Deputado Adauto de Lima
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    PB-054
    PB-054
    PB-054
    PB-054
    PB-054
    PB-054
    Rua Napoleão Laureano
    Rua Napoleão Laureano
    Rua Napoleão Laureano
    Rua Almeida Barreto
    Rua Almeida Barreto
    Rua Almeida Barreto
    PB-054
    PB-054
    PB-054
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    PB-054
    PB-054
    PB-054
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    Avenida Prefeito Antônio Batista Santiago
    Praça Manoel Joaquim araújo
    Praça Manoel Joaquim araújo
    Praça Manoel Joaquim araújo
    Rua Francisco Gomes Costa
    Rua Francisco Gomes Costa
    Rua Francisco Gomes Costa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    PB-054
    PB-054
    PB-054
    PB-054
    PB-054
    PB-054
    Rua Deputado Adauto de Lima
    Rua Deputado Adauto de Lima
    Rua Deputado Adauto de Lima
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida José Silveira
    Avenida José Silveira
    Avenida José Silveira
    Rua Cônego Tranquilino
    Rua Cônego Tranquilino
    Rua Cônego Tranquilino
    Rua Napoleão Laurenao
    Rua Napoleão Laurenao
    Rua Napoleão Laurenao
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    Rua José Silveira
    Rua José Silveira
    Rua José Silveira
    Rua Getúlio Vargas
    Rua Getúlio Vargas
    Rua Getúlio Vargas
    Rua das Caravelas
    Rua das Caravelas
    Rua das Caravelas
    Avenida Beira Mar
    Avenida Beira Mar
    Avenida Beira Mar
    Avenida Diógenes Chianca
    Avenida Diógenes Chianca
    Avenida Diógenes Chianca
    Avenida João Machado
    Avenida João Machado
    Avenida João Machado
    Rua Senhor dos Passos
    Rua Senhor dos Passos
    Rua Senhor dos Passos
    Avenida Barão do Triunfo
    Avenida Barão do Triunfo
    Avenida Barão do Triunfo
    Praça Dom Ulrico
    Praça Dom Ulrico
    Praça Dom Ulrico
    Avenida General Osório
    Avenida General Osório
    Avenida General Osório
    Rua Professor Batista Leite
    Rua Professor Batista Leite
    Rua Professor Batista Leite
    Avenida Cecília Miranda
    Avenida Cecília Miranda
    Avenida Cecília Miranda
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    BR-104 - Queimadas
    BR-104 - Queimadas
    BR-104 - Queimadas
    Rua Rosário di Lorenzo
    Rua Rosário di Lorenzo
    Rua Rosário di Lorenzo
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida São Paulo
    Avenida São Paulo
    Avenida São Paulo
    Rua Doutor Severino Cruz
    Rua Doutor Severino Cruz
    Rua Doutor Severino Cruz
    Rua Gutemberg Morais Paiva
    Rua Gutemberg Morais Paiva
    Rua Gutemberg Morais Paiva
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Rua João Bernardo de Albuquerque
    Rua João Bernardo de Albuquerque
    Rua João Bernardo de Albuquerque
    Avenida Duarte da Silveira
    Avenida Duarte da Silveira
    Avenida Duarte da Silveira
    Avenida General Bento da Gama
    Avenida General Bento da Gama
    Avenida General Bento da Gama
    Rua Rodrigues de Aquino
    Rua Rodrigues de Aquino
    Rua Rodrigues de Aquino
    Praça João Pessoa
    Praça João Pessoa
    Praça João Pessoa
    Rua Marechal Almeida Barreto
    Rua Marechal Almeida Barreto
    Rua Marechal Almeida Barreto
    Rua Agente Fiscal José da Costa Duarte
    Rua Agente Fiscal José da Costa Duarte
    Rua Agente Fiscal José da Costa Duarte
    Avenida Visconde de Pelotas
    Avenida Visconde de Pelotas
    Avenida Visconde de Pelotas
    Avenida Visconde de Pelotas
    Avenida Visconde de Pelotas
    Avenida Visconde de Pelotas
    Avenida Almirante Tamandaré
    Avenida Almirante Tamandaré
    Avenida Almirante Tamandaré
    Avenida Ministro José Américo de Almeida
    Avenida Ministro José Américo de Almeida
    Avenida Ministro José Américo de Almeida
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Parque Solon de Lucena
    Parque Solon de Lucena
    Parque Solon de Lucena
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Janúncio Ferreira
    Avenida Janúncio Ferreira
    Avenida Janúncio Ferreira
    Rua Euclides Bacalhau
    Rua Euclides Bacalhau
    Rua Euclides Bacalhau
    Avenida Rui Barbosa
    Avenida Rui Barbosa
    Avenida Rui Barbosa
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Rua Monsenhor Sales
    Rua Monsenhor Sales
    Rua Monsenhor Sales
    Rua José Adnoeste Roberto
    Rua José Adnoeste Roberto
    Rua José Adnoeste Roberto
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    Avenida Cabo Branco
    Avenida Cabo Branco
    Avenida Cabo Branco
    Rua Antônio Teotônio
    Rua Antônio Teotônio
    Rua Antônio Teotônio
    Avenida 1º de Maio
    Avenida 1º de Maio
    Avenida 1º de Maio
    PB-066
    PB-066
    PB-066
    Rua Coronel Augusto Fernandes Maia
    Rua Coronel Augusto Fernandes Maia
    Rua Coronel Augusto Fernandes Maia
    Rua Juiz Ovídio Gouveia
    Rua Juiz Ovídio Gouveia
    Rua Juiz Ovídio Gouveia
    Rua Tenente Francisco de Assis Moreira
    Rua Tenente Francisco de Assis Moreira
    Rua Tenente Francisco de Assis Moreira
    Avenida Silvino Lopes
    Avenida Silvino Lopes
    Avenida Silvino Lopes
    Avenida Silvino Lopes
    Avenida Silvino Lopes
    Avenida Silvino Lopes
    Avenida Nego
    Avenida Nego
    Avenida Nego
    Avenida Bacharel José de Oliveira Curchatuz
    Avenida Bacharel José de Oliveira Curchatuz
    Avenida Bacharel José de Oliveira Curchatuz
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    Rua Francisco Claudino Pereira
    Avenida João Câncio da Silva
    Avenida João Câncio da Silva
    Avenida João Câncio da Silva
    Avenida Euzely Fabrício de Souza
    Avenida Euzely Fabrício de Souza
    Avenida Euzely Fabrício de Souza
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Rua Maceió
    Rua Maceió
    Rua Maceió
    Avenida Prefeito Severino Cabral
    Avenida Prefeito Severino Cabral
    Avenida Prefeito Severino Cabral
    Rua Engenheiro José Bezerra
    Rua Engenheiro José Bezerra
    Rua Engenheiro José Bezerra
    Avenida Prefeito Severino Cabral
    Avenida Prefeito Severino Cabral
    Avenida Prefeito Severino Cabral
    Rua Benjamim Constant
    Rua Benjamim Constant
    Rua Benjamim Constant
    Rua Luiza Bezerra Motta
    Rua Luiza Bezerra Motta
    Rua Luiza Bezerra Motta
    Rua Vigário Calixto
    Rua Vigário Calixto
    Rua Vigário Calixto
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Dom Pedro II
    Avenida Dom Pedro II
    Avenida Dom Pedro II
    Avenida Piauí
    Avenida Piauí
    Avenida Piauí
    Rua Wandick Pinto Filgueiras
    Rua Wandick Pinto Filgueiras
    Rua Wandick Pinto Filgueiras
    Rua Padre José Alves
    Rua Padre José Alves
    Rua Padre José Alves
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Avenida Abdias Gomes de Almeida
    Rua Deputado Geraldo Mariz
    Rua Deputado Geraldo Mariz
    Rua Deputado Geraldo Mariz
    Rua Deputado Geraldo Mariz
    Rua Deputado Geraldo Mariz
    Rua Deputado Geraldo Mariz
    Avenida João Câncio da Silva
    Avenida João Câncio da Silva
    Avenida João Câncio da Silva
    BR-101
    BR-101
    BR-101
    Rua Valdecir Torres
    Rua Valdecir Torres
    Rua Valdecir Torres
    Rua Severino Massa Spinelli
    Rua Severino Massa Spinelli
    Rua Severino Massa Spinelli
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Senador Ruy Carneiro
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Avenida Monteiro Lobato
    Rua Newton Timóteo de Souza
    Rua Newton Timóteo de Souza
    Rua Newton Timóteo de Souza
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Rua Engenheiro José Bezerra
    Rua Engenheiro José Bezerra
    Rua Engenheiro José Bezerra
    Rua Júlia Freire
    Rua Júlia Freire
    Rua Júlia Freire
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    Rodovia Governador Antônio Mariz
    RUA FLORESTAL
    RUA FLORESTAL
    RUA FLORESTAL
    Rua Clotilde Alves Rocha
    Rua Clotilde Alves Rocha
    Rua Clotilde Alves Rocha
    Rua Virgolino de Souza Campos
    Rua Virgolino de Souza Campos
    Rua Virgolino de Souza Campos
    Rua Coronel Eduardo Costa
    Rua Coronel Eduardo Costa
    Rua Coronel Eduardo Costa
    Rua Adauto Toledo
    Rua Adauto Toledo
    Rua Adauto Toledo
    Rua Deputado Petrônio Figueiredo
    Rua Deputado Petrônio Figueiredo
    Rua Deputado Petrônio Figueiredo
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida Prefeito Osvaldo Pessoa
    Avenida 1º de Maio
    Avenida 1º de Maio
    Avenida 1º de Maio
    Praça Abnom Milenês
    Praça Abnom Milenês
    Praça Abnom Milenês
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Avenida Benício de Oliveira Lima
    Avenida Benício de Oliveira Lima
    Avenida Benício de Oliveira Lima
    Av. João Maurício
    Av. João Maurício
    Avenida João Maurício
    Rua Senador Leal
    Rua Senador Leal
    Rua Senador Leal
    Rua Frutuoso Barbosa
    Rua Frutuoso Barbosa
    Rua Frutuoso Barbosa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida São Paulo
    Avenida São Paulo
    Avenida São Paulo
    Rua Rita Carneiro Diniz
    Rua Rita Carneiro Diniz
    Rua Rita Carneiro Diniz
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Ludolvico de Melo Azedo
    Rua Márcia Carneiro Morais de Oliveira
    Rua Márcia Carneiro Morais de Oliveira
    Rua Márcia Carneiro Morais de Oliveira
    Rua Santos Coelho
    Rua Santos Coelho
    Rua Santos Coelho
    Avenida Manoel Tavares
    Avenida Manoel Tavares
    Avenida Manoel Tavares
    Rua Estelita Cruz
    Rua Estelita Cruz
    Rua Estelita Cruz
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Rua Vigário Virgino
    Rua Vigário Virgino
    Rua Vigário Virgino
    Rua Otacílio Nepomuceno
    Rua Otacílio Nepomuceno
    Rua Otacílio Nepomuceno
    Rua Pintor Santa Rosa
    Rua Pintor Santa Rosa
    Rua Pintor Santa Rosa
    Rua Joana de Barros Moreira Machado
    Rua Joana de Barros Moreira Machado
    Rua Joana de Barros Moreira Machado
    Rua Tertuliano Castro
    Rua Tertuliano Castro
    Rua Tertuliano Castro
    Rua Doutor Damasquins Ramos Maciel
    Rua Doutor Damasquins Ramos Maciel
    Rua Doutor Damasquins Ramos Maciel
    Rua Empresário João Rodrigues Alves
    Rua Empresário João Rodrigues Alves
    Rua Empresário João Rodrigues Alves
    Isidro Gomes 257
    Isidro Gomes 257
    Isidro Gomes 257
    Rua Vicente Cozza
    Rua Vicente Cozza
    Rua Vicente Cozza
    Rua Vicente Cozza
    Rua Vicente Cozza
    Rua Vicente Cozza
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Osório Paes 35
    Rua Osório Paes 35
    Rua Osório Paes 35
    Rua Francisco Vargas
    Rua Francisco Vargas
    Rua Francisco Vargas
    Rua Orlando Falcone de Oliveira
    Rua Orlando Falcone de Oliveira
    Rua Orlando Falcone de Oliveira
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Fagundes Varela
    Avenida Fagundes Varela
    Avenida Fagundes Varela
    Avenida João da Mata
    Avenida João da Mata
    Avenida João da Mata
    Rua Genival de Oliveira
    Rua Genival de Oliveira
    Rua Genival de Oliveira
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida Governador Flávio Ribeiro Coutinho
    Avenida 27 de Julho
    Avenida 27 de Julho
    Avenida 27 de Julho
    Parque Solon de Lucena
    Parque Solon de Lucena
    Parque Solon de Lucena
    Rua Bancário Sergio Guerra
    Rua Bancário Sergio Guerra
    Rua Bancário Sergio Guerra
    Rua Hercílio Alves de Sousa
    Rua Hercílio Alves de Sousa
    Rua Hercílio Alves de Sousa
    Rua Pedro de Azevedo Cruz
    Rua Pedro de Azevedo Cruz
    Rua Pedro de Azevedo Cruz
    PB-095
    PB-095
    PB-095
    Rua Escritor Sebastião de Azevedo Bastos
    Rua Escritor Sebastião de Azevedo Bastos
    Rua Escritor Sebastião de Azevedo Bastos
    Rua Walfredo Macedo Brandão
    Rua Walfredo Macedo Brandão
    Rua Walfredo Macedo Brandão
    Rua Irineu Pinto
    Rua Irineu Pinto
    Rua Irineu Pinto
    Avenida General Edson Ramalho
    Avenida General Edson Ramalho
    Avenida General Edson Ramalho
    Rua Cônego Nicodemos Neves
    Rua Cônego Nicodemos Neves
    Rua Cônego Nicodemos Neves
    Rua Paulo Ouvidio de Lucena
    Rua Paulo Ouvidio de Lucena
    Rua Paulo Ouvidio de Lucena
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Avenida Presidente João Pessoa
    Rua Radialista Newton Júnior
    Rua Radialista Newton Júnior
    Rua Radialista Newton Júnior
    Avenida Doutor Eupídio de Almeida
    Avenida Doutor Eupídio de Almeida
    Avenida Doutor Eupídio de Almeida
    Rua Antônio da Silva
    Rua Antônio da Silva
    Rua Antônio da Silva
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Nossa Senhora de Lourdes
    Rua Nossa Senhora de Lourdes
    Rua Nossa Senhora de Lourdes
    Rua Bancário Sergio Guerra
    Rua Bancário Sergio Guerra
    Rua Bancário Sergio Guerra
    BR-230
    BR-230
    BR-230
    avenida Flamboyant
    avenida Flamboyant
    avenida Flamboyant
    Rua Bancário Sérgio Guerra
    Rua Bancário Sérgio Guerra
    Rua Bancário Sérgio Guerra
    Rua Ernesto Jerônimo de Farias
    Rua Ernesto Jerônimo de Farias
    Rua Ernesto Jerônimo de Farias
    Avenida Benício de Oliveira Lima
    Avenida Benício de Oliveira Lima
    Avenida Benício de Oliveira Lima
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Rua Francisco Timóteo de Souza
    Rua Francisco Timóteo de Souza
    Rua Francisco Timóteo de Souza
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida Valdemar Galdino Naziazeno
    Avenida General Bento da Gama
    Avenida General Bento da Gama
    Avenida General Bento da Gama
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Presidente Epitácio Pessoa
    Avenida Barão de Mamanguape
    Avenida Barão de Mamanguape
    Avenida Barão de Mamanguape
    Avenida Senador Humberto Lucena
    Avenida Senador Humberto Lucena
    Avenida Senador Humberto Lucena
    Avenida Floriano Peixoto
    Avenida Floriano Peixoto
    Avenida Floriano Peixoto
    Avenida Benjamin Constant
    Avenida Benjamin Constant
    Avenida Benjamin Constant
    Rua Antônio Camelo
    Rua Antônio Camelo
    Rua Antônio Camelo
    Avenida Izidro Gomes
    Avenida Izidro Gomes
    Avenida Izidro Gomes
    Avenida Presidente Nilo Peçanha
    Avenida Presidente Nilo Peçanha
    Avenida Presidente Nilo Peçanha
    Praça Antenor Navarro
    Praça Antenor Navarro
    Praça Antenor Navarro
    Rua Jardim Recreio III
    Rua Jardim Recreio III
    Rua Jardim Recreio III
    Rua Projetada 3
    Rua Projetada 3
    Rua Projetada 3
    Maurício de Araújo Gama Filho
    Maurício de Araújo Gama Filho
    Maurício de Araújo Gama Filho
    Rua Carlos Gomes
    Rua Carlos Gomes
    Rua Carlos Gomes
    Rua Governador Tarcísio Burity
    Rua Governador Tarcísio Burity
    Rua Governador Tarcísio Burity
    Rua Mamede Moisés Raia
    Rua Mamede Moisés Raia
    Rua Mamede Moisés Raia
    Rua Carlos Alverga
    Rua Carlos Alverga
    Rua Carlos Alverga
    Rua Helena Meira Lima
    Rua Helena Meira Lima
    Rua Helena Meira Lima
    Rua Henrique Nobrega
    Rua Henrique Nobrega
    Rua Henrique Nobrega
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Rua José Oscar Teixeira Primo
    Rua José Oscar Teixeira Primo
    Rua José Oscar Teixeira Primo
    Rua Maria Eva Moura
    Rua Maria Eva Moura
    Rua Maria Eva Moura
    Rua Carlos Alberto Souza
    Rua Carlos Alberto Souza
    Rua Carlos Alberto Souza
    Rua Antônio Viêira da Rocha
    Rua Antônio Viêira da Rocha
    Rua Antônio Viêira da Rocha
    Rua Gláuber Alisson Guimarães Figueiredo
    Rua Gláuber Alisson Guimarães Figueiredo
    Rua Gláuber Alisson Guimarães Figueiredo
    Rua Barúnas
    Rua Barúnas
    Rua Barúnas
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Avenida Marechal Floriano Peixoto
    Rua Terezinha de Medeiros Dantas Souza
    Rua Terezinha de Medeiros Dantas Souza
    Rua Terezinha de Medeiros Dantas Souza
    Rua Maria M de Figueiredo
    Rua Maria M de Figueiredo
    Rua Maria M de Figueiredo
    Rua dos Tucanos
    Rua dos Tucanos
    Rua dos Tucanos
    Rua Do Marfim Pescador
    Rua Do Marfim Pescador
    Rua Do Marfim Pescador
    Rua Coronel João Figueiredo
    Rua Coronel João Figueiredo
    Rua Coronel João Figueiredo
    Rua Sebastião César Paredes
    Rua Sebastião César Paredes
    Rua Sebastião César Paredes
    Rua Afrígio Ribeiro Brito
    Rua Afrígio Ribeiro Brito
    Rua Afrígio Ribeiro Brito
    Avenida Marcionila da Conceição
    Avenida Marcionila da Conceição
    Avenida Marcionila da Conceição
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Hélio Rodrigues
    Rua Hélio Rodrigues
    Rua Hélio Rodrigues
    Rua Anísio R de Souza Campos
    Rua Anísio R de Souza Campos
    Rua Anísio R de Souza Campos
    Rua Severia Maria Vasconcelos de Carvalho
    Rua Severia Maria Vasconcelos de Carvalho
    Rua Severia Maria Vasconcelos de Carvalho
    Rua Irineu Joffily
    Rua Irineu Joffily
    Rua Irineu Joffily
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Olívio de Moraes Magalhães
    Rua Antenor Navarro
    Rua Antenor Navarro
    Rua Antenor Navarro
    Avenida Vasco da Gama
    Avenida Vasco da Gama
    Avenida Vasco da Gama
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Vila Nova
    Rua Vila Nova
    Rua Vila Nova
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Avenida Paris
    Avenida Paris
    Avenida Paris
    Avenida Paris
    Avenida Paris
    Avenida Paris
    R. Rosemira Severiano Nascimento
    Rua Rosemira Severiano Nascimento
    R. Rosemira Severiano Nascimento
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Avenida Paris
    Avenida Paris
    Avenida Paris
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Praça Frei Paulo
    Rua Afonso Pena
    Rua Afonso Pena
    Rua Afonso Pena
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Rua Presidente João Pessoa
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Avenida Hilton Souto Maior
    Rua Otacílio de Albuquerque
    Rua Otacílio de Albuquerque
    Rua Otacílio de Albuquerque
    Rua Rosendo Elias
    Rua Rosendo Elias
    Rua Rosendo Elias
    Avenida Floriano Peixoto
    Avenida Floriano Peixoto
    Avenida Floriano Peixoto
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr
    addr


#### 4.3 Postal Codes

**SQL:**

```sql
SELECT value
       FROM (SELECT * FROM nodes_tags
               UNION ALL 
             SELECT * FROM ways_tags) tags
where key='postcode';
```

**Python:**


```python
SQL = "SELECT value "+\
       "FROM (SELECT * FROM nodes_tags "+\
               "UNION ALL "+\
             "SELECT * FROM ways_tags) tags "+\
"WHERE key='postcode' "
data = engine.execute(SQL).fetchall()
data
```




    [(u'58380-000',),
     (u'58414-500',),
     (u'58039-120',),
     (u'58380-000',),
     (u'58380-000',),
     (u'58013080',),
     (u'58380-000',),
     (u'58045010',),
     (u'58385-000',),
     (u'58360000',),
     (u'58030001',),
     (u'58045-010',),
     (u'58045-010',),
     (u'58045-010',),
     (u'58380000',),
     (u'58380000',),
     (u'58013-420',),
     (u'58030-330',),
     (u'58039-210',),
     (u'58039-181',),
     (u'58039-170',),
     (u'58039-170',),
     (u'58015-510',),
     (u'58015-510',),
     (u'58015-510',),
     (u'58041-000',),
     (u'58036-440',),
     (u'58077174',),
     (u'58400-180',),
     (u'58400-180',),
     (u'58400-180',),
     (u'58402-013',),
     (u'58042-006',),
     (u'58015-020',),
     (u'58013-131',),
     (u'58385-000',),
     (u'58038102',),
     (u'58360000',),
     (u'58360000',),
     (u'58402-045',),
     (u'58410-268',),
     (u'58025-000',),
     (u'58040-330',),
     (u'58320-000',),
     (u'58039-160',),
     (u'58040080',),
     (u'58304-973',),
     (u'58416-440',),
     (u'58440-960',),
     (u'58416-440',),
     (u'58423-490',),
     (u'58430-360',),
     (u'58109-525',),
     (u'58180-223',),
     (u'58429-500',),
     (u'58036605',),
     (u'58062-286',),
     (u'58.062-284',),
     (u'58414230',),
     (u'58400-270',),
     (u'58400-270',),
     (u'58040-720',),
     (u'5837000',),
     (u'58015-280',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',),
     (u'addr',)]



**Fixing postcode problems:**


```python
import re

#All postcodes for this region should be between 58000000 and 58999999
MIN = 58000000 
MAX = 58999999
DEFAULT = 58000001

for postcode, in data:
    postcode = re.sub('[.-]', '', postcode)
    if re.match("^[0-9]*$", postcode) and (int(postcode) > MIN and int(postcode) < MAX):
        print postcode
    else:
        print DEFAULT
```

    58380000
    58414500
    58039120
    58380000
    58380000
    58013080
    58380000
    58045010
    58385000
    58360000
    58030001
    58045010
    58045010
    58045010
    58380000
    58380000
    58013420
    58030330
    58039210
    58039181
    58039170
    58039170
    58015510
    58015510
    58015510
    58041000
    58036440
    58077174
    58400180
    58400180
    58400180
    58402013
    58042006
    58015020
    58013131
    58385000
    58038102
    58360000
    58360000
    58402045
    58410268
    58025000
    58040330
    58320000
    58039160
    58040080
    58304973
    58416440
    58440960
    58416440
    58423490
    58430360
    58109525
    58180223
    58429500
    58036605
    58062286
    58062284
    58414230
    58400270
    58400270
    58040720
    58000001
    58015280
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001
    58000001


# Sort cities by count, descending


**SQL:**

```sql
SELECT value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE key LIKE '%city'
GROUP BY value
ORDER BY count DESC
```

**Python:**


```python
SQL = "SELECT key, value, COUNT(*) as count "+\
    "FROM (SELECT * FROM nodes_tags "+\
        "UNION ALL "+\
    "SELECT * FROM ways_tags) tags "+\
"GROUP BY key, value "+\
"ORDER BY count DESC"

data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["key","value", "count"])
df_key_city = df[df['key'] == 'city']
df_key_city
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>key</th>
      <th>value</th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24</th>
      <td>city</td>
      <td>addr</td>
      <td>610</td>
    </tr>
    <tr>
      <th>59</th>
      <td>city</td>
      <td>João Pessoa</td>
      <td>146</td>
    </tr>
    <tr>
      <th>141</th>
      <td>city</td>
      <td>Ingá</td>
      <td>31</td>
    </tr>
    <tr>
      <th>160</th>
      <td>city</td>
      <td>Campina Grande</td>
      <td>22</td>
    </tr>
    <tr>
      <th>344</th>
      <td>city</td>
      <td>Campia Grade Paraíba</td>
      <td>5</td>
    </tr>
    <tr>
      <th>410</th>
      <td>city</td>
      <td>Serra Redonda</td>
      <td>3</td>
    </tr>
    <tr>
      <th>495</th>
      <td>city</td>
      <td>Itatuba</td>
      <td>3</td>
    </tr>
    <tr>
      <th>517</th>
      <td>city</td>
      <td>Alhandra</td>
      <td>2</td>
    </tr>
    <tr>
      <th>646</th>
      <td>city</td>
      <td>Conde</td>
      <td>2</td>
    </tr>
    <tr>
      <th>708</th>
      <td>city</td>
      <td>Bayeux</td>
      <td>2</td>
    </tr>
    <tr>
      <th>829</th>
      <td>city</td>
      <td>Queimadas</td>
      <td>1</td>
    </tr>
    <tr>
      <th>854</th>
      <td>city</td>
      <td>Pitimbu-PB</td>
      <td>1</td>
    </tr>
    <tr>
      <th>919</th>
      <td>city</td>
      <td>JOAO PESSOA</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1702</th>
      <td>city</td>
      <td>Itabaiana</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1703</th>
      <td>city</td>
      <td>Joao Pessoa</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1944</th>
      <td>city</td>
      <td>ingá</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>city</td>
      <td>Salgado de São Félix</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2105</th>
      <td>city</td>
      <td>Itabaiaba</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2452</th>
      <td>city</td>
      <td>Gurinhem</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2508</th>
      <td>city</td>
      <td>Pedras de Fogo</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2555</th>
      <td>city</td>
      <td>Fagundes</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2571</th>
      <td>city</td>
      <td>Cabedelo</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3024</th>
      <td>city</td>
      <td>joao pessoa</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3069</th>
      <td>city</td>
      <td>João Pessoa PB</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3133</th>
      <td>city</td>
      <td>Santa Rita</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



There are many rows with the same city written differently with the same semantic. Example: *João Pessoa PB*, *JOAO PESSOA*, *Joao Pessoa* and *João Pessoa*.

# Data Overview and Additional Ideas


### File sizes

* CG.osm...................74MB
* nodes_tags.csv..........773KB
* nodes.csv...............27.1M
* ways_nodes.csv..........9.7M
* ways_tags.csv...........4M
* ways.csv................2.9M

### Number of nodes


```python
SQL = "SELECT COUNT(*) FROM nodes"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["count"])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>312581</td>
    </tr>
  </tbody>
</table>
</div>



### Number of ways


```python
SQL = "SELECT COUNT(*) FROM ways"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["count"])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>47050</td>
    </tr>
  </tbody>
</table>
</div>



### Number of unique users


```python
SQL = "SELECT COUNT(DISTINCT(e.uid)) "+\
      "FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e"
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["count"])
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>436</td>
    </tr>
  </tbody>
</table>
</div>



### Top 10 contributing users



```python
import matplotlib.pyplot as plt

SQL = "SELECT e.user_name, COUNT(*) as num "+\
"FROM (SELECT user_name FROM nodes UNION ALL SELECT user_name FROM ways) e "+\
"GROUP BY e.user_name "+\
"ORDER BY num DESC "+\
"LIMIT 10"

data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["user_name","num"])

x = range(len(df['user_name'].values))
my_xticks = df['user_name'].values


fig = plt.gcf()
plt.xticks(x, my_xticks, rotation='vertical')

plt.plot(x, df['num'].values, 'r^') 

plt.title('Contributing Users')
plt.xlabel('User Names')
plt.ylabel('Contributions')

plt.subplots_adjust(bottom=0.15)
plt.margins(0.2)

plt.show()

```


![png](output_61_0.png)


### Number of users appearing only once (having 1 post)


**SQL:**

```sql
SELECT user_name, COUNT(*)
     FROM (SELECT user_name FROM nodes UNION ALL SELECT user_name FROM ways) e
     GROUP BY user_name HAVING COUNT(*) = 1
```

**Python:**


```python
SQL = "SELECT user_name, COUNT(*) "+\
     "FROM (SELECT user_name FROM nodes UNION ALL SELECT user_name FROM ways) e "+\
     "GROUP BY user_name HAVING COUNT(*) = 1"
    
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["user_name","count"])
df.count()
```




    user_name    84
    count        84
    dtype: int64



# Additional Ideas


### Top 10 appearing amenities



```python
import matplotlib.pyplot as plt

SQL = "SELECT value, COUNT(*) as num "+\
    "FROM nodes_tags "+\
    "WHERE key='amenity' "+\
    "GROUP BY value "+\
    "ORDER BY num DESC"
    
data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["values","count"])
x = range(len(df['values'].values))
my_xticks = df['values'].values


fig = plt.gcf()
plt.xticks(x, my_xticks, rotation='vertical')

plt.plot(x, df['count'].values) 
plt.title('Apperaring Amenities')
plt.xlabel('AMENITIES')
plt.ylabel('COUNT')
fig.set_size_inches(18, 8.5)
plt.show()
```


![png](output_69_0.png)


The information tagged is divergent from the real world. If we analyze the top 10 appearing amenities we have ~ 2.5x more restaurant than bar or fast food trucks and it is absolutly false. What was the criteria used to classifying an establishment with 'restaurant', 'fast_food' or 'bar' or 'pub')?. A possible solution in this case is use a google maps street view and walk to the address and using a transparent criteria reclassify or ask for some help in some social media.

### Users with generate errors in abbreviations names or postcodes

For each row with error in abbreviations and postcodes we select the _id_ to find the users with more contribute with problems in the dataset.


```python
SQL = "SELECT user_name, count(*) as num FROM WAYS "+\
"WHERE id in (65586659,138277880,191658499,194970920,195038714,195040104,195040106,195040107, "+\
             "229334940,234058106,234058393,242706196,258907452,259278813,259283262,265700650, "+\
             "266629174,278206095,280665688,281223510,286466669,295391511,311264457,313867017, "+\
             "316414020,329028575,329160730,329592243,340312961, "+\
             "340313132,340313133,340313717,340313718,340314063,340314065,340314066,340316560, "+\
             "340316561,340316563,340316663,340319200,340324759,340325019,340325438,340325439, "+\
             "340325440,340328538,340328539,340328541,340328542,340364509,340364515,340364712, "+\
             "340365089,340365090,340365913,340365914,340365973,340366140,340366539,340366614, "+\
             "340366615,340366630,340366631,340366632,340367251,340416321,340416404,340416405, "+\
             "340417600,340417601,340417602,340417603,340417755,340417823,340418256,340418434, "+\
             "340419125,340419126,340419127,340420207,340420208,340420209,340420210,340420211, "+\
             "340422051,340422054,340422055,340422056,340422057,340422058,340422059,340423026, "+\
             "340423034,340423037,340423038,340423040,340423041,340447841,340448620,340449287, "+\
             "342651401,346614635,366024517,366024900,374506774,391298813,391598881,391822437, "+\
             "395915995,447884595,447884596,454369375,479928628,480776043,497215943,500811548, "+\
             "500811551,500812648,507371208,507372315,518593795,532749954,532749957,532749958, "+\
             "532749959,541928961,544419258,544419259,544419260,544794145,548625344,550482807, "+\
             "556887520,563941013,587003802,611655187,611656778,611657079,611668352,611668774, "+\
             "625270979) "+\
"GROUP BY user_name ORDER BY num desc"


data = engine.execute(SQL).fetchall()
df = pd.DataFrame(data, columns=["user_name","num"])

x = range(len(df['user_name'].values))
my_xticks = df['user_name'].values


fig = plt.gcf()
plt.xticks(x, my_xticks, rotation='vertical')

plt.plot(x, df['num'].values, 'r^') 

plt.title('Contributing Users')
plt.xlabel('User Names')
plt.ylabel('Contributions')

fig.set_size_inches(18, 8.5)


plt.show()

```


![png](output_73_0.png)


The user: **GPS Editor** was responsable for more than 70 errors. In the future we could meansure the confiability or quality of insertion for each users. It could to help to find and predict problems on the dataset. 

# Conclusion


The map area selected to build this project no presents problems with street names abbreviations or postcodes. However, it presents another issues:

* **Sintatic problems:** Many times, we have the same semantic entity written with different ways or with discrete orthographic mistakes. Example: JOAO PESSOA, João Pessoa, joão pessoa, joao pessoa. This problem dilute the importance of a term against these different ways to count it. A possible solution for this should be the construction of an algorithm to group this world based on lexicos or [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance).

* **Wrong tendencies:** The information tagged is divergent from the real world. If we analyze the top 10 appearing amenities we have ~ 2.5x more restaurant than bar or fast food trucks and it is absolutly false. What was the criteria used to classifying an establishment with 'restaurant', 'fast_food' or 'bar' or 'pub')?. A possible solution in this case is use a google maps street view and walk to the address and using a transparent criteria reclassify or ask for some help in some social media.

* **Temporal tagging:** Personally I was to walk in the street this week to check the information on these openstreetmap dataset and some points there is no more exists. A café was changes to a bar, a gas stations was closed and so on.


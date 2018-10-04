COPY nodes(id,lat,lon,user_name,uid,version,changeset,timestamp) 
FROM '/Users/zegildo/Desktop/Udacity/codereviewer-master/6-Wrangle_OpenStreetMap_Data/csvs/nodes.csv' DELIMITER ',' CSV HEADER;

COPY nodes_tags(key,type,id,value) 
FROM '/Users/zegildo/Desktop/Udacity/codereviewer-master/6-Wrangle_OpenStreetMap_Data/csvs/nodes_tags.csv' DELIMITER ',' CSV HEADER;

COPY ways(id,user_name,uid,version,changeset,timestamp) 
FROM '/Users/zegildo/Desktop/Udacity/codereviewer-master/6-Wrangle_OpenStreetMap_Data/csvs/ways.csv' DELIMITER ',' CSV HEADER;

COPY ways_nodes(id,node_id,position) 
FROM '/Users/zegildo/Desktop/Udacity/codereviewer-master/6-Wrangle_OpenStreetMap_Data/csvs/ways_nodes.csv' DELIMITER ',' CSV HEADER;

COPY ways_tags(id,key,value,type) 
FROM '/Users/zegildo/Desktop/Udacity/codereviewer-master/6-Wrangle_OpenStreetMap_Data/csvs/ways_tags.csv' DELIMITER ',' CSV HEADER;
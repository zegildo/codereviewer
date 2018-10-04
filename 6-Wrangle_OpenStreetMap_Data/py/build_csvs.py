#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import re
import csv
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

SAMPLE_OSM = "../osm/CG.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['key','type','id','value']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def node_tags(element, problem_chars, default_tag_type):
    tags = []
    for child in element:
        k_value = child.get("k")
        if (child.tag == 'tag') and (not problem_chars.match(k_value)):
            node_tags = {}
            node_tags['id'] = element.get("id")
            node_tags['value'] = child.get("v")
            node_tags['type'], node_tags['key'] = get_right_key_type(k_value, default_tag_type)
            tags.append(node_tags)
    return tags

def get_right_key_type(k_value, default_tag_type):
    SCAPE = ":"
    if SCAPE in k_value:
        return k_value.split(SCAPE, 1)
    else:
        return default_tag_type, k_value
        
def node_struct(element, node_attr_fields, problem_chars, default_tag_type):
    node_attribs = {}
    for attr in node_attr_fields:
        node_attribs[attr] = element.get(attr)
    tags = node_tags(element, problem_chars, default_tag_type)
    
    return node_attribs, tags    

def ways_nodes(element):
    w_nodes = []
    posicion = 0
    for child in element:
        if(child.tag == 'nd'):
            w_nodes_attr = {}
            w_nodes_attr['id'] = element.get("id")
            w_nodes_attr['node_id'] = child.get("ref")
            w_nodes_attr['position'] = posicion
            posicion +=1
            w_nodes.append(w_nodes_attr)
    return w_nodes
            
def way_struct(element, way_attr_fields, problem_chars, default_tag_type):
    way_attribs = {}
    for attr in way_attr_fields:
        way_attribs[attr] = element.get(attr)
    w_nodes = ways_nodes(element)
    tags = node_tags(element, problem_chars, default_tag_type)

    return way_attribs, w_nodes, tags
    

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    if element.tag == 'node':
        node_attribs, tags = node_struct(element, node_attr_fields, problem_chars, default_tag_type) 
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        way_attribs, way_nodes, tags = way_struct(element, way_attr_fields, problem_chars, default_tag_type)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def salve_csv(csv_name, fieldnames, elements):
    print(csv_name)
    print(fieldnames)

    with open(csv_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for element in elements:
            writer.writerow([element[field] for field in fieldnames])

def create_csv(file_in):
    """Create csvs files"""
    nodes, nodes_tags = [], []
    ways, ways_nodes, ways_tags  = [], [], []

    for element in get_element(file_in, tags=('node', 'way')):
        el = shape_element(element)

        if element.tag == 'node':
            nodes.append(el['node'])
            for tag in el['node_tags']:
                nodes_tags.append(tag)
                
        elif element.tag == 'way':
            ways.append(el['way'])
            
            for w_nodes in el['way_nodes']:
                ways_nodes.append(w_nodes)
            
            for w_tag in el['way_tags']:
                ways_tags.append(w_tag)
    
    salve_csv(NODES_PATH, NODE_FIELDS, nodes)
    salve_csv(NODE_TAGS_PATH, NODE_TAGS_FIELDS, nodes_tags)
    salve_csv(WAYS_PATH, WAY_FIELDS, ways)
    salve_csv(WAY_NODES_PATH, WAY_NODES_FIELDS, ways_nodes)
    salve_csv(WAY_TAGS_PATH, WAY_TAGS_FIELDS, ways_tags)

if __name__ == '__main__':
    create_csv(SAMPLE_OSM)

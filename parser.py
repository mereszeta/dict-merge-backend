import xml.dom.minidom

import xml.etree.ElementTree as ET

import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

database = client["dictmerge"]
collection = database["wordnet"]
collectionPolnet = database["polnet"]

units = []


#


def parse_wordnet():
    tree = ET.parse("./plwordnet-4.0.xml")
    root = tree.getroot()
    lexical_units = root.findall('lexical-unit')
    synset_units = root.findall('synset')
    # lexical_relations = root.findall('lexicalrelations')
    # synset_relations = root.findall("synsetrelations")
    for unit in lexical_units:
        if unit.attrib['workstate'] != "nieprzetworzony":
            units.append({"id": unit.attrib["id"], "name": unit.attrib["name"], "desc": unit.attrib["desc"],
                          "pos": unit.attrib["pos"]})
    collection.insert_many(units)


def parse_polnet():
    tree = ET.parse("./polnet.xml")
    root = tree.getroot()
    synsets = root.findall('SYNSET')
    words_res = {}
    for synset in synsets:
        words = list(set(map(lambda x: x.text, synset.find("SYNONYM").findall("LITERAL"))))
        definition = synset.find("DEF").text
        for word in words:
            if word in words_res:
                words_res[word].append(definition)
            else:
                words_res[word] = [definition]
    items = list(map(lambda item: {"name": item[0], "desc": item[1]}, words_res.items()))
    collectionPolnet.insert_many(items)


parse_polnet()

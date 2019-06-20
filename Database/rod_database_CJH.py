# CJH creading functions to make a RoDpedia item database
# TODO: make this into a class, make a web crawler, save to CSV

from bs4 import BeautifulSoup
import re
import requests

url1 ='https://rodpedia.realmsofdespair.info/wiki/A_black_silk_belt'
url2 ='https://rodpedia.realmsofdespair.info/wiki/A_brigand%27s_dagger'
def get_clean_url(url):

    soup = get_soup(url)
    # strip out the styling crap
    for script in soup(['script','style']):
        script.extract()
    test = soup.get_text()
    cleaned = re.sub(r'(\n)+', r'\n', test)
    description_text = cleaned.split('Retrieved from')[0]

    #list of categories
    categories = re.findall('Categories:(.*)$',test,re.MULTILINE)
    if len(categories) > 0:
        categories = categories[0].split("|")
        for idx, category in enumerate(categories):
            categories[idx] = re.sub(r'Items', r'', category).strip()

    # pull out the level item type and weight...
    # One idiot put a colon in his weight description... others put in total crap
    if len(re.findall('level (\d*)\s(.*), weight:? (\d*)', test, re.MULTILINE)) > 0:
        (level, item_type, weight) = re.findall('level (\d*)\s(.*), weight:? (\d*)', test, re.MULTILINE)[0]
    else:
        (level, item_type, weight) = ('','','')
    # check to see if it is weapon or armor
    if 'weapon' in item_type:
        weapon_type = re.findall('(.*)weapon',item_type)[0]
        item_type = "weapon"
        damage = check_length(re.findall('Damage is (\d+) to (\d+).* (\d+)',description_text,re.MULTILINE))
    else:
        weapon_type=""
        damage=""
    # Sometimes there is no Object description - probably need to flag this as a problem type...
    item_name = check_length(re.findall('Object \'(.*)\'',description_text))
    if len(item_name) < 2 :
        item_name = check_length(re.findall('(.*) - RoDpedia', description_text))
    worn = check_length(re.findall(' worn:\s+(\S*)',description_text))

    gold = check_length(re.findall('gold value of (\d+)',description_text))
    special_properties = check_split(re.findall('Special properties:(.*)$',description_text,re.MULTILINE))
    genres_allowed = check_split(re.findall('Genres allowed:(.*)$',description_text,re.MULTILINE))
    armor_class = check_length(re.findall('Armor class is (\d+) of (\d+).$',description_text,re.MULTILINE))
    affects_list = re.findall('Affects (.+) by (.+)[\.?]$',description_text,re.MULTILINE)
    # Glance descriptions are pretty rare, actually
    glance_desc = check_length(re.findall('^(.*)$\s+Identify',description_text,re.MULTILINE))
    if any(bad in glance_desc for bad in {'Notes','Jump to','is a stub'}):
        glance_desc = ''
    if len(description_text.split('/Exam')) > 1:
        exam_desc = re.sub(r'\n',r' ',description_text.split('/Exam')[1].strip())
    else:
        exam_desc=""
    if any(bad in exam_desc for bad in {'Notes','Jump to'}):
        exam_desc = ''
    other_keys_names = ['Mob','Area','Pop', 'Manufactured','Out of Game','Minimum Level','Known Keywords']
    other_keys_vals = []
    for k in other_keys_names:
        temp = re.findall(k+':(.*)',description_text,re.MULTILINE)
        if len(temp)>0:
            temp = temp[0].strip()
        else:
            temp = ""
        other_keys_vals.append(temp)
    other_keys = dict(zip(other_keys_names, other_keys_vals))

    item_dict = {'ITEM_NAME':item_name,
                'LEVEL':level,
                'ITEM_TYPE':item_type,
                'WORN':worn,
                'ARMOR_CLASS':armor_class,
                'WEAPON_TYPE':weapon_type,
                'DAMAGE':damage,
                'GOLD':gold,
                'WEIGHT':weight,
                'SPECIAL_PROPERTIES':special_properties,
                'GENRES_ALLOWED':genres_allowed,
                'AFFECTS_LIST':affects_list,
                'GLANCE_DESCRIPTION':glance_desc,
                'EXAM_DESCRIPTION': exam_desc,
                'CATEGORIES':categories,
                 'HTTP_DESCRIPTION':description_text}
    item_dict.update(other_keys)

    return item_dict

def check_split(thing):
    if len(thing)>0:
        return thing[0].split()
    else:
        return ""

def check_length(thing):
    if len(thing)>0:
        return thing[0]
    else:
        return ""

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    return soup

def get_description(url):
    soup = get_soup(url)
    for script in soup(['script','style']):
        script.extract()
    test = soup.get_text()
    cleaned = re.sub(r'(\n)+', r'\n', test)
    description_text = cleaned.split('Retrieved from')[0]
    return description_text

def get_valid_item_urls(url):
    soup = get_soup(url)
    header = 'https://rodpedia.realmsofdespair.info'
    badstrings = {':', 'Categor', 'index', 'RoDpedia', 'http', '#', 'Main_Page'}
    url_list = []
    bad_url_list = []
    for a in soup.find_all('a', href=True):
        if any(bad in str(a) for bad in badstrings):
            #print('**BAD URL**:', a['href'])
            bad_url_list.append(header + a['href'])
        else:
            #print('ITEM:', a['href'])
            url_list.append(header + a['href'])
    return[url_list,bad_url_list]

def get_complete_url_list():
    all_urls = []
    for url in item_urls:
        all_urls.append(get_valid_item_urls(url)[0])
    flat_list = [item for sublist in all_urls for item in sublist]
    return flat_list

item_urls = ['https://rodpedia.realmsofdespair.info/wiki/Category:Items',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Black+silk+belt%2C+a',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Chained+dragonhide+wristlet',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Dented+vambraces+of+a+fallen+warrior',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Flying+broom%2C+A',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Heaume+of+the+Venerable',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Leather+restraints',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Ninja+gi%2C+a',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Pop+Items',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Seal+of+Shadows%2C+a',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Small%2C+copper+key%2C+a',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=Tattered+robes+of+intolerance%2C+the',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=White+scale+mail',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=brand+of+Doom',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=extradimensional+portal',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=ice+cold+glass+of+lemonade',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=old+suit+of+leather+armor',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=rolling+pin',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=spiked+dog+collar',
             'https://rodpedia.realmsofdespair.info/index.php?title=Category:Items&from=wooden+post']

# messed up and brought in a trailing '.' sometimes
def fix_tuples(item):
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        i[1] = re.sub(r'\.', r'', i[1])
    return affects_list

def get_attribute(item,attribute):
    result = ""
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        if i[0] == attribute:
            result = i[1]
    return result
    #item['AFFECTS_LIST'] = affects_list

# CJH creading functions to make a RoDpedia item database
# TODO: make this into a class, fix AC display, save to Excel with column widths, make smart queries and summary stats
# TODO - fix AC, SAVES, make simpler
import re
import requests
import pickle
import pandas as pd
from bs4 import BeautifulSoup

# -------- WEB SECTION -----------
def get_soup(url):
    """Building block function for getting a soup from a url."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    return soup

def get_description(url):
    """Quick way to check the basic HTML description of an item."""
    soup = get_soup(url)
    for script in soup(['script','style']):
        script.extract()
    test = soup.get_text()
    cleaned = re.sub(r'(\n)+', r'\n', test)
    description_text = cleaned.split('Retrieved from')[0]
    return description_text

def get_valid_item_urls(url):
    """Takes a Rodpedia index page and converts to a list of valid item urls."""
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
    """Builds a list of every valid Rodpedia item"""
    all_urls = []
    for url in item_urls:
        all_urls.append(get_valid_item_urls(url)[0])
    flat_list = [item for sublist in all_urls for item in sublist]
    return flat_list

# This is the list of everything on Rodpedia as of 6/20/2019
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

# -------- ITEM CREATION SECTION -----------
def make_item_from_url(url):
    """Make an item from an Rodpedia item url."""
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

def fix_exam(item):
    """Originally I had tried to split the text on the Description/Exam but that was not general enough"""
    # make the original .* not greedy with the ? - that gives us BOTH of these
    # not sure why it doesn't work without removing the all the \n first
    str = re.sub(r'\n', r' ', item['HTTP_DESCRIPTION'])
    notecount=len(re.findall('Notes', str, re.MULTILINE))
    if notecount >1:
        #Break it apart by Notes
        exam = re.findall('Description/Exam(.*?)Notes?', str, re.MULTILINE)
    else:
        #Take the whole thing
        exam = re.findall('Description/Exam(.*)', str)
    match = ''
    if len(exam)>1:
        match = exam[1].strip()
    elif len(exam) > 0:
        match = exam[0].strip()
    else:
        match=''
    return match

def check_split(thing):
    """Helper function to deal with multi-line regexp searches of Rodpedia entries."""
    if len(thing)>0:
        return thing[0].split()
    else:
        return ""

def check_length(thing):
    """Helper function to deal with single-line regexp searches of Rodpedia entries."""
    if len(thing)>0:
        return thing[0]
    else:
        return ""

def check_int(thing):
    """Helper function to deal with single-line regexp searches of Rodpedia entries."""
    if len(thing) > 0:
        return int(thing[0])
    else:
        return ""

def print_item(item):
    """Takes an item (dictionary) and prints the it in useful format"""
    print("\nItem name: {}\nLevel: {}\tWorn: {} \tType: {} {}"
          .format(item['ITEM_NAME'],item['LEVEL'],item['WORN'],item['ITEM_TYPE'],item['WEAPON_TYPE']))
    print("AC: {}\tDamage:{}".format(item['ARMOR_CLASS'],item['DAMAGE']))
    print("STR: {} INT: {} WIS: {} DEX: {} CON: {} CHA: LCK: {} HIT: {} DMG: {}"
          .format(item['STR'],item['INT'],item['WIS'],item['DEX'],item['CON'],item['CHA'],item['LCK'],item['HIT_ROLL'],item['DAMAGE_ROLL']))
    print("HP: {}\t MANA: {}".format(item['HP'], item['MANA']))
    print("Area: {}\t Mob: {}".format(item['Area'], item['Mob']))

def grep_name(items, name):
    """Intial method for grepping the database"""
    for ix, item in enumerate(items):
        if name.lower() in item['ITEM_NAME'].lower():
            print("\nMatch ID: {}".format(ix),end='')
            print_item(item)

def grep_all(items, name):
    """Intial method for grepping the database"""
    for ix, item in enumerate(items):
        for attrib in item:
            if name.lower() in str(item[attrib]).lower():
                print("\nMatch ID: {}".format(ix),end='')
                print_item(item)
                break

def numerate(item):
    """Just go though everything and if it can be changed to an int, do it"""
    # note i could not loop through db and reassign, i had to make a blank and populate it with this
    temp_item = item.copy()
    for key in temp_item:
        #print(key + ' : ' + str(item[key]))
        try:
            temp_item[key] = int(temp_item[key])
            #print("Converted {} to int".format(temp_item[key]))
        except ValueError as verr:
            #print ("Value error on converting {}".format(temp_item[key]))
            pass  # do job to handle: s does not contain anything convertible to int
        except Exception as ex:
            #print ("Exception on converting {}".format(temp_item[key]))
            pass  # do job to handle: Exception occurred while converting to int
    return temp_item

# -------- ITEM ATTRIBUTE PROCESSING SECTION -----------
# messed up and brought in a trailing '.' sometimes
def fix_tuples(item):
    """Fixer function because I originally brought in a trailing period on AFFECTS_LIST"""
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        i[1] = re.sub(r'\.', r'', i[1])
    return affects_list

def get_attribute(item,attribute):
    """Converts tuples to list and returns the value of an attribute, e.g. 'damage roll' """
    result = ""
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        if i[0] == attribute:
            result = i[1]
    return result
    #item['AFFECTS_LIST'] = affects_list


# -------- PICKLE SECTION -----------
def save_db(items,outfile=''):
    """Save the database to pkl format"""
    if outfile == '':
        outfile = 'RoD_Database.pkl'
    with open(outfile, 'wb') as fp:
        pickle.dump(items, fp)

def load_db(outfile=''):
    """Save the database to pkl format"""
    if outfile == '':
        outfile = 'RoD_Database.pkl'
    with open(outfile, 'rb') as fp:
        items = pickle.load(fp)
    return items

# -------- PANDAS SECTION -----------
# columns for the pandas save
xcel_cols = ['ITEM_NAME','Area','LEVEL','ITEM_TYPE','WORN','AC','WEAPON_TYPE','AVERAGE_DAMAGE','STR','INT',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','GLANCE_DESCRIPTION',
        'SPECIAL_PROPERTIES','WEIGHT','GOLD', 'AFFECTS_LIST', 'DAMAGE', 'Manufactured',
        'Minimum Level', 'Mob', 'Out of Game', 'Pop','Known Keywords','CATEGORIES',
        'GENRES_ALLOWED','ARMOR_CLASS','EXAM_DESCRIPTION','HTTP_DESCRIPTION']

def make_pandas_df(items,errors='ignore'):
    """Make a dataframe and make sure the right strings can be treated as numbers"""
    df = pd.DataFrame(items)
    #order them
    df = df[xcel_cols]
    numerics = ['LEVEL','AC','AVERAGE_DAMAGE','STR','INT',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','WEIGHT','GOLD','Minimum Level']
    for col in numerics:
       #for excel you want to ignore, but for using in python you need to coerce
       #df[col]= pd.to_numeric(df[col], errors='ignore')
       #df[col] = pd.to_numeric(df[col], errors='coerce')
       df[col] = pd.to_numeric(df[col], errors=errors)
    return df

def save_pd_to_excel(df,outfile='',sheet_name=''):
    """Make the excel file formatted so that I never have to touch it manually"""
    if outfile=='':
        outfile = 'RodDatabase.xlsx'
    if sheet_name=='':
        sheet_name = 'CJH RoD DB v0.1 06212019'
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, columns=xcel_cols)
    worksheet = writer.sheets[sheet_name]
    # Change the column widths - default is the length of the column name
    col_names= ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y','Z',
                'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK']
    for s, col in zip(xcel_cols, col_names):
        #apprently you can't just give it a single column name - have to use 'B:B' when you mean 'B'
        worksheet.set_column(col+':'+col, len(s)+3)
    # Item name is the only one I'll make bigger than default
    worksheet.set_column('B:B', 42)
    writer.save()



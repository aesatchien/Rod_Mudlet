# CJH creading functions to make a RoDpedia item database
# TODO: make this into a class, fix AC display, save to Excel with column widths, make smart queries and summary stats
# TODO - fix SAVES, make simpler
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
def item_from_url(url):
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

    item_dict = item_from_description(description_text)
    item_dict.update({'CATEGORIES':categories})
    return item_dict

def item_from_description(description_text):
    # list of categories - crap i threw this away, have to keep it somehow next time

    # pull out the level item type and weight...
    # One idiot put a colon in his weight description... others put in total crap
    if len(re.findall('level (\d*)\s(.*), weight:? (\d*)', description_text, re.MULTILINE)) > 0:
        (level, item_type, weight) = re.findall('level (\d*)\s(.*), weight:? (\d*)', description_text, re.MULTILINE)[0]
        level = safe_int(level)
        weight = safe_int(weight)
    else:
        (level, item_type, weight) = ('', '', '')
    # check to see if it is weapon or armor
    if 'weapon' in item_type:
        weapon_type = re.findall('(.*)weapon', item_type)[0]
        item_type = "weapon"
        damage = check_length(re.findall('Damage is (\d+) to (\d+).* (\d+)', description_text, re.MULTILINE))
        if len(damage) >    1:
            average_damage = safe_int(damage[2])
        else:
            average_damage = ''
    else:
        weapon_type = ''
        damage = ''
        average_damage = ''
    # Sometimes there is no Object description - probably need to flag this as a problem type...
    item_name = check_length(re.findall('Object \'(.*)\'', description_text))
    if len(item_name) < 2:
        item_name = check_length(re.findall('(.*) - RoDpedia', description_text))
    worn = check_length(re.findall(' worn:\s+(\S*)', description_text))
    gold = safe_int(check_length(re.findall('gold value of (\d+)', description_text)))
    special_properties = check_split(re.findall('Special properties:(.*)$', description_text, re.MULTILINE))
    genres_allowed = check_split(re.findall('Genres allowed:(.*)$', description_text, re.MULTILINE))
    races_allowed = check_split(re.findall('Races allowed:(.*)$', description_text, re.MULTILINE))
    armor_class = check_length(re.findall('Armor class is (\d+) of (\d+).$', description_text, re.MULTILINE))
    if len(armor_class)>0:
        ac = safe_int(armor_class[1])
    else:
        ac=''
    affects_list = re.findall('Affects (.+) by (.+)[\.?]$', description_text, re.MULTILINE)
    # Glance descriptions are pretty rare, actually
    glance_desc = check_length(re.findall('^(.*)$\s+Identify', description_text, re.MULTILINE))
    if any(bad in glance_desc for bad in {'Notes', 'Jump to', 'is a stub'}):
        glance_desc = ''
    exam_desc = fix_exam_description({'HTTP_DESCRIPTION':description_text})

    # one liners present in the web description
    other_keys_names = ['Mob', 'Area','Pop', 'Manufactured', 'Out of Game', 'Minimum Level', 'Known keywords']
    other_keys_vals = []
    for k in other_keys_names:
        temp = re.findall(k+':(.*)',description_text,re.MULTILINE)
        if len(temp)>0:
            temp = temp[0].strip()
        else:
            temp = ""
        other_keys_vals.append(temp)
    other_dict = dict(zip([re.sub(r' ',r'_',x.upper()) for x in other_keys_names], other_keys_vals))

    stat_keys = ['damage roll', 'hit roll', 'dexterity', 'strength', 'wisdom', 'constitution', 'intelligence',
                          'luck', 'charisma', 'hp', 'mana']
    stat_key_names = ['DAMAGE_ROLL', 'HIT_ROLL','DEX','STR','WIS','CON','INT','LCK','CHA','HP','MANA']
    calculated_stats=[]
    for affect in stat_keys:
        calculated_stats.append(safe_int(get_attribute({'AFFECTS_LIST':affects_list}, affect)))
    calculated_dict = dict(zip(stat_key_names, calculated_stats))

    item_dict = {'ITEM_NAME': item_name,
                 'LEVEL': level,
                 'ITEM_TYPE': item_type,
                 'WORN': worn,
                 'AC': ac,
                 'WEAPON_TYPE': weapon_type,
                 'AVERAGE_DAMAGE': average_damage,
                 'VALUE': calculate_value({'AFFECTS_LIST': affects_list})}
    item_dict.update(calculated_dict)
    item_dict.update(other_dict)
    item_dict.update({'GOLD': gold,
                 'WEIGHT': weight,
                 'SPECIAL_PROPERTIES': special_properties,
                 'GENRES_ALLOWED': genres_allowed,
                 'RACES_ALLOWED': races_allowed,
                 'AFFECTS_LIST': affects_list,
                 'GLANCE_DESCRIPTION': glance_desc,
                 #'CATEGORIES': categories,
                 'ARMOR_CLASS': armor_class,
                 'DAMAGE': damage,
                 'EXAM_DESCRIPTION': exam_desc,
                 'HTTP_DESCRIPTION': description_text})
    return item_dict


def fix_exam_description(item):
    """Originally I had tried to split the text on the
    Description/Exam but that was not general enough"""
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

def numerate(item):
    """Just go though everything and if it can be changed to an int, do it"""
    # note I could not loop through db and reassign, i had to make a blank and populate it with this
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

# -------- UTILITY SECTION -----------
def print_item(item):
    """Takes an item (dictionary) and prints the it in useful format"""
    print("\nItem name: {}\nLevel: {}\tWorn: {} \tType: {} {} \tValue: {}"
          .format(item['ITEM_NAME'].upper(),item['LEVEL'],item['WORN'].upper(),item['ITEM_TYPE'].upper(),item['WEAPON_TYPE'].upper(),item['VALUE']))
    print("AC: {}\tDamage:{}".format(item['ARMOR_CLASS'],item['DAMAGE']))
    print("STR: {} INT: {} WIS: {} DEX: {} CON: {} CHA: LCK: {} HIT: {} DMG: {}"
          .format(item['STR'],item['INT'],item['WIS'],item['DEX'],item['CON'],item['CHA'],item['LCK'],item['HIT_ROLL'],item['DAMAGE_ROLL']))
    print("HP: {}\t MANA: {}".format(item['HP'], item['MANA']))
    print(f"AREA: {item['AREA']}\t MOB: {item['MOB']}")
    genres = ''
    for x in item['GENRES_ALLOWED']:
        genres += x + ' '
    races = ''
    for x in item['RACES_ALLOWED']:
        races += x + ' '
    print(f'RACES: {races.strip()} \tGENRES: {genres.strip()}')
    print(flatten_affects(item))

def print_web(item):
    """Show exactly what you get from the web"""
    print(item['HTTP_DESCRIPTION'])

def flatten_affects(item):
    """Longer listing of all affects"""
    af = item['AFFECTS_LIST']
    str = ''
    for key in af:
        str = str + key[0] + ' ' + key[1] + '; '
    return str

def format_affects(item):
    """Succinct list of affects to include in the pandas df - but available to items"""
    af = item['AFFECTS_LIST']
    str = format_affects_list(af)
    return str

def format_affects_list(af):
    """Succinct list of affects to include in the pandas df"""
    str = ''
    for key in af:
        words= re.findall(r"[\w']+", key[0])
        for word in words:
            str = str + word[0:3] + ' '
        str = str.strip() + ':' + key[1] + '; '
        #str = str + key[0] + ' ' + key[1] + '; '
    return str.strip().upper()

def grep_name(items, name, verbose=True):
    """Intial method for grepping the database"""
    matches = []
    for ix, item in enumerate(items):
        if name.lower() in item['ITEM_NAME'].lower():
            if verbose:
                print("\nMatch ID: {}".format(ix),end='')
                print_item(item)
            matches.append(ix)
    return matches

def grep_all(items, query_string, verbose=True, min_level=0, max_level=50, min_value=-10,area=''):
    """Intial method for grepping the database"""
    matches = []
    for ix, item in enumerate(items):
        for attrib in item:
            if (query_string.lower() in str(item[attrib]).lower()
                and min_level<=safe_int(item['LEVEL'],default_value=-1)<= max_level
                and item['VALUE']>= min_value) and area.lower() in item['AREA'].lower():
                if verbose:
                    print("\nMatch ID: {}".format(ix),end='')
                    print_item(item)
                matches.append(ix)
                break
    return matches

# -------- ITEM ATTRIBUTE PROCESSING SECTION -----------
# messed up and brought in a trailing '.' sometimes
def fix_tuples(item):
    """Fixer function because I originally brought in a trailing period on AFFECTS_LIST"""
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        i[1] = re.sub(r'\.', r'', i[1])
    return affects_list

def get_attribute(item,attribute):
    """Converts tuples to list and returns the value of an single attribute, e.g. 'damage roll' """
    allowed_attributes = ['damage roll', 'hp', 'hit roll', 'mana', 'dexterity', 'strength', 'armor class',
                          'wisdom', 'constitution', 'intelligence', 'luck', 'affected_by', 'charisma', 'moves',
                          'save vs spell', 'save vs breath', 'save vs paralysis', 'save vs poison', 'resistant:cold',
                          'hp regeneration', 'save vs rod', 'mana regeneration', 'resistant:magic', 'resistant:fire',
                          'resistant:poison', 'age', 'resistant:nonmagic', 'resistant:slash', 'carrying capacity',
                          'resistant:acid', 'resistant:unholy', 'resistant:drain', 'susceptible:fire',
                          'resistant:electricity', 'resistant:energy', 'damage vs evils', 'parry',
                          'damage vs devouts', 'susceptible:cold', 'resistant:charm', 'susceptible:holy',
                          'resistant:sleep', 'grip', 'second attack', 'susceptible:drain', 'damage vs undead',
                          'immune', 'cost of fireshield', 'resistant:blunt', 'damage vs dragons', 'backstab',
                          'mount', 'resistant:paralysis', 'susceptible:electricity', 'susceptible:pierce', 'blood',
                          'damage vs dragon', 'third attack', 'weight', 'susceptible:magic', 'susceptible:blunt',
                          'disarm', 'pick', 'resistant:pierce', 'wait time of mercuria', 'height',
                          'susceptible:poison', 'punch', 'damage of vindur gong', 'damage vs golem',
                          'susceptible:paralysis', 'damage of dorn nadur', 'cost of locate object', 'scan', 'peek']
    result = ""
    affects_list = [list(elem) for elem in item['AFFECTS_LIST']]
    for i in affects_list:
        if i[0] == attribute:
            result = i[1]
    return result
    #item['AFFECTS_LIST'] = affects_list

numeric_attributes = ['damage roll',  'hit roll',  'dexterity', 'strength', 'wisdom', 'constitution', 'intelligence', 'luck', 'charisma',
                          'save vs spell', 'save vs breath', 'save vs paralysis', 'save vs poison', 'save vs rod']
qualitative_attributes = ['armor class','affected_by','resistant:cold','resistant:magic', 'resistant:fire',
                          'resistant:poison', 'age', 'resistant:nonmagic', 'resistant:slash', 'carrying capacity',
                          'resistant:acid', 'resistant:unholy', 'resistant:drain', 'susceptible:fire',
                          'resistant:electricity', 'resistant:energy', 'damage vs evils', 'parry',
                          'damage vs devouts', 'susceptible:cold', 'resistant:charm', 'susceptible:holy',
                          'resistant:sleep', 'grip', 'second attack', 'susceptible:drain', 'damage vs undead',
                          'immune', 'cost of fireshield', 'resistant:blunt', 'damage vs dragons', 'backstab',
                          'mount', 'resistant:paralysis', 'susceptible:electricity', 'susceptible:pierce', 'blood',
                          'damage vs dragon', 'third attack', 'weight', 'susceptible:magic', 'susceptible:blunt',
                          'disarm', 'pick', 'resistant:pierce', 'wait time of mercuria', 'height',
                          'susceptible:poison', 'punch', 'damage of vindur gong', 'damage vs golem',
                          'susceptible:paralysis', 'damage of dorn nadur', 'cost of locate object', 'scan', 'peek','moves']
reduced_attributes = ['mana','hp']
regeneration_attributes = ['mana regeneration','hp regeneration']

def calculate_value(item,verbose=False):
    """Calculate an item value based on summing weighted attributes """
    affects = item['AFFECTS_LIST']
    value=0
    for affect in affects:
        if affect[0] in numeric_attributes:
            if 'save' in affect[0]:
                value += -1*safe_int_valuation(affect[1])
                if verbose:
                    print(f'adding numeric {-1*safe_int_valuation(affect[1])} from {affect[0]}')
            else:
                value += safe_int_valuation(affect[1])
                if verbose:
                    print(f'adding numeric {safe_int_valuation(affect[1])} from {affect[0]}')
        if affect[0] in qualitative_attributes:
            value += 1
            if verbose:
                print(f'adding qualitiatve 1 from {affect[0]} ({affect[1]})')
        if affect[0] in reduced_attributes:
            value += safe_int_valuation(affect[1])/10
            if verbose:
                print(f'adding reduced {safe_int_valuation(affect[1])/10} from {affect[0]} ({affect[1]})')
        if affect[0] in regeneration_attributes:
            value += safe_int_valuation(affect[1])/5
            if verbose:
                print(f'adding regen reduced {safe_int_valuation(affect[1])/5} from {affect[0]} ({affect[1]})')
    return value

def safe_int_valuation(object):
    """Try to deal with cases where the database passes us strings instead of ints"""
    value = 1
    try:
        value = int(object)
    except ValueError as verr:
        if len(re.findall(r"[\d']+", object)) > 0:
            value = int(re.findall(r"[\d']+", object)[0])
    return value

def safe_int(object, default_value=''):
    """Try to deal with cases where the database passes us strings instead of ints"""
    value = ''
    try:
        value = int(object)
    except ValueError as verr:
        value = default_value
    return value



# -------- PICKLE SECTION -----------
def save_db(items,outfile=''):
    """Save the database to pkl format"""
    if outfile == '':
        outfile = 'RoD_Database.pkl'
    with open(outfile, 'wb') as fp:
        pickle.dump(items, fp)

def load_db(infile=''):
    """Save the database to pkl format"""
    if infile == '':
        infile = 'RoD_Database.pkl'
    with open(infile, 'rb') as fp:
        items = pickle.load(fp)
    return items

# -------- PANDAS SECTION -----------
# columns for the pandas save
xcel_cols_old = ['ITEM_NAME','Area','LEVEL','ITEM_TYPE','WORN','AC','WEAPON_TYPE','AVERAGE_DAMAGE','VALUE','STR','INT',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','GLANCE_DESCRIPTION',
        'SPECIAL_PROPERTIES','WEIGHT','GOLD', 'AFFECTS_LIST', 'DAMAGE', 'Manufactured',
        'Minimum Level', 'Mob', 'Out of Game', 'Pop','Known Keywords','CATEGORIES',
        'GENRES_ALLOWED','ARMOR_CLASS','EXAM_DESCRIPTION','HTTP_DESCRIPTION']
xcel_cols = ['ITEM_NAME', 'AREA', 'LEVEL', 'ITEM_TYPE', 'WORN', 'AC', 'WEAPON_TYPE', 'AVERAGE_DAMAGE', 'VALUE','STR',
             'INT', 'WIS', 'DEX', 'CON', 'CHA', 'LCK', 'HP', 'MANA', 'HIT_ROLL', 'DAMAGE_ROLL', 'GLANCE_DESCRIPTION',
             'SPECIAL_PROPERTIES', 'WEIGHT', 'GOLD', 'AFFECTS_LIST', 'DAMAGE', 'MANUFACTURED',
             'MINIMUM_LEVEL', 'MOB', 'OUT_OF_GAME', 'POP', 'KNOWN_KEYWORDS', 'CATEGORIES',
             'GENRES_ALLOWED', 'RACES_ALLOWED', 'ARMOR_CLASS', 'EXAM_DESCRIPTION', 'HTTP_DESCRIPTION']

def make_pandas_df(items,errors='ignore'):
    """Make a dataframe and make sure the right strings can be treated as numbers"""
    df = pd.DataFrame(items)
    #order them
    df = df[xcel_cols]
    numerics = ['LEVEL','AC','AVERAGE_DAMAGE','STR','INT','VALUE',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','WEIGHT','GOLD','MINIMUM_LEVEL']
    for col in numerics:
       #for excel you want to ignore, but for using in python you need to coerce
       #df[col]= pd.to_numeric(df[col], errors='ignore')
       #df[col] = pd.to_numeric(df[col], errors='coerce')
       df[col] = pd.to_numeric(df[col], errors=errors)
    df['AFFECTS'] = df.AFFECTS_LIST.apply(format_affects_list)
    return df

def save_pd_to_excel(df,outfile='',sheet_name=''):
    """Make the excel file formatted so that I never have to touch it manually"""
    if outfile=='':
        outfile = 'RodDatabase.xlsx'
    if sheet_name=='':
        sheet_name = 'CJH RoD DB v0.1 06212019'
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    # add columns created explicitly for pandas and excel
    pandas_cols = xcel_cols.copy()
    pandas_cols.insert(22,'AFFECTS')
    df.to_excel(writer, sheet_name=sheet_name, columns=pandas_cols)
    worksheet = writer.sheets[sheet_name]
    # Change the column widths - my imposed default is the length of the column name's string
    col_names= ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y','Z',
                'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL','AM','AN']
    for s, col in zip(pandas_cols, col_names):
        #apprently you can't just give it a single column name - have to use 'B:B' when you mean 'B'
        worksheet.set_column(col+':'+col, len(s)+3)
    # Item name and maybe a few other are the only ones I'll make bigger than default
    worksheet.set_column('B:B', 42)
    worksheet.set_column('C:C', 35)
    writer.save()


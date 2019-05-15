import pandas as pd

from bs4 import BeautifulSoup

import selenium
from selenium import webdriver

from time import sleep


###### DEFINING THE FUNCTIONS TO COLLECT SPECIFIC PIECES OF THE HTML######
##########################################################################

def get_main_scope(soup_object):
    """
    Returns perfume name and gender, designer name, family/group of perfume. In that order
    
    Parameters: 
    -----------
    soup_object: html content, parsed with BeautifulSoup
    """
    #get perfume name and gender
    # function to get the name of the perfume
    name = soup_object.find('h1', {'style' : 'clear: left;'}).text.strip()
    
    # get designer, and perfume family
    main_scope = soup_object.find('p', {'style' : 'font-size: 12px;'})
    
    designer = main_scope.find('span', {'itemprop' : 'name'}).text.strip()
    try: 
        group = main_scope.find('span' ,{'style' : 'float:right;'}).find('a').text.strip()
    except: 
        group = 'NA'
    
    return name, designer, group

#--------------------------------------------------------------------------------
# making a function that returns a tuple of note, and dominancy:
def get_main_accords(soup_object):
    # grab the main accords piece
    accords = soup_object.find_all('div', {'style' : 'width: 130px; height: 20px; border: solid 1px #ffffff; border-top: none; position: relative; text-align: center; clear: both; padding: 0;'})
    
    notes = []
    for i in range(len(accords)):
        notes.append(accords[i].find('span', {'style' : 'position: relative; font-weight: bold; z-index: 60;'}).text.strip())

        
    # grab the dominance scale:
    accord_percentage = soup_object.find_all('div', {'style' : 'width: 130px; height: 20px; border: solid 1px #ffffff; border-top: none; position: relative; text-align: center; clear: both; padding: 0;'})
    
    # finding position
    for s in str(accord_percentage[1]).split(';'):
        if '/span' in s:
            position = str(accord_percentage[1]).split(';').index(s)
            
    
    # find percentages of the accords
    percentages = []
    for i in range(len(accord_percentage)):
        percentages.append( (str(accord_percentage[i]).split(';')[position].split(':')[1][:-2]) ) 
    
    # tuple them together
    results = list(zip(notes, percentages))
    
    return results

#-----------------------------------------------------------------------------------------
def get_votes(soup_object):
    """
    Returns three things:
    Total number of voters, Opinions, Purchase numbers. In this order
    You can index to get only what you want. Example: get_votes(soup)[1] will return Opinions (collective reviews).
    
    Parameters: 
    soup_object: BeautifulSoup object, requested and ready.
    """
    
    # grab votes piece
    votes = []
    for i in str(soup_object.find("div", {'id' : 'diagramresult'}))['style'].split(';'):
        if 'height' in i:
            votes.append(i.split(':')[1][:-2]) # [:-2] means take all but the last two characters, coz they are px
            
    # grab votes categories piece
    vote_categories = soup_object.find_all('div', {'class' : 'votecaption'})
    
    categories = []
    for v in range(len(vote_categories)):
        categories.append(vote_categories[v].text)
        
    
    # getting total number of voters
    num_voters = soup_object.find('b', {'id' : 'peopleD'}).text
    num_voters = int(num_voters)
    
    
    # getting other statistics: 
    stats = str(soup_object.find('span', {'style' : 'font-size: 10px;'}).text).split('  ')
    status = []
    status_number = []
    for sentence in stats:
        status.append(sentence.split(':')[0])
        status_number.append(sentence.split(':')[1][1:])
     
    status_full = list(zip(status, status_number))
    
    
            
    # tuple them together
    results = list(zip(categories, votes))
    
#     print(f"Total Voters: {num_voters}, Purchases: {status_full}")
    return num_voters, results, status_full

#-----------------------------------------------------------------------------
# making a synopsis and ratings function: 
def get_synopsis(soup_object):
    """
    This function returns the short perfume description, perfume review total out of 5 start, and total number of 
    voters. In that order. 
    
    Parameters: 
    -----------
    soup_object: the parsed html content.
    """
    # written short description 
    synopsis = soup_object.find('div', {'itemprop' : 'description'}).text.strip()
    
    # rating (out of 5)
    rating = soup_object.find('span', {'itemprop' : 'ratingValue'}).text.strip()
    
    # total number of voters
    num_voters = soup_object.find('span', {'itemprop' : 'ratingCount'}).text.strip() # also found from function get_votes(soup_object)[0] it's the first return
    
    return synopsis, rating, num_voters


# get all notes regardless if Top, Middle, or Base
# BELOW ANOTHER FUNCTION get_notes_class() THAT RETURNS EACH PART: TOP, MIDDLE, BASE independently
def get_all_notes(soup_object):
    """
    Returns a list of all the notes in a perfume; regardless whether it's a Top, Middle or Base note. 
    Usually, the first four are Top, the second four are Middle, and the all the rest are Base. (Make sure of this!)
    
    Parameters:
    -----------
    soup_object: parsed html content by BeautifulSoup
    """
    # grabbing the whole rectangle of notes
    pyramid = soup_object.find('div', {'style' : 'width: 230px; float: left; text-align: center; clear: left;'})
    
    # drilling down
    all_pyramid = pyramid.find_all('span', {'class' : 'rtgNote'})
    
    #drilling down to notes names
    notes = []
    for p in all_pyramid:
        notes.append(p.find('img')['bt-xtitle'])
        
    return notes

#-------------------------------------------------------------------------
def get_notes_class(soup_object):
    """
    Returns notes in each class independently. Returns Top, Middle, Base notes. In that order. 
    
    Parameters: 
    -----------
    soup_object: html content, parsed with BeautifulSoup
    """
    
    # get the notes box
    notes_box = soup_object.find('div', {'style' : 'width: 230px; float: left; text-align: center; clear: left;'})\
    .find_all('p')  # top notes is [0], middle is [1], and base is [2]
    
    # get each list section, to drill down on it
    top_section = notes_box[0].find_all('span', {'class' : 'rtgNote'})
    middle_section = notes_box[1].find_all('span', {'class' : 'rtgNote'})
    base_section = notes_box[2].find_all('span', {'class' : 'rtgNote'})
        
    # drilling down each notes section to get each note name:
    top_notes = []
    for t in top_section:
        top_notes.append(t.find('img')['bt-xtitle'])
        
    middle_notes = []
    for t in middle_section:
        middle_notes.append(t.find('img')['bt-xtitle'])
        
    base_notes = []
    for t in base_section:
        base_notes.append(t.find('img')['bt-xtitle'])
    
    return top_notes, middle_notes, base_notes


def get_long_sil(soup_object):
    """
    Returns a table of Longevity, and Sillage. In that order. 
    
    Parameters: 
    -----------
    soup_object: html content, parsed with BeautifulSoup
    """
    
    # Longevity table
    long_votes_table = soup_object.find('div', {'class' : 'longSilBox effect6'})\
    .find('table', {'class' : 'voteLS long'}).find('tbody').find_all('tr')
    
    # printing votes, and their count
    longevity_votes =[]
    for k in long_votes_table:
        longevity_votes.append(k.text.split('\n')[1:3])
    
    # making the numbers integers
    temp_long = [int(i[1]) for i in longevity_votes]
    temp_long_votes = [i[0] for i in longevity_votes]
    longevity_votes = list(zip(temp_long_votes, temp_long))
    
    
    # Sillage
    sil_1 = []
    sil_2 = []
    for s in soup_object.find('div', {'class' : 'divSil'}).find('table').find_all('tr'):
        sil_1.append(s.find('td', {'class' : 'ndSum'}).text.strip())
        sil_2.append(s.find('td').text.split('\n'))

    sil_1 = [int(i) for i in sil_1[1:] ]
    sil_2 = [i[0] for i in sil_2[1:] ]
    
    sillage_votes = list(zip(sil_2, sil_1))
        
    return longevity_votes, sillage_votes


#------------------------------------------------------------------------------------------------
def get_reviews(soup_object):
    """
    Returns the member id, and reviews text with the user name from each perfume's page. In that order.
    
    Parameters:
    ----------
    soup_object: html content, parsed by BeautifulSoup
    """
    # get the reviews section
    written_reviews_section = soup_object.find('div', {'xmlns' : 'http://www.w3.org/1999/html'})\
    .find_all('div', {'class':'pwq'})
    
    # get review text
    # Note: format is: user\n\n\n\ntext
    reviews = []
    for r in written_reviews_section:
        reviews.append(r.text.strip())
        
    member_id = []
    for member in written_reviews_section:
        member_id.append(member.find('a')['href'].split('/')[2])
        
    return member_id, reviews

#====================================================================================
# Alternative functions:
#------------------------

# alternative to get_notes_class()
def get_notes_class_alternative(soup_object):
    top_section = soup_object.find('div', 
                {'style' : 'width: 230px; float: left; text-align: center; clear: left;'})

    all_notes_alternative = []
    for sp in step_1.find_all('span'):
        all_notes_alternative.append(sp.find('img')['bt-xtitle']) # or ['alt'] at the end, both work


    return all_notes_alternative
                                         
                                         

#alternative to get_long_sil()
def get_main_accords_alternative(soup_object):
    
    main_accords_public = []
    for m in soup_object.find('div', {'id' : 'userMainNotes'}).find_all('img'):
        main_accords_public.append(m['alt'])
    
    return main_accords_public


def get_long_sil_alternative(soup_object):
    
    # for Longevity
    long_score_name = []
    long_score_value = []
    for k in soup_object.find('div', {'class' : 'divLong'}).find('tbody').find_all('tr'):
        long_score_name.append(k.find_all('td')[0].text.strip())
        long_score_value.append(k.find_all('td')[1].text.strip())

    # zip them together to print them
    long_scores = list(zip(long_score_name, long_score_value))
    
    # for Sillage
    sil_score_name = ['soft', 'moderate', 'heavy', 'enormous']
    sil_score_value = []
    for k in soup_object.find('div', {'class' : 'divSil'}).find_all('td', {'class' : 'ndSum'}):
        sil_score_value.append(k.text.strip())

    sil_scores = list(zip(sil_score_name, sil_score_value))
    
    return long_scores, sil_scores


def get_votes_alternative(soup_object):
    
    # have it/had it/want it/my signature 
    # get names, and values of these categories
    names = []
    values = []
    for k in soup_object.find_all('span', {'style' : 'font-size: 10px;'})[0].text.strip().split('  '):
        names.append(k.split(':')[0].strip())
        values.append(k.split(':')[1].strip())
   
    buying_votes = list(zip(names, values))
    
    
    # love/like/dislike, winter/spring/summer/fall, day/night
    
    opinions_percentage = []
    for k in BeautifulSoup.prettify((soup_object).find_all('div', {'id' : 'diagramresult'})[0]).split('height:')[2:]:
        opinions_percentage.append(k.split(';')[0].strip('px')) # divide this number by 100
        
    
    opinions = list(zip(['Love', 'Like', 'Dislike' 'Winter', 'Spring', 'Summer', 'Fall', 'Day', 'Night'], 
                       opinions_percentage))
    
    
    return buying_votes, opinions
######################################################################################
########## COLLECTING THE SOUP OBJECTS ##############################################
#################################################################################

def get_soups(links_list, local_driver):
    
    """
    Returns a list of soup objects for later find and use, handels for error 429 "Too Many Requests".
    MUST RUN `local_driver = webdriver.Chrome()` BEFORE running this function.
    
    Parameters:
    -----------
    links_list: a list of links that are healthy and ready to get.
    """
    
    from time import sleep
    
    soup_list = []
    for n, link in enumerate(links_list):
        local_driver.get(link)
        local_soup = BeautifulSoup(local_driver.page_source, 'lxml')
        
        
        if local_soup.find('h1').text == '429 Too Many Requests':
            the_429 = True
            
            while the_429: # means automatically true
                sleep(900) # sleep for 15 minutes
                local_driver.get(link)
                local_soup = BeautifulSoup(local_driver.page_source, 'lxml')
                if local_soup.find('h1').text != '429 Too Many Requests':
                    soup_list.append(local_soup)
                    the_429 = False

        
        else: 
            soup_list.append(local_soup)
            sleep(7)
            # to print which link I'm at, and what is it's index
            print(n)
            print(link)
            print('-----')

            
            
    return soup_list 

#------------------------------------------------------------------------------------
# this function was not used, and so not tested,
def prettify_save(soup_objects_list, output_file_name):
    """
    Saves the results of get_soup() function to a text file. 
    
    Parameters: 
    -----------
    soup_object_list: 
        list of BeautifulSoup objects to be saved to the text file
    output_file_name:
        entered as string with quotations and with extension .txt , used to name the output text file
        
    This function can work independent of the rest of the library. 
        
    Note: 
    Unique to Windows, open() needs argument: encoding = 'utf8' for it to work. 
    """
    
    prettified_soup = [BeautifulSoup.prettify(k) for k in soup_objects_list]
    custom_word_added = [m + 'BREAKHERE' for m in prettified_soup]
    one_string = "".join(custom_word_added)
    
    # unique to Windows, open() needs argument: encoding = "utf8"
    with open(output_file_name, 'w') as file:
        file.write(one_string)
        
    return None

###################################################################################################################
########### MAKING THE DATA FRAMES ###################################3
##########################################################

def make_reviews_df(one_prettified_soup):
    """
    Returns one data frame of the customer id, reviews, and few characteristics about the perfume.
    
    Parameters: 
    -----------
    one_prettified_soup:
        A prettified soup object. Example: the output list of the prettify_save() function above; could be read from a text file.
    
    """
    
    # preparing the soup_objects
    soup_object = BeautifulSoup(one_prettified_soup, 'lxml')
    
    # gathering the lists
    customer_id = get_reviews(soup_object)[0]
    review_text = get_reviews(soup_object)[1]

    perfume_name = get_main_scope(soup_object)[0]
    designer = get_main_scope(soup_object)[1]
    group = get_main_scope(soup_object)[2]
    
    try: 
        main_accords = get_main_accords(soup_object)
    except:
        main_accords = 'NA'
    
    all_notes = get_all_notes(soup_object)

    # make the initial df
    temp_df = pd.DataFrame({'customer-id' : customer_id, 'review_test' : review_text})
    
    # add the perfume characteristics to it, to pin down the review
    temp_df['perfume_name'] = perfume_name
    temp_df['designer'] = designer
    temp_df['perfume_group'] = group
    temp_df['main_accords'] = [main_accords for i in range(temp_df.shape[0])]
    temp_df['all_notes'] = [all_notes for i in range(temp_df.shape[0])] 
    # making copies of the list, otherwise pandas is trying to put it as a column, and raises lenght conflict
    
    return temp_df

#-------------------------------------------------------------------------------------------------------------

# from fragrantica_library.py file
def make_perfume_df(one_prettified_soup):

    """
    Returns one data frame of all the characteristics, and statistics of the perfume.
    
    Parameters: 
    -----------
    one_prettified_soup:
        A prettified soup object. Example: the output list of the prettify_save() function above; could be read from a text file.
    
    """
    
    # preparing the soup_objects
    soup_object = BeautifulSoup(one_prettified_soup, 'lxml')
    
    # gathering the lists
    perfume_name = get_main_scope(soup_object)[0]
    designer = get_main_scope(soup_object)[1]
    group = get_main_scope(soup_object)[2]
     

    try:
        main_accords = get_main_accords(soup_object)
    except:
        try: 
            main_accords = get_main_accords_alternative(soup_object)
        except:
            main_accords = 'NA'

    try: 
        top_notes = get_notes_class(soup_object)[0]
        middle_notes = get_notes_class(soup_object)[1]
        base_notes = get_notes_class(soup_object)[2]
    except:
        top_notes = 'NA'
        middle_notes = 'NA'
        base_notes = 'NA'

    try:
        all_notes = get_all_notes(soup_object)
    except: 
        all_notes = 'NA'

    try:     
        longevity = get_long_sil_alternative(soup_object)[0]
    except:
        longevity = 'NA'
    
    try:
        sillage = get_long_sil_alternative(soup_object)[1]
    except:
        sillage = 'NA'

    try: 
        synopsis = get_synopsis(soup_object)[0]
    except:
        synopsis = 'NA'
    
    try:
        rating = get_synopsis(soup_object)[1] #overall rating
    except:
        rating = 'NA'
    
    try:
        num_voters = get_synopsis(soup_object)[2]
    except:
        num_voters = 'NA'

    try: 
        opinions = get_votes_alternative(soup_object)[1]   
    except:
        opinions = 'NA'
        
    try:    
        purchases = get_votes_alternative(soup_object)[0]
    except:
        purchases = 'NA'

    
    # make the initial df
    temp_df_2 = pd.DataFrame({
            'perfume_name' : [perfume_name], 
            'designer' : [designer],
            'group' : [group],
            'main_accords' : [main_accords],
            'all_notes' : [all_notes], 
            'top_notes' : [top_notes],
            'middle_notes' : [middle_notes],
            'base_notes' : [base_notes],
            'longevity' : [longevity], 
            'sillage' : [sillage], 
            'synopsis' : [synopsis],
            'overall_rating' : [rating],
            'total_num_voters' : [num_voters],
            'opinions' : [opinions],
            'purchases' : [purchases]
        })
    # what matters to pandas is each list length. A list of length 1 could be ANY object! could be a dictionary or a 
    # list of lists or a list of dfs! (well maybe not the latter, don't know)  
    return temp_df_2

## CLEANING THE DATAFRAME
# ------------------------
import pandas as pd
df = pd.read_csv("../ready_files/random_500_reviews_df.csv")
df.drop(["designer", "perfume_group", "main_accords", "all_notes"], axis = 1, inplace = True)

df['perfume_name'] = df['perfume_name'].map(lambda x: x.strip())

df.rename(columns = {'review_test' : 'review', 
                     'customer-id' : 'customer_id'}, inplace = True)

# shuffling the dataframe, keeping it at its origianl size
df = df.sample(frac = 1)

# reset the indicies to start from zero
df.reset_index(col_level = 0, inplace = True)
df.drop('index', axis = 1, inplace = True)

# cleaning the reviews text
df['review'] = df['review'].map(lambda x: x[20:].strip().replace('\n',''))

# dropping all non-English reviews, as they cause information loss by having many neutral ones
from langdetect import detect 

non_eng_indicies = []
for review in df['review']:
    if detect(review[:90])!='en':
        non_eng_indicies.append(list(df.loc[df['review']==review, :].index)) #list of indicies of non-english reviews
        
non_eng_indicies_list = [] # to extract the list of lists above into one list of indicies
for k in non_eng_indicies:
    for i in k:
        non_eng_indicies_list.append(i)
        
df.drop(non_eng_indicies_list, inplace = True)

## VADER SENTIMENT ANALYSIS, TO CREATE THE RATINGS FOR EACH REVIEW
#---------------------------------------------------------------------

# !pip install vaderSentiment

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

Vader_sentiment = []
for v in df['review']:
    Vader_sentiment.append(analyser.polarity_scores(v)['compound']) # to get only the compound score
    
df['vader_sentiment'] = Vader_sentiment # sentiment is a float between -1 and 1, 0 is neutral

## EDA
#-------
import matplotlib.pyplot as plt

custom_stop_words = list(ENGLISH_STOP_WORDS) + ['just', 'perfume', 'fragrance', 'don', '10', 'think', 'note', '2018', '2013', 
                                               'fragrances', 'smells', 'smell', 'scent', '2017', 'feel', 'way', 'little', 
                                               'really', 'bottle', '2016', '2014', 'say', 'little', '2015', '2012']

def plot_words(df):
    """
    Enter the dataframe you want, get a barplot of the most 25 frequent words, according to CountVectorizer
    """
    
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, ENGLISH_STOP_WORDS
    cv = CountVectorizer(stop_words=custom_stop_words, min_df=.01)

    sparse_matrix = cv.fit_transform(df['review'])
    features_df = pd.DataFrame(sparse_matrix.todense(), 
                              columns = cv.get_feature_names())

    return features_df.sum().sort_values(ascending = False).head(25).plot(kind = 'barh', figsize = (8,8));


# What people mentioned the most (most frequent words) in each category pos/neg/neutral
pos_reviews_df = df.loc[df['vader_sentiment'] >0 ,: ]
neg_reviews_df = df.loc[df['vader_sentiment']<0 , :]
neutral_reviews_df = df.loc[df['vader_sentiment'] == 0, :]

# generate barplots for most frequent words in each dataframe
plot_words(df)
plot_words(pos_reviews_df)
plot_words(neg_reviews_df)

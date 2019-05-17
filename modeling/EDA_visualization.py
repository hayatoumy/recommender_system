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
df.reset_index(col_level = 0, drop = True ,inplace = True)

# cleaning the reviews text
df['review'] = df['review'].map(lambda x: x[20:].strip().replace('\n',''))


###
# dropping all non-English reviews, as they cause information loss by having many neutral ones
# keep only alphabetical words
def letters(string):
    import re
    return re.sub(r"[^A-Za-z]+", ' ', string) 

# executing the function letters()
review_list = []
for r in df['review']:
    review_list.append(letters(r))
    
df['review'] = review_list # replace with the only alphabet reviews

# get indicies of non-english reviews
def drop_non_eng(text_series):
    from langdetect import detect
    
    for r in text_series:
        if detect(r) != 'en':
            df.drop(df.loc[text_series == r, :].index, axis = 0, inplace = True)
    return df

from time import time 
t0 = time()
df = drop_non_eng(df['review']) # the core code
print(f"it takes {round( (time()-t0)/60 ,1)} minutes to drop non-English reviews")

   
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
%config InlineBackend.figure_format = 'retina'

def plot_words(df):
    """
    Enter the dataframe you want, get a barplot of the most 25 frequent words, according to CountVectorizer
    """
    
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, ENGLISH_STOP_WORDS
    
    custom_stop_words = list(ENGLISH_STOP_WORDS) + ['just', 'perfume', 'fragrance', 'don', 'think', 'note', 'notes', 
                                               'fragrances', 'smells', 'smell', 'scent', 'bottle']
    
    cv = CountVectorizer(stop_words=custom_stop_words, min_df=.01)

    sparse_matrix = cv.fit_transform(df['review'])
    features_df = pd.DataFrame(sparse_matrix.todense(), 
                              columns = cv.get_feature_names())

    return features_df.sum().sort_values(ascending = False).head(15).plot(kind = 'barh', figsize = (8,8));


# What people mentioned the most (most frequent words) in each category pos/neg/neutral
pos_reviews_df = df.loc[df['vader_sentiment'] >0 ,: ]
neg_reviews_df = df.loc[df['vader_sentiment']<0 , :]
neutral_reviews_df = df.loc[df['vader_sentiment'] == 0, :]

# generate barplots for most frequent words in each dataframe
plot_words(df);
plt.title('most used words'.title(), fontsize = 14);

plot_words(pos_reviews_df);
plt.title('most used words in positive reviews'.title(), fontsize = 14);

plot_words(neg_reviews_df);
plt.title('most used words in negative reviews'.title(), fontsize = 14);

plot_words(neutral_reviews_df);
plt.title('most used words in neutral reviews'.title(), fontsize = 14);


# average most liked and most hated 10 perfumes, according to reviewers
# positive
best_liked_10 = pos_reviews_df['vader_sentiment'].groupby(pos_reviews_df['perfume_name']).mean().sort_values(ascending = False)[:10].to_frame()
# negative
worst_hated_10 = neg_reviews_df['vader_sentiment'].groupby(neg_reviews_df['perfume_name']).mean().sort_values(ascending = False)[:10].to_frame()
# neutral
top_neutral_10 = neutral_reviews_df['vader_sentiment'].groupby(neutral_reviews_df['perfume_name']).mean().sort_values(ascending = False)[:10].to_frame()

best_liked_10.plot(kind = 'barh', title = 'most liked perfumes'.title());
worst_hated_10.plot(kind = 'barh', title = 'most hated perfumes'.title());
top_neutral_10.plot(kind = 'barh', title = 'most neutral perfumes'.title())

# most reviewed perfumes
most_reviewed_10 = df['perfume_name'].value_counts().sort_values(ascending = False)[:10]
most_reviewed_10.plot(kind = 'barh', title = 'most reviewed perfumes'.title());

# perfume_project

### The Problem Statement: 
When a user logs in to a fragrance website, print out a list of perfumes he/she might like, to try next. 

### Where These Recommendations Come From?
Based on the cosine similarities, find the most similar user to the logged-in user, find which perfumes the similar user have reviewed and liked, that the logged-in user have not tried out yet, and print those out. <br />
If the logged-in user turned out to be one of the biggest reviewers; that is, have tried a lot of perfumes, then the most similar user might have not tried as much, and so we will have an empty list of recommendations. If that happens, we will look for the most similar 3 perfumes for the top 3 perfumes liked by the logged-in user, and print out that list of 9 perfumes to try next. <br />
**Explanation** <br />
Why would I compare only to most similar user, and not the most three similar users or so? <br /> 
There's a valid point for using next most similar users, and I might do this to the model, while controlling for how many perfumes to recommend to not overwhelm the customer or lose credibility; but I was afraid this will give a long stretch for predictions that might not be relevant at that point; since it's cosine similarities, on top of sentiment analysis, based on Vader. 
And the logged-in user might end up hating it, and thus losing faith in our recommendations, and instead of being a feature, it'll become a nuisance. 
**Extension** <br />
Of course, when deploying this model to the fragrance website, recommendations should always include recent launched perfumes, and new arrivals. These perfumes, however, need to share the same notes in the most liked perfumes by the logged-in user, or other features, like wearability in a certain season, etc. <br />
This latter case has not been treated for in this project, and that would be its own project, or an extension to this one in the near future. 

### Mechanics: 
Find cosine similarities between users; and find cosine similarities between items. Make functions to search on the criteria mentioned above; then turn everything into very easy to use functions. <br />
**Note** <br /> 
The collected review texts didn't have ratings attached to them by users. Vader library was used to give a rating between -1 and 1 for sentiment analysis, that is, from negative, to neurtral, to positive. <br />
VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media, and works well on texts from other domains. [vaderSentiment GitHub](https://github.com/cjhutto/vaderSentiment) 

#### Other Mechanics to Be Attempted Next, or in Later Projects:
1. Manually label few hundreds or thousands reviews. Make a model to predict ratings for the rest of the reviews based on text analysis. Then run the cosine similarity recommenders again. <br />  Evaluate performance by field and content knowledge to assess goodness of recommendations.
2. Exploring how nueral networks for unspervised learning for text data can be implemented to group together similar reviews about each perfume, thus grouping together similar users. Can be done to items as well. 
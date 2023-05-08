

import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
# import tqdm
import time
# import openpyxl
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from textblob import TextBlob
# import textblob
import re
from tweepy import OAuthHandler
# import json
import tweepy
import pandas as pd
import streamlit as st
import warnings
warnings.filterwarnings("ignore")
# EDA Pkgs
# import plotly.graph_objects as go


# To Hide Warnings
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)
# Viz Pkgs
matplotlib.use('Agg')
# sns.set_style('darkgrid')


STYLE = """
<style>
img {
    max-width: 100%;
}
</style> """


def main():
    """ Common ML Dataset Explorer """
    # st.title("Live twitter Sentiment analysis")
    # st.subheader("Select a topic which you'd like to get the sentiment analysis on :")

    html_temp = """
	<div style="background-color:tomato;"><p style="color:white;font-size:40px;padding:9px">Live twitter Sentiment analysis</p></div>
	"""

    st.sidebar.title('Visualization Selector')

    select = st.sidebar.radio("Select analysis mode:",
                              ('#Hashtag', '@Twitter_Handle'))
    st.markdown(html_temp, unsafe_allow_html=True)

    st.sidebar.title('Popular Trends near you!')

    ################# Twitter API Connection #######################
    consumer_key = "HhvfC5DdrER4uqcoBauccRkBV"
    consumer_secret = "Xu0BVmS7qSyYPKv6eCOOxmOGPIMxvK33IBSxOne6FlJTnRSN4n"
    access_token = "621893422-a3Lr6g3dnp2xCvO30hYND4knZv2PdWNKU9JhZOPH"
    access_token_secret = "wY07uwrcPN8JAfbxKzXbsdpyF4ECEpLMmrZQvfnQPHz46"
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAJPfnAEAAAAAes7FhbZjY%2BDkVPgSX6KHzKgWu%2BU%3DuUYQnr6PHJg5rDw3HiYkQWBVrlrtSPhubUznxCOsqYB5aWy79e"
    # Use the above credentials to authenticate the API.

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
    ################################################################

    df = pd.DataFrame(
        columns=["Date", "User", "IsVerified", "Tweet", "Likes", "RT", 'User_location'])

    # Write a Function to extract tweets:
    def get_tweets(Topic, select, Count):
        i = 0
        if select == "@Twitter_Handle":
            # my_bar = st.progress(100) # To track progress of Extracted tweets
            for tweet in tweepy.Cursor(api.user_timeline, id=Topic).items():
                # time.sleep(0.1)
                # my_bar.progress(i)
                df.loc[i, "Date"] = tweet.created_at
                df.loc[i, "User"] = tweet.user.name
                df.loc[i, "IsVerified"] = tweet.user.verified
                df.loc[i, "Tweet"] = tweet.text
                df.loc[i, "Likes"] = tweet.favorite_count
                df.loc[i, "RT"] = tweet.retweet_count
                df.loc[i, "User_location"] = tweet.user.location
            # df.to_csv("TweetDataset.csv",index=False)
            # df.to_excel('{}.xlsx'.format("TweetDataset"),index=False)   ## Save as Excel
                i = i+1
                if i > Count:
                    break
                else:
                    pass
        elif select == "#Hashtag":
            for tweet in tweepy.Cursor(api.search, q=str(Topic), lang="en", tweet_mode='extended').items():
                # time.sleep(0.1)
                # my_bar.progress(i)
                df.loc[i, "Date"] = tweet.created_at
                df.loc[i, "User"] = tweet.user.name
                df.loc[i, "IsVerified"] = tweet.user.verified
                df.loc[i, "Tweet"] = tweet.full_text
                df.loc[i, "Likes"] = tweet.favorite_count
                df.loc[i, "RT"] = tweet.retweet_count
                df.loc[i, "User_location"] = tweet.user.location
            # df.to_csv("TweetDataset.csv",index=False)
            # df.to_excel('{}.xlsx'.format("TweetDataset"),index=False)   ## Save as Excel
                i = i+1
                if i > Count:
                    break
                else:
                    pass

    # Function to Clean the Tweet.
    def clean_tweet(tweet):
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([RT])', ' ', tweet.lower()).split())

    # Funciton to analyze Sentiment

    def analyze_sentiment(tweet):
        analysis = TextBlob(tweet)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'

    # Function to Pre-process data for Worlcloud
    def prepCloud(Topic_text, Topic):
        Topic = str(Topic).lower()
        Topic = ' '.join(re.sub('([^0-9A-Za-z \t])', ' ', Topic).split())
        Topic = re.split("\s+", str(Topic))
        stopwords = set(STOPWORDS)
        # Add our topic in Stopwords, so it doesnt appear in wordClous
        stopwords.update(Topic)
        ###
        text_new = " ".join(
            [txt for txt in Topic_text.split() if txt not in stopwords])
        return text_new

    #
    from PIL import Image

    image = Image.open('Logo1.jpg').convert('RGB')
    st.image(image, caption='Twitter for Analytics', use_column_width=True)

    st.subheader(
        "Select a topic which you'd like to get the sentiment analysis on :")
    # Collect Input from user :
    Topic = str()
    Topic = str(st.text_input(
        "Enter the topic you are interested in (Press Enter once done)"))
    # tags = api.trends_place(23424848)

   # trends1 = api.get_place_trends(23424977)
    trends1 = api.trends_place(23424977)

    hashtags = [x['name'] for x in trends1[0]['trends']]

    st.sidebar.write(hashtags[0:24])
    chart_visual = st.sidebar.selectbox(
        'Select Charts/Plot type', ('Line Chart', 'Bar Chart', 'Pie Chart', 'Bubble Chart', 'WordCloud'))

    if len(Topic) > 0:

        # Call the function to extract the data. pass the topic and filename you want the data to be stored in.
        with st.spinner("Please wait, Tweets are being extracted"):
            get_tweets(Topic, select, Count=200)
        st.success('Tweets have been Extracted !!!!')

        # Call function to get Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x: clean_tweet(x))

        # Call function to get the Sentiments
        df["Sentiment"] = df["Tweet"].apply(lambda x: analyze_sentiment(x))

        # Write Summary of the Tweets
        st.write("Total Tweets Extracted for Topic '{}' are : {}".format(
            Topic, len(df.Tweet)))
        st.write("Total Positive Tweets are : {}".format(
            len(df[df["Sentiment"] == "Positive"])))
        st.write("Total Negative Tweets are : {}".format(
            len(df[df["Sentiment"] == "Negative"])))
        st.write("Total Neutral Tweets are : {}".format(
            len(df[df["Sentiment"] == "Neutral"])))

        # See the Extracted Data :

        # st.markdown(html_temp, unsafe_allow_html=True)
        st.success("Below is the Extracted Data :")
        st.write(df.head(50))

        # get the countPlot
        if chart_visual == 'Bar Chart':
            st.success("Generating A Count Plot")
            st.subheader(" Count Plot for Different Sentiments")
            st.write(sns.countplot(df["Sentiment"]))
            st.pyplot()
            st.success(
                "Generating A Count Plot (Verified and unverified Users)")
            st.subheader(
                " Count Plot for Different Sentiments for Verified and unverified Users")
            st.write(sns.countplot(df["Sentiment"], hue=df.IsVerified))
            st.pyplot()

        # Piechart
        elif chart_visual == 'Pie Chart':
            st.success("Generating A Pie Chart")
            a = len(df[df["Sentiment"] == "Positive"])
            b = len(df[df["Sentiment"] == "Negative"])
            c = len(df[df["Sentiment"] == "Neutral"])
            d = np.array([a, b, c])
            explode = (0.1, 0.0, 0.1)
            st.write(plt.pie(d, shadow=True, explode=explode, labels=[
                     "Positive", "Negative", "Neutral"], autopct='%1.2f%%'))
            st.pyplot()

        # Create a Worlcloud
        elif chart_visual == 'WordCloud':
            selected_status = st.sidebar.selectbox('Select Sentiment Status', options=[
                                                   'All Tweets', 'Positive Tweets', 'Negative Tweets'])

            if selected_status == 'All Tweets':
                st.success(
                    "Generating A WordCloud for all things said about {}".format(Topic))
                text = " ".join(review for review in df.clean_tweet)
                stopwords = set(STOPWORDS)
                text_newALL = prepCloud(text, Topic)
                wordcloud = WordCloud(
                    stopwords=stopwords, max_words=800, max_font_size=70).generate(text_newALL)
                st.write(plt.imshow(wordcloud, interpolation='bilinear'))
                st.pyplot()

        # Wordcloud for Positive tweets only
            if selected_status == 'Positive Tweets':
                st.success(
                    "Generating A WordCloud for all Positive Tweets about {}".format(Topic))
                text_positive = " ".join(
                    review for review in df[df["Sentiment"] == "Positive"].clean_tweet)
                stopwords = set(STOPWORDS)
                text_new_positive = prepCloud(text_positive, Topic)
                # text_positive=" ".join([word for word in text_positive.split() if word not in stopwords])
                wordcloud = WordCloud(
                    stopwords=stopwords, max_words=800, max_font_size=70).generate(text_new_positive)
                st.write(plt.imshow(wordcloud, interpolation='bilinear'))
                st.pyplot()

        # Wordcloud for Negative tweets only
            if selected_status == 'Negative Tweets':
                st.success(
                    "Generating A WordCloud for all Negative Tweets about {}".format(Topic))
                text_negative = " ".join(
                    review for review in df[df["Sentiment"] == "Negative"].clean_tweet)
                stopwords = set(STOPWORDS)
                text_new_negative = prepCloud(text_negative, Topic)
                # text_negative=" ".join([word for word in text_negative.split() if word not in stopwords])
                wordcloud = WordCloud(
                    stopwords=stopwords, max_words=800, max_font_size=70).generate(text_new_negative)
                st.write(plt.imshow(wordcloud, interpolation='bilinear'))
                st.pyplot()

      # elif chart_visual == 'Bubble Chart':
      #      fig = go.Figure()
       #     fig.add_trace(go.Scatter(x=df["Sentiment"],y=len(df["Sentiment"]),mode='markers',marker_size=[40, 60, 80, 60, 40, 50], name='Formerly_Smoked'))

    st.sidebar.header("About App")
    st.sidebar.info("A Twitter Sentiment analysis Project which will extract tweets for the Twitter Handle or the topic selected by the user. The extracted tweets will then be processed and Sentiment Analysis will be performed on them to determine the Sentiments of those tweets. \
                    AS output,the various Visualizations will be displayed to help us understand the overall mood of the people on Twitter regarding the input provided by the user.")

    st.sidebar.header("Project Made By:")
    st.sidebar.info("Sarthak Ahir")
    st.sidebar.info("Dharmik Bhanushali")

    # st.sidebar.subheader("Scatter-plot setup")
    # box1 = st.sidebar.selectbox(label= "X axis", options = numeric_columns)
    # box2 = st.sidebar.selectbox(label="Y axis", options=numeric_columns)
    # sns.jointplot(x=box1, y= box2, data=df, kind = "reg", color= "red")
    # st.pyplot()

    if st.button("Exit"):
        st.balloons()


if __name__ == '__main__':
    main()

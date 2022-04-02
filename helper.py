from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):

    if selected_user != "Overall":
        df = df[df["users"] == selected_user]

    # fetch total messages
    num_messages = df.shape[0]

    # fetch total number of words
    words = []
    for message in df["messages"]:
        words.extend(message.split())
    
    # fetch total media files
    num_media_messages = df[df["messages"] == "<Media omitted>\n"].shape[0]

    # fetch total links shared
    links = []
    for message in df["messages"]:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df["users"].value_counts().head()
    df = round((df["users"].value_counts() / df.shape[0])*100, 2).reset_index().rename(columns={'index':'name', 'users':'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()

    f_h = open("stopwords_hindi.txt", "r", encoding="utf-8")
    stop_words_hindi = f_h.read()

    if selected_user != "Overall":
        df = df[df["users"] == selected_user]
    
    # remove group_notification
    temp = df[df["users"] != "group_notification"]
    # remove '<Media omitted>\n'
    temp = temp[temp["messages"] != "<Media omitted>\n"]

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words and word not in stop_words_hindi:
                y.append(word)
        return " ".join(y)
    
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp["messages"] = temp["messages"].apply(remove_stop_words)
    df_wc = wc.generate(temp["messages"].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):

    # hinglish stop words
    f = open("stop_hinglish.txt", "r")
    stop_words = f.read()

    # hindi stop words
    f_h = open("stopwords_hindi.txt", "r", encoding="utf-8")
    stop_words_hindi = f_h.read()

    if selected_user != "Overall":
        df = df[df["users"] == selected_user]
    
    # remove group_notification
    temp = df[df["users"] != "group_notification"]
    # remove '<Media omitted>\n'
    temp = temp[temp["messages"] != "<Media omitted>\n"]

    words = []

    for message in temp["messages"]:
        for word in message.lower().split():
            if word not in stop_words and word not in stop_words_hindi:
                words.append(word)

    most_common_words_df = pd.DataFrame(Counter(words).most_common(25)).rename(columns={0: "word", 1: "frequency"})
    return most_common_words_df


def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    emojis = []
    for message in df['messages']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    timeline = df.groupby(["year", "month_num", "month"]).count()["messages"].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline["month"][i] + "-" + str(timeline["year"][i]))
    
    timeline["time"] = time
    timeline.drop([0], inplace=True)

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    daily_timeline = df.groupby("only_date").count()["messages"].reset_index()
    daily_timeline.drop([0], inplace=True)

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    return df["day_name"].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    return df["month"].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)
    
    return user_heatmap

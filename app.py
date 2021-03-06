import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("fivethirtyeight")

st.sidebar.title("Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df["users"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show Analysis with respect to", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["messages"], color="#457b9d", linewidth=1) # color="green", linewidth=0.4
        ax.set_xticklabels(timeline["time"], fontsize=8)
        ax.set_ylabel("Message Frequency")
        plt.xticks(rotation="vertical")
        plt.tight_layout()
        st.pyplot(fig)


        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline["only_date"], daily_timeline["messages"], color="#457b9d", linewidth=0.4)
        plt.xticks(rotation="vertical")
        st.pyplot(fig)


        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color="#2b2d42", edgecolor='black')
            ax.set_ylabel("Message Frequency")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="#8d99ae", edgecolor='black')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        st.title("Weekly activity map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        # finding the busiest users in the group(Group level)
        if selected_user == "Overall":
            st.title("Most busy users")
            x, busy_percent_df = helper.most_busy_users(df)

            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.barh(x.index, x.values, color="#e63946", alpha=0.7, edgecolor='black')
                plt.xticks(rotation='vertical')
                plt.xlabel("Number of messages")
                st.pyplot(fig)
            with col2:
                st.dataframe(busy_percent_df)

        # WordCloud
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        most_common_words_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_words_df["word"], most_common_words_df["frequency"])
        plt.xticks(rotation="vertical")
        st.title("Most common words")
        st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            explode = [0, 0.1, 0.2, 0.3, 0.4]
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), explode=explode, shadow=True, autopct="%0.2f", wedgeprops={"edgecolor": "black"})
            st.pyplot(fig)

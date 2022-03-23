import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud , STOPWORDS
from model_results import run_model_get_results
import os

#creates wordcloud
def create_wordcloud(sub_data,count):
    sub_text = ' '.join(sub_data['comment'])
    # Create stopword
    stopwords = set(STOPWORDS)
    # Generate a word cloud image
    wordcloud = WordCloud(width = 3000, height = 1000, random_state=1, background_color='black', colormap='Set2', collocations=False, stopwords = STOPWORDS).generate(sub_text)
    # Display the generated image
    if count == 0:
        wordcloud.to_file("static/sub_cloud.png")
    else:
        address = "static/user_cloud_" + str(count) + ".png"
        wordcloud.to_file(address)

#transforms all the data into a user level dictonary and a subreddit level dictonary
def get_web_data(subname):
    
    print(os.getcwd())

    sub_level_dic = {}
    user_level_dic = {}

    main_data, filtered_5_data = run_model_get_results(subname)
    top_users = filtered_5_data["user"].value_counts()
    top_user_indices = list(top_users.index[:10])
    #top 10 users selected here

    main_data = main_data[main_data.user.isin(top_user_indices)]
    filtered_5_data = filtered_5_data[filtered_5_data.user.isin(top_user_indices)]

    #list of 10 closest subreddits
    closest_subreddits = main_data['subreddit'].value_counts()
    df_val_counts = pd.DataFrame(closest_subreddits)
    df_value_counts_reset = df_val_counts.reset_index()
    df_value_counts_reset.columns = ['sub_name', 'visits']
    df_value_counts_reset = df_value_counts_reset[df_value_counts_reset["sub_name"] != subname]
    df_10_closest_subs = df_value_counts_reset.head(10)
    total = df_10_closest_subs["visits"].sum()

    count=1
    temp_dic = {}
    for index, row in df_10_closest_subs.iterrows():
        dic = {
            'subname': row['sub_name'].display_name,
            'visits': row['visits'],
            'percentage': round(row['visits'] / total, 2),
        }

        temp_dic[count] = dic
        count += 1
    sub_level_dic["closesnt_subs"] = temp_dic
    create_wordcloud(main_data,0)
    sub_level_dic['wordcloud'] = 'sub_cloud.png'
    sub_level_dic['close_sub'] = df_10_closest_subs['sub_name'].values[0].display_name

    #getting user data
    count= 1
    for user in top_user_indices:
        single_user_info = user_data_processing(user,filtered_5_data,main_data,count)
        user_level_dic[count] = single_user_info
        count += 1

    user_level_dic['common_subs'] = common_subs(top_user_indices,main_data)

    user_data_dic = {}
    for key, value in user_level_dic.items():
      temp_dic = {}
      try :
        temp_dic['fav_sub']= value['fav_sub']
        temp_dic['user_prediction'] = value['user_prediction']
        temp_dic['real_aff']= value['real_aff']
        user_data_dic[key]=temp_dic
      except:
        pass

    sub_level_dic['user_info'] = user_data_dic
    right = 0
    left = 0
    for key, value in user_data_dic.items():
      right += value['user_prediction'][0]
      left += value['user_prediction'][1]
    right_final = round(right/10,2)
    left_final = round(left/10,2)
    unful = 100 -(right_final-left_final)
    sub_level_dic['pol_score']= [right_final,left_final,unful]

    return(sub_level_dic,user_level_dic)

def user_data_processing(user,filtered_5_data,main_data,count):

    dic_single = {}
    single_user = filtered_5_data[filtered_5_data.user == user]
    single_user_main = main_data[main_data.user == user]
    '''
    number_of_comments_made = len(single_user_main)
    user_text = ' '.join(single_user['comment'])
    user_word_count = len(user_text.split())
    print(int(user_word_count/number_of_comments_made))

    #unique words.
    unique_words = len(set(user_text.split()))
    print(unique_words)'''

    #user level prediction

    users_predictions = list(single_user['scores'])
    sum_right = 0
    sum_left = 0


    for entry in users_predictions:
      sum_right += entry[0]
      sum_left += entry[1]
    
    right_final = round((sum_right/(sum_right+sum_left))*100,2)
    left_final = round((sum_left/(sum_right+sum_left))*100, 2)
    unfulfil = 100 - (right_final+left_final)
    dic_single['user_prediction'] = [right_final,left_final,unfulfil]
    #user word_cloud

    create_wordcloud(single_user_main,count)
    dic_single["word_cloud"] = "user_cloud_" + str(count) + ".png"
    #user actual affliliation


    flair_types = [':auth: - AuthCenter', ':libright: - LibRight',
        ':libleft: - LibLeft', ':centrist: - Centrist',
        ':CENTG: - Centrist', ':authleft: - AuthLeft',
        ':authright: - AuthRight', ':right: - Right', ':left: - Left',
        ':lib: - LibCenter', ':libright2: - LibRight']

    user_aff = list(set(list(single_user_main.flair.unique())).intersection(flair_types))
    dic_single['real_aff'] = 'Unknown' if not user_aff else user_aff
        
    #how famous the user is on an subreddit

    subs = list(single_user_main.subreddit.unique())
    subscore = {}
    for sub in subs:
      temp_df = single_user_main.loc[single_user_main['subreddit'] == sub.display_name]
      upvote_score = temp_df.upvotes.sum()
      subscore[sub.display_name] = upvote_score

    sorted_score = sorted(subscore.items(), key=lambda item: item[1], reverse=True)
    top_10_best_subs = sorted_score[:10]
    dic_single['most_upvoted_subs'] = top_10_best_subs


    #user active subs 
    closest_subreddits = single_user_main['subreddit'].value_counts()
    df_val_counts = pd.DataFrame(closest_subreddits)
    df_value_counts_reset = df_val_counts.reset_index()
    df_value_counts_reset.columns = ['sub_name', 'visits']
    df_10_closest_subs = df_value_counts_reset.head(10)
    total = df_10_closest_subs["visits"].sum()



    temp_list = []
    for index, row in df_10_closest_subs.iterrows():
        dic = {
            'subname': row['sub_name'].display_name,
            'visits': row['visits'],
            'percentage': round(row['visits'] / total, 2),
        }

        temp_list.append(dic)
    dic_single['most_visited'] = temp_list
    dic_single['fav_sub'] = df_10_closest_subs['sub_name'].values[0].display_name
    return(dic_single)

#common subs between all our users:
def common_subs(top_user_indices,main_data):
    user_sub_dic ={}
    for user in top_user_indices:
      single_user_main = main_data[main_data.user == user]
      user_subs = list(single_user_main.subreddit.unique())
      user_sub_dic[user] = [sub.display_name for sub in user_subs]

    user_comm_dic = {}
    total_list = []
    for count, (key, value) in enumerate(user_sub_dic.items(), start=1):
        common_count_list = []
        for key_2,value_2 in user_sub_dic.items():
          if key == key_2 :
            continue
          common = set(value).intersection(value_2)
          common_count_list.append(len(common))
        user_comm_dic[count] = common_count_list
        total_list.append(len(value))
    user_comm_dic['total'] = total_list

    return(user_comm_dic)


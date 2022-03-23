import subprocess
import sys


# code to check and if unavailable download praw
try:
    import praw
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'praw'])
finally:
    import praw

import random
import pandas as pd



# Function connects to reddit and downloads all data
# input = subreddit Name
# return = pandas dataframe containing comments, subreddit names, upvotes , userflairs and user numbers
def get_reddit_data(sub_name):

    try :
        reddit = praw.Reddit(
            client_id="client id here ",
            client_secret="sec key",
            password="reddit password",
            user_agent="user afent name",
            username="username", check_for_async=False
        )
    except:
        return("error1")

    try:
        #select = ['year','day','hour','all','month','week']
        #random_choice = random.choice(select)
        user_list = [
            str(submission.author)
            for submission in reddit.subreddit(sub_name).top(
                'year', limit=15
            )
        ]

    except :
        return("error2")

    row_list = []
    for count, name in enumerate(user_list, start=1):
        try:
            for comment in reddit.redditor(name).comments.top("all",limit=None):
                row_dict = {
                    'comment': comment.body,
                    'subreddit': comment.subreddit,
                    'upvotes': comment.score,
                    'user': count,
                    'flair':comment.author_flair_text,
                }

                row_list.append(row_dict)  

        except:
            pass
    return pd.DataFrame(row_list)



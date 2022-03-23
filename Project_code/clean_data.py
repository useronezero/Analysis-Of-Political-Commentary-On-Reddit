import subprocess
import sys
import pip


# code to check and download any unavailable libraries.

pip.main(['install', 'unidecode'])

try:
    from cleantext import clean
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'clean-text'])
finally:
    from cleantext import clean

from user_data import get_reddit_data
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Function for lemmatization using POS tag
def lemmatize_words(text):
    
    lemmatizer = WordNetLemmatizer()
    wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV} # Pos tag, used Noun, Verb, Adjective and Adverb
    pos_tagged_text = nltk.pos_tag(text.split())
    return " ".join(
        lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN))
        for word, pos in pos_tagged_text
    )

def stopwords_removal(text):
    STOPWORDS = set(stopwords.words('english'))
    return " ".join(word for word in str(text).split() if word not in STOPWORDS)

def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

#using clean-text to lowercase and remove some irrelevnt data
def basic_cleaning(comment):
    return clean(comment,
        fix_unicode=True,               
        lower=True,                     
        no_line_breaks=True,           
        no_urls=True,                 
        no_emails=True,                
        no_phone_numbers=True,         
        no_numbers=True,              
        no_digits=True,                
        no_currency_symbols=True,
        no_punct=True,                      
        replace_with_punct="",          
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="",
        replace_with_number="",
        replace_with_digit="",
        replace_with_currency_symbol="",
        lang="en")
    

#function to perform cleaning
#input = subreddit name and data from user_data.py
#returns clean data
def data_cleaning(sub_name):
    
    userdata_df = get_reddit_data(sub_name)
    
    try :
        if userdata_df == 'error1':
            return 1
        elif userdata_df == 'error 2':
            return 2
    except: 
        pass
    
    userdata_df['comment'] = userdata_df['comment'].apply(basic_cleaning)
    
    userdata_df['comment'] = userdata_df['comment'].apply(remove_emoji)
    
    userdata_df['comment'] = userdata_df['comment'].apply(stopwords_removal)
    
    userdata_df['comment'] = userdata_df['comment'].apply(lemmatize_words)
    
    return(userdata_df)
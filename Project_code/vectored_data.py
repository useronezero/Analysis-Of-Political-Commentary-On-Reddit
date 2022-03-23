from clean_data import data_cleaning
import io
import numpy as np
import pandas as pd


#function to load vectors
def load_vectors(fname):
    embeddings_dict = {}
    with open(fname, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[word] = vector
    return(embeddings_dict)

#returns comments with 5 or more words
def atleast_5_words(clean_data):
    remove_5 = []
    for index,data in clean_data.iterrows():
        dic = {}
        comment = data['comment']
        if len(comment.split()) > 5:
            dic['comment'] = comment
            dic['subreddit'] = data['subreddit']
            dic['upvotes'] = data['upvotes']
            dic['user'] = data['user']
            remove_5.append(dic)
    return(pd.DataFrame(remove_5))

#forms word vectors
def vector_formation(subname):
    
    cleaned_data = data_cleaning(subname)

    cleaned_data_5 = atleast_5_words(cleaned_data)

    word_vectors = load_vectors("glove.twitter.27B.200d.txt")


    vectored_data = []
    for sentence in cleaned_data_5['comment']:
        vec_sentence = []
        for word in sentence.split():
            try:
                word_vec = word_vectors[word]
                word_vec = np.array(word_vec)
            except KeyError :
                word_vec = np.zeros(200)
                word_vec = word_vec.tolist()
            vec_sentence.append(word_vec)
        vectored_data.append(vec_sentence)


    for enc_sent in vectored_data:
        length = 30-(len(enc_sent)%30)
        if length > 25:
            length = 0
        pad = np.zeros((200))
        for _ in range(length):
            enc_sent.insert(0,pad)



    return(cleaned_data,cleaned_data_5,vectored_data)
    
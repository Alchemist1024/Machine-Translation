# import the necessary packages
import os
import pickle
import random

import keras.backend as K
import jieba
import numpy as np
from gensim.models import KeyedVectors

from config import stop_word, unknown_word, Tx, Ty, embedding_size, n_s
from config import valid_translation_folder, valid_translation_en_filename, valid_translation_zh_filename
from model import build_model

if __name__ == '__main__':
    channel = 3

    model_weights_path = 'models/model.01-83.7189.hdf5'
    model = build_model()
    model.load_weights(model_weights_path)

    print('loading CWV word embedding(zh)')
    word_vectors_zh = KeyedVectors.load_word2vec_format('data/sgns.merge.char')

    vocab_zh = pickle.load(open('data/vocab_train_zh.p', 'rb'))
    vocab_set_zh = set(vocab_zh)

    vocab_en = pickle.load(open('data/vocab_train_en.p', 'rb'))
    idx2word_en = vocab_en
    word2idx_en = dict(zip(idx2word_en, range(len(vocab_en))))

    print(model.summary())

    translation_path_en = os.path.join(valid_translation_folder, valid_translation_en_filename)
    translation_path_zh = os.path.join(valid_translation_folder, valid_translation_zh_filename)
    filename = 'data/samples_valid.p'

    print('loading valid texts and vocab')
    with open(translation_path_en, 'r') as f:
        data_en = f.readlines()

    with open(translation_path_zh, 'r') as f:
        data_zh = f.readlines()

    indices = range(len(data_en))

    length = 10
    samples = random.sample(indices, length)

    batch_x = np.zeros((length, Tx, embedding_size), np.float32)

    for i in range(length):
        idx = samples[i]
        sentence_zh = data_zh[idx]
        input_en = []
        seg_list = jieba.cut(sentence_zh)
        for j, token in enumerate(seg_list):
            if token in vocab_set_zh:
                word = token
            else:
                word = unknown_word
            batch_x[i, j] = word_vectors_zh[word]

        batch_x[i, j + 1] = word_vectors_zh[stop_word]

    s0 = np.zeros((length, n_s))
    c0 = np.zeros((length, n_s))
    preds = model.predict([batch_x, s0, c0])

    output_en = []
    for i in range(length):
        output = preds[i]
        for t in range(Ty):
            word_pred = idx2word_en[np.argmax(output)]
            output_en.append(word_pred)
            if word_pred == stop_word:
                break
        print(' '.join(output_en))

    K.clear_session()

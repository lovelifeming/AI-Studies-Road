#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/3/2/002 9:29
# @Author : zengsm
# @File : lstm-crf-ner

import codecs
import pickle
import sys

import numpy as np
import tensorflow as tf
from Batch import BatchGenerator
from bilstm_crf import Model
from utils import test_input, extraction, train

""" 参考《深度学习之实战TensorFlow入门》 第10章循环神经网络以及第三章到第八章的内容
    还要学习自然语言处理中文分词，词性标注与命名实体识别
    双向LSTM提取特征，提供给CRF模型进行实体识别
       tensorFlow 1.8 python 2.7    """

with open('../data/renmin.pkl', 'rb') as inp:
    word2id = pickle.load(inp)
    id2word = pickle.load(inp)
    tag2id = pickle.load(inp)
    id2tag = pickle.load(inp)
    x_train = pickle.load(inp)
    y_train = pickle.load(inp)
    x_test = pickle.load(inp)
    y_test = pickle.load(inp)
    x_valid = pickle.load(inp)
    y_valid = pickle.load(inp)

print("train len:", len(x_train))
print("test len:", len(x_test))
print("word2id len:", len(word2id))
print("Creating the data generator ...")
data_train = BatchGenerator(x_train, y_train, shuffle=True)
data_valid = BatchGenerator(x_valid, y_valid, shuffle=False)
data_test = BatchGenerator(x_test, y_test, shuffle=False)
print("Finished creating the data generator.")

epochs = 31
batch_size = 32

config = {'lr': 0.001, 'embedding_dim': 100, 'sen_len': len(x_train[0]), 'batch_size': batch_size,
          'embedding_size': len(word2id) + 1, 'tag_size': len(tag2id), 'pretrained': False}

embedding_pre = []
if len(sys.argv) == 2 and sys.argv[1] == 'pretrained':
    print("use pretrained embedding")
    config["pretrained"] = True
    word2vec = {}
    with codecs.open('vec.txt', 'r', 'utf-8') as input_data:
        for line in input_data.readlines():
            word2vec[line.split()[0]] = map(eval, line.split()[1:])
    unknow_pre = []
    unknow_pre.extend([1] * 100)
    embedding_pre.append(unknow_pre)
    for word in word2id:
        if word2vec.has_key(word):
            embedding_pre.append(word2vec[word])
        else:
            embedding_pre.append(unknow_pre)
    embedding_pre = np.asarray(embedding_pre)

if len(sys.argv) == 2 and sys.argv[1] == "test":
    print("begin to test...")
    model = Model(config, embedding_pre, dropout_keep=1)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        ckpt = tf.train.get_checkpoint_state('./model')
        if ckpt is None:
            print("Model not found,please train your model first")
        else:
            path = ckpt.model_checkpoint_path
            print('loading pre-trained model from %s......' % path)
            saver.restore(sess, path)
            test_input(model, sess, word2id, id2tag, batch_size)
elif len(sys.argv) == 3:
    print("begin to extraction...")
    model = Model(config, embedding_pre, dropout_keep=1)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        ckpt = tf.train.get_checkpoint_state('./model')
        if ckpt is None:
            print("Model not found,please train your model first")
        else:
            path = ckpt.model_checkpoint_path
            print('loading pre-trained model from %s......' % path)
            saver.restore(sess, path)
            extraction(sys.argv[1], sys.argv[2], model, sess, word2id, id2tag, batch_size)
else:
    print("begin to train...")
    model = Model(config, embedding_pre, dropout_keep=0.5)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        train(model, sess, saver, epochs, batch_size, data_train, data_test, id2word, id2tag)

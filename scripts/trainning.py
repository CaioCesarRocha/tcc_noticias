import gensim, os, json
from gensim.corpora import Dictionary
from gensim.models import TfidfModel, LsiModel
from gensim import corpora, similarities
from handling import DataProcess

BASEDIR = os.getcwd()
FILTER_ONE_WEEK = 7

notices = []

DataProcess.open_file('../G1Initial.jl', notices)
DataProcess.open_file('../IG_Initial.jl', notices)
DataProcess.open_file('../Terra_Initial.jl', notices)
DataProcess.open_file('../UolInitial.jl', notices)

notices = list(filter(lambda x: DataProcess.date_filter(x['data']) <= FILTER_ONE_WEEK , notices))
notices = sorted(notices, key = lambda x: x['data'],reverse=True)

docts = []

docts.extend(notice['corpo'] for notice in notices)

dictionary = Dictionary(docts)
BoW = [dictionary.doc2bow(doct) for doct in docts]

model_tfidf = TfidfModel(BoW)
vector_tfidf = model_tfidf[BoW]

lsi = LsiModel(vector_tfidf, id2word=dictionary, num_topics=300)

index = similarities.Similarity(BASEDIR+"/index", lsi[BoW], num_features=len(dictionary), num_best=10)

dictionary.save(BASEDIR+"/notices_dict.dict")
corpora.MmCorpus.serialize(BASEDIR+"/notices_BoW.mm", BoW)
lsi.save(BASEDIR+"/model_lsi.lsi")
index.save(BASEDIR+"/model_similarity.index")


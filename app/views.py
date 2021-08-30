from django.shortcuts import render
from django.http import JsonResponse
#Forbidden (CSRF token missing or incorrect.) Serve para nao ser necessário o token
from django.views.decorators.csrf import csrf_exempt  
#Transforms a function decorator into a method decorator so it can be used in an instance method.
from django.utils.decorators import method_decorator 
from django.conf import settings

#Imports to run the models similarities
import sys, gensim, nltk, os, json, re, pymongo, time
from gensim import corpora,similarities
from gensim.corpora import Dictionary
from gensim.models import TfidfModel, LsiModel
from datetime import date, datetime
from app.scripts.handling import DataProcess

#Imports to run the worker with redis
from rq import Queue
from worker import conn
from redis import Redis
from rq.job import Job


#CONNECTION MONGO_DB
#MONGO_URI = "localhost"
MONGO_DATABASE = "crawler"
url_mongo = os.environ['MONGODB_URI']
client = pymongo.MongoClient(url_mongo)
db = client[MONGO_DATABASE]
collection_notice = 'notices_collection'
collection_rating = 'notices_rating'


BASEDIR = os.getcwd() #make the path of api
notices, doct_noticeBase = [],[]
format="%d/%m/%Y"


def process_results(results):
	result_final = []
	for result in results:
		title = result[0] + "."

		link = result[1]	
		if (re.search("g1.globo.com",link)):
			picture = "globo"
		elif(re.search("terra.com.br",link)):
			picture = "terra"
		elif(re.search("uol.com.br",link)):
			picture = "uol"
		elif(re.search("ig.com.br",link)):
			picture = "ig"

		data = result[2]
		data = data.strftime('%d/%m/%Y')

		result_final.append({"title": title, "link": link, "data": data, "picture": picture})
	return result_final


def process_models(notices, body, link):
	link = link
	docts = list(map(lambda x: x['corpo'] , notices))
	dictionary = Dictionary(docts)
	BoW = [dictionary.doc2bow(doct) for doct in docts]

	model_tfidf = TfidfModel(BoW)
	vector_tfidf = model_tfidf[BoW]

	lsi = LsiModel(vector_tfidf, id2word=dictionary, num_topics=200)
	index = similarities.Similarity(BASEDIR+"/index", lsi[BoW], num_features=len(dictionary), num_best=8)
	
	doct_noticeBase = body
	BoW_notice = [dictionary.doc2bow(doct_noticeBase) for doct in doct_noticeBase]

	vector_lsi = lsi[BoW_notice[0]]

	sims = index[vector_lsi]
	print(sims)
	results = []
	for sim in sims:
		if sim[1] > 0.55:
			try:
				results.append([notices[sim[0]]['title'],notices[sim[0]]['link'],notices[sim[0]]['data']])
			except:
				pass
	
	if(results[0][1] == link):
		results.pop(0)
	if(len(results) >= 1):
		results = process_results(results)
		return results		
	else:
		results = 404 #NOTHING FOUND
		return results

def process_notice(url_base):
	url = url_base

	if(os.path.exists(BASEDIR+"/notice_base.jl")):
		os.remove("notice_base.jl")
	#Make the file notice_base
	if (re.search("g1.globo.com",url)):
		os.system("scrapy crawl G1NoticeBase -a notice_base=%s -o notice_base.jl"%url)
	elif(re.search("terra.com.br",url)):
		os.system("scrapy crawl TerraNoticeBase -a notice_base=%s -o notice_base.jl"%url)		
	elif(re.search("uol.com.br",url)):
		os.system("scrapy crawl UolNoticeBase -a notice_base=%s -o notice_base.jl"%url)
	elif(re.search("ig.com.br",url)):
		os.system("scrapy crawl IGNoticeBase -a notice_base=%s -o notice_base.jl"%url)

	with open('notice_base.jl','r') as file:
		for line in file:
			notice_base = json.loads(line)
			corpo = notice_base['corpo']
			data = notice_base['data']
			
	results = find_range_notices(data, corpo, url)
	return results



def find_range_notices(data, corpo, url):
	date = data
	date = datetime.strptime(date,format).date()
	body = corpo
	link = url

	#Make the range dates(Start and End to filter notices in the mongo)	
	start = DataProcess.date_start(date)
	end = DataProcess.date_end(date)
	#Get news from the Mongo that are within the defined range
	notices = db[collection_notice].find({"data":{"$gt": start,"$lt": end}})
	notices = [notice for notice in notices]

	results = process_models(notices, body, link)
	return results


def try_find_url(url_base):
	url = url_base
	try:
		bases = db[collection_notice].find({"link": url})
		base = [base for base in bases]
		data = list(map(lambda x: x['data'], base))
		data = data[0].strftime('%d/%m/%Y')
		corpo = list(map(lambda x: x['corpo'], base))
		corpo = corpo[0]
		results = find_range_notices(data, corpo, url)
		return results
	except:
		results = process_notice(url)
		return results


def process_url(url_base):
	url = url_base
	if ((re.search("g1.globo.com",url)) or (re.search("terra.com.br",url)) or (re.search("uol.com.br",url)) or (re.search("ig.com.br",url))):
		q = Queue(connection=conn)		
		results = q.enqueue(try_find_url, url, job_id='worker_sims')
		results = 205
		return results
	else:
		results = 400
	return results


@method_decorator(csrf_exempt, name='dispatch')
def get_url_base(request):
	#print('Request received from client')
	if request.method == 'POST':
		json_array = json.loads(request.body)
		for obj in json_array:
		    url_base = obj['url']
		
		# call the function to process the notice from your url
		results = process_url(url_base)

		# send data to client (json_array, safe=False)
		return JsonResponse(results, safe=False)
	elif request.method == 'GET':
		results = get_worker_results()		
		return JsonResponse(results, safe=False)
	else:
		return JsonResponse({'message': 'Server received GET request', 'status': 'GET'})


def get_worker_results():
	job = Job.fetch('worker_sims', connection=conn)
	status = job.get_status()
	print(status)
	if(status == "started"):
		results = 1
		return results
	elif(status == "finished"):
		job.refresh()
		results = job.result

		return results

def set_rates(rate,_id, numVotos, rate_actual, rate_one, rate_two, rate_tree, rate_four):
	rate_total = 0
	rate_total = rate_actual * numVotos
	numVotos = numVotos + 1
	new_rate = (float(rate_total) + float(rate))/ numVotos
	new_rate = round(new_rate,2)

	try:
		if(rate == "1"):
			rate_one = rate_one + 1
			db[collection_rating].update_one({'_id': _id}, {'$set': {'rate_average': new_rate, 'numVotos': numVotos, 'rate_one': rate_one}},upsert=False)
		elif(rate == "2"):
			rate_two = rate_two + 1
			db[collection_rating].update_one({'_id': _id}, {'$set': {'rate_average': new_rate, 'numVotos': numVotos, 'rate_two': rate_two}},upsert=False)
		elif(rate == "3"):
			rate_tree = rate_tree + 1
			db[collection_rating].update_one({'_id': _id}, {'$set': {'rate_average': new_rate, 'numVotos': numVotos, 'rate_tree': rate_tree}},upsert=False)
		else:
			rate_four = rate_four + 1
			db[collection_rating].update_one({'_id': _id}, {'$set': {'rate_average': new_rate, 'numVotos': numVotos, 'rate_four': rate_four}},upsert=False)
		result = 200
		return result
	except:
		print("error_set_rate")
		result = 500
		return result

def get_actual_rates(rate,notice_id, link):
	rate = rate
	_id = notice_id
	link = link
	
	try:
		rates = db[collection_rating].find({"_id": _id})
		rates = [rate_actual for rate_actual in rates]
		rate_actual = list(map(lambda x: x['rate_average'] , rates))
		rate_actual = rate_actual[0]
		numVotos = list(map(lambda x: x['numVotos'] , rates))
		numVotos = numVotos[0]
		rate_one = list(map(lambda x: x['rate_one'] , rates))
		rate_one = rate_one[0]
		rate_two = list(map(lambda x: x['rate_two'] , rates))
		rate_two = rate_two[0]
		rate_tree = list(map(lambda x: x['rate_tree'] , rates))
		rate_tree = rate_tree[0]
		rate_four = list(map(lambda x: x['rate_four'] , rates))
		rate_four = rate_four[0]

		insert = set_rates(rate,_id, numVotos, rate_actual, rate_one, rate_two, rate_tree, rate_four)
		return insert
	except:
		if(rate == "1"):
			db[collection_rating].insert({"numVotos": 1, "rate_average": rate, "link": link, "rate_one": 1, "rate_two": 0, "rate_tree": 0, "rate_four": 0})
		elif(rate == "2"):
			db[collection_rating].insert({"numVotos": 1, "rate_average": rate, "link": link, "rate_one": 0, "rate_two": 1, "rate_tree": 0, "rate_four": 0})
		elif(rate == "3"):
			db[collection_rating].insert({"numVotos": 1, "rate_average": rate, "link": link, "rate_one": 0, "rate_two": 0, "rate_tree": 1, "rate_four": 0})
		else:
			db[collection_rating].insert({"numVotos": 1, "rate_average": rate, "link": link, "rate_one": 0, "rate_two": 0, "rate_tree": 0, "rate_four": 1})
			result = 200
			return result
	

def get_id_notice(url, rate):		
	link = url
	rate = rate
	notices = db[collection_rating].find({"link": link})
	notice = [notice for notice in notices]
	notice_id = list(map(lambda x: x['_id'], notice))
	if(notice_id == []):
		notice_id = False
	else:
		notice_id = notice_id[0]
	
	insert = get_actual_rates(rate, notice_id, link)
	return insert


#function initial to post the notices rate
@method_decorator(csrf_exempt, name='dispatch')
def post_rating(request):
	if request.method == 'POST':
		json_array = json.loads(request.body)

		for obj in json_array:
		    rate = obj['rate']
		    url = obj['url']
		
		insert = get_id_notice(url, rate)

		return JsonResponse(insert, safe=False)
	else:
		return JsonResponse({'message': 'Post not habilited', 'status': 'POST'})

        
        

        
		
	
		


        
        
        
    
       
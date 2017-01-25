#---------import statements---------#
import requests
import json
import rauth
import wikipedia
import matplotlib.pyplot as plt
import numpy as np
import unittest

CACHE_FNAME = 'data_cache.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def get_search_parameters1(location, term,radius,limit):
	params = {}
	params["location"] = "{}".format(location)
	params["term"] = term
	params["radius_filter"] = radius
	params["limit"] = limit
	return params

def get_results(params):
	#Obtained the following in Manage API Access on yelp's dev site for YELP v2
	consumer_key = "Qz2STkU1QtjD1NtBENRZvg"
	consumer_secret = "_wZOEYfURwsZCJUeL7xPInB__Ms"
	token = "0MJs5Nckqs6Zle2UG40IGsOYHX5PadVQ"
	token_secret = "i1PcGRfqBgH3ALmhdiStNU_85OM"
	session = rauth.OAuth1Session(consumer_key = consumer_key,consumer_secret = consumer_secret,access_token = token,access_token_secret = token_secret) #<class 'rauth.session.OAuth1Session'>
	base_url="http://api.yelp.com/v2/search"
	
	request = session.get(base_url,params=params) #<class 'requests.models.Response'>

	data = request.json() #dictionary
	return data


def get_search_parameters2(origin, destination,travel_mode):
	params = {}
	params["units"] = "imperial"
	params["origins"] = origin
	params["destinations"] = destination
	params["mode"]=travel_mode
	if travel_mode=="transit":
		params["transit_mode"]=raw_input("Which transit mode do you want to take, bus or train? ")
	params["key"] = "AIzaSyDDemzLMU_dUb68V1MZpJ6jQbjFahSKRvY"
	return params

def canonical_order(d):
	res=[]
	for k in sorted(d.keys()):
		res.append((k, d[k]))
	return res

def requestURL(baseurl, params = {}):
    req = requests.Request(method = 'GET', url = baseurl, params = canonical_order(params))
    prepped = req.prepare()
    return prepped.url


#-------------Class Definition----------------#

class Yelp():
    def __init__(self, yelp_dict={}):
        self.rating=yelp_dict["rating"]
        self.name=yelp_dict["name"]
        self.phone=yelp_dict["phone"]
        self.url=yelp_dict["url"]
        self.review_count=yelp_dict["review_count"]
        self.location=yelp_dict["location"]["display_address"]

    def ratings(self):
    	return self.rating*self.review_count

    def address(self):
    	address=""
    	for add in self.location:
    		address=address+add+ ' '
    	return str(address)


class Google():
	def __init__(self, google_dict={}):
		self.duration=google_dict["rows"][0]["elements"][0]["duration"]['text']
		self.distance=google_dict["rows"][0]["elements"][0]["distance"]['text']
		self.origin=str(google_dict["origin_addresses"][0])
		self.destination=str(google_dict["destination_addresses"][0])
		self.duration_value=google_dict["rows"][0]["elements"][0]["duration"]['value']
		
	def location_check(self):
		if self.origin==self.destination:
			print "Error | Please check origin and destination"
			exit()
		else:
			return "You are all good" 

	def wiki_search(self):
		city=str(self.destination.split(',')[:1])
		print "\n"
		return wikipedia.summary(city)

	def time(self):
		return "{} is {} away and you will need approximately {} to reach there".format((self.destination), self.distance, self.duration)


origin_location=raw_input("Where are you currently? ")
destination_location=raw_input("Where do you want to go? ")
mode=raw_input("How do you want to travel, driving or transit? ")

base_url2="https://maps.googleapis.com/maps/api/distancematrix/json"

params2= get_search_parameters2(origin_location, destination_location,mode)


if requestURL(base_url2,params2) in CACHE_DICTION:
    print '...Using cached Google data...'
    google_cache = CACHE_DICTION[requestURL(base_url2,params2)] # use stored response
else:
	print '...Fetching data from Google...'
	r=requests.get(base_url2, params=params2)	#requesting data from Google
	CACHE_DICTION[requestURL(base_url2,params2)]=r.json()
	google_cache=CACHE_DICTION[requestURL(base_url2,params2)]

try:
	google_insts=Google(google_cache)
except:
	print "Check input"
	exit()

print google_insts.location_check()
print google_insts.time()

flag=int(raw_input("Do you want to know more about the city? Press 1 for yes, 0 for No: "))
if (flag==1):
	try:
		print google_insts.wiki_search()
	except:
		print "No page exists"

flag2=int(raw_input("\nDo you want to continue further? Press 1 to continue, 0 to exit: "))
if (flag2==0):
	exit()


parameters_str =raw_input("\nEnter type of place, area radius and the number of results you want to search for, separated by commas: ")
parameters_list=parameters_str.split(',')

base_url="http://api.yelp.com/v2/search"
params=get_search_parameters1(destination_location, parameters_list[0], int(parameters_list[1]), int(parameters_list[2]))


if requestURL(base_url,params) in CACHE_DICTION:
    print '...Using cached Yelp data...' 
    yelp_cache = CACHE_DICTION[requestURL(base_url,params)] # use stored response
else:
	print '...Fetching data from Yelp...'
	CACHE_DICTION[requestURL(base_url,params)]=get_results(params) #requesting data from Yelp
	yelp_cache=CACHE_DICTION[requestURL(base_url,params)]
	cache_file = open(CACHE_FNAME, 'w')
	cache_file.write(json.dumps(CACHE_DICTION))
	cache_file.close()

yelp_insts=[Yelp(x) for x in yelp_cache["businesses"]] #list comprehension


 #-------------Plotting----------------#

def plot(instance_list):
	name_list=[]
	rating_list=[]
	name_rating={}
	for instance in instance_list:
		name_rating[instance.name]=instance.ratings()

	name_list= sorted(name_rating.keys(), key=lambda k:  name_rating[k]) #sorting
	for name in name_list:
		rating_list.append(name_rating[name])

	plt.rcdefaults()
	y_pos = np.arange(len(name_list))
	plt.barh(y_pos, rating_list, align='center', alpha=0.8) #plotting data
	plt.yticks(y_pos, name_list)
	plt.xlabel('Reviews x Ratings')	
	plt.title('Recommendation')
	plt.show()


#------------output to csv-----------#

new_file = open("data.csv", 'w')
new_file.write ('NAME, RATING, REVIEWS, CONTACT NUMBER, ADDRESS, AREA CODE\n')
for instance in yelp_insts:
    new_file.write(instance.name + ',' + str(instance.rating)+ ',' + str(instance.review_count)+ ',' + str(instance.phone) +  ',' + instance.address() + '\n')

print "Here are the recommendations\n"

plot(yelp_insts)


#-------------------TESTS--------------------#
class Tests(unittest.TestCase):

	def testforparams1(self):
		self.assertEqual(type(params), type({'a':1,'b':2}), "testing type of parameters")

	def testforparams2(self):
		self.assertEqual(type(params2), type({'a':1,'b':2}), "testing type of parameters")
		
	def testforyelpdict(self):
		self.assertEqual(type(yelp_cache), type({'a':1,'b':2}), "testing type of parameters")

	def testforgoogledict(self):
		self.assertEqual(type(google_cache), type({'a':1,'b':2}), "testing type of parameters")	

	def testforlocation(self):
		self.assertEqual(type(google_insts.location_check()), type("Hello World"), "testing type of parameters")	

	def testforlenparams2(self):
		self.assertEqual(len(params2), 5, "testing len of parameters")
		
	def testforyelpinstance(self):
		self.assertEqual(type(yelp_insts),type(['3','4','5']), "testing type of instances")

	def testforgoogleinstance(self):
		self.assertEqual(type(yelp_insts[0]),type(google_insts), "testing type of instances")

	def testforyelprating(self):
		self.assertEqual(type(yelp_insts[0].rating),type(3.5), "testing type of instances")

	def testforinput(self):
		self.assertEqual(type(origin_location), type("Hello World"), "testing type of wikipedia result")

	def testforparamterslist(self):
		self.assertEqual(len(parameters_list), 3, "testing length of parameters list")


unittest.main(verbosity=2)












from utils import *
import argparse,time
from multiprocessing import Process
import random
import json,os
from bs4 import BeautifulSoup
from urllib.request import urlopen,urlparse

patterns = {
	"https://www.pledge.to/organizations":{
		"link":"a.featured-fundraiser-link",
		"name":"h1.h3",
		"address":"span.h-card.vcard",
		"causes":"ul.list-inline.text-center a",
		"country":"ul.list-inline.text-center a",
		"state":"abbr.p-region",
		"website":"li.px-1.px-sm-2 a",
		"mission":"section.mb-5 p",
		"description":"section.mb-5 div",
		"gross":"p.mt-3.mb-0.text-muted.text-nowrap b",
		"bg":"div.embed-responsive-item.bg-white.bg-cover.featured-fundraiser-image",
		"logo":"div.h-100.d-flex.flex-column img[src]",
		"next-page":"",
		"end":["h1","We're sorry, but something went wrong."],
		"year":"year"
		
	}
}


##fetch the remote resource from the given, can change user-agent
## if supplied
def fetch_resource(url,user_agent=None):
	try:
		response = requests.get(url,headers={"user-agent":user_agent},timeout=10.0,allow_redirects=True)
	except Exception:
		print("failed to fetch => {}".format(url))
		return None
	else:
		return BeautifulSoup(response.content,"lxml")


def get_contact(url):
	print(url,"get_contact")
	results = []
	bs = fetch_resource(url,USER_AGENTS[0])
	if not bs: return ['','','']
	text = bs.get_text()
	reg_type = re.search("\d{3}\([a-zA-Z0-9]+\)\d",text)
	email = re.search("[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+",text)
	phone = re.search("\(\d{3}\)\s*\d{3}-\d{4}",text) 
	return [reg_type.group(0) if reg_type else '',
         email.group(0) if email else '',
         phone.group(0) if phone else '' ]


#get date and month
def get_date_month(string):
	date = re.search("\s+(\d{2}),\s+\d{4}",string)
	month = re.search("\s+([a-zA-Z]+)\s+\d{2},\s+\d{4}",string)
	return date.group(1) if date else '',month.group(1) if month else ''

#rename picture
def rename_images(name,url):
	ext = url.split(".")[-1]
	rn = random.randint(0,1000)
	return "{}-{}.{}".format(name,rn,ext)

def extract_bg(bg):
	bg_img = bg.split(": ")[-1]
	print(bg_img)
	src = bg_img.replace("'"," ").replace("(",'').replace(")",'').replace(";",'').strip()
	src = re.search("\s+https://.*[^\)]",src)
	src = src.group(0).strip() if src else None
	return src

#parse the site based on passed pattern, pattern is a dictionary of css selectors
def parse(bs,pattern,root,url,image1_url,image2_url,reg=None):
	name_tag = bs.select(pattern.get("name"))
	name = name_tag[0].get_text().strip() if name_tag else ''
	address_rest = bs.find("span",{"class":"p-street-address"}).next_siblings if bs.find("span",{"class":"p-street-address"}) else ''
	address_rest = [l.get_text() for l in bs.find("span",{"class":"p-street-address"}).next_siblings] if address_rest else []
	address_head = bs.find("span",{"class":"p-street-address"}).get_text() if address_rest else ''
	address = address_head + ''.join(address_rest)
	country = bs.select("ul.list-inline.text-center a")[-1].get_text() if bs.select("ul.list-inline.text-center a") else None
	#if not is_country_allowed(country.strip()):
	#	return None
	causes = ",".join([tag.get_text() for tag in bs.select(" ul.list-inline.text-center a")[:-1]])  if bs.select("ul.list-inline.text-center a") else ''
	causes = map_focus(causes)
	website_tag   = bs.select(pattern.get("website"))
	website = website_tag[0].get("href").strip() if website_tag else ''
	reg_type,email,phone = get_contact(website)
	mission_tag = bs.select(pattern.get("mission"))
	mission = mission_tag[0].get_text() if mission_tag else ''
	description_tag = bs.select(pattern.get("description"))
	description = description_tag[0].get_text() if description_tag else ''
	reg_no = reg if reg else ''
	#reg_no    = reg.get_text() if  not (isinstance(reg,str) and reg) else reg  
	date,month = get_date_month(mission)
	year_founded = re.search("[^$]\d{4}",mission)
	year =  year_founded.group(0) if year_founded else ''
	gross_tag = bs.select(pattern.get("gross"))
	state_tag  = bs.select(pattern.get("state"))
	state = state_tag[0].get_text() if  state_tag else ""
	gross = " "
	image1_name = rename_images(name,image1_url)
	image2_name = rename_images(name,image1_url)
	download_image(image1_url,image1_name,FOLDER)
	download_image(image2_url,image2_name,FOLDER)
	images = json.dumps([image1_name,image2_name])
	reg_type = "EIN"
	return [ name,address,country,state,causes,email,phone,website,mission,description,reg_no,reg_type,year,month,date,
			gross,images,json.dumps([root]),json.dumps([url])]


def main(url,pattern):
	bs = fetch_resource(url,USER_AGENTS[0])
	conn,cur = open_db()
	create_folder()
	root = urlparse(url)
	root = root.scheme+"://"+root.netloc
	for i in range(1,833):
		print("page %d"%i)
		if bs:
			procs = []
			links = bs.select(pattern.get("link"))
			for link in links:
					if link:
						image1_tag = link.select(pattern.get("bg"))
						image2_tag = link.select(pattern.get("logo"))
						image1_url  = extract_bg(image1_tag[0].get("style")) if image1_tag else None
						image2_url = image2_tag[0].get("src") if image2_tag else None
						#print(image2_url,image1_url)
						target_url = root+link.get("href")
						proc = Process(target=crawl,args=(target_url,image1_url,image2_url,pattern))
						proc.start()
						procs.append(proc)
						time.sleep(0.2)

			time.sleep(1)
			for proc in procs: proc.join()
			#bs = fetch_resources(url+"?page=%d"i)
		#else:
			#dump_to_csv()
			#open("pledge-conf","w").write(str(step))
			#print("May be network is down => Retry")
			#exit(-2)

			#next_page = bs.select(pattern.get("next-page"))[0]
			#if next_page:
		#bs = fetch_resource(next_page.get("href"))
			#else:
		#print("next page I am looking at")
		bs = fetch_resource(url+"?page=%d"% i,USER_AGENTS[i%2])
		#if bs:
				#if bs.find(pattern.get("end")[0]).get_text() == pattern.get("end")[-1]:
					#exit(0)
		#step += 1
		if i % MAX_REQUESTS == 0:
			print(i%MAX_REQUESTS,i)
			print("slowing down requests for 1 minute") 
			time.sleep(DOWNLOAD_DELAY/2)

	dump_to_csv()

#crawl a single resource 
def crawl(url,image1_url,image2_url,pattern):
	print("in crawl get called %s"%url)
	response = fetch_resource(url,USER_AGENTS[0])
	reg = re.search("\d{2}[-]*\d{7}",url).group(0) if re.search("/\d{2}[-]*\d{7}/",url) else ''
	root = urlparse(url)
	conn,cur = open_db()
	root_domain = root.scheme+"://"+root.netloc
	if response:
		results = parse(response,pattern,root_domain,url,image1_url,image2_url,reg)
		print(results)
		if results:
			insert_to_db(conn,cur,results)
			dump_to_sql(results)
	os._exit(0)

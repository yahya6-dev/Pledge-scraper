import _thread as thread
import pymysql
from bs4 import BeautifulSoup
import requests
from utils import check_exists
from urllib.request import urlparse
from pledge_scraper import *









if __name__=="__main__":
	arg = argparse.ArgumentParser()
	arg.add_argument("-s","--site",default=0,help="Available site 1.https://www.pledge.to/organizations => type python3 start.py --site=1",type=int,choices=[1])
	sites = ["https://www.pledge.to/organizations"]
	args = arg.parse_args()
	if int(args.site) > 1:
		print("only one site => Available")
		exit(-2)
	if not args.site:
		print("Site not specified")
		exit(-22)
	site = sites[args.site-1]
	pattern = patterns[site]	
	main(site,pattern)	

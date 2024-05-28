from urllib.request import urlretrieve,urlparse
import os,sqlite3,csv,_thread as thread,re,json
import requests
import pymysql
#maximum timeout for each request including image download
TIME_OUT = 10.0
#user agent change per 1000  request
USER_AGENTS = ["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
				"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
			  ]
# one minute after 1000 requests
DOWNLOAD_DELAY = 60 
MAX_REQUESTS = 100
#this the list of accepted columns in the database
COLUMNS = ["Id","Organization_Name","Nonprofit_Address","Country","State_Province_Territory","Focus_Cause","Email","Phone",
	   "Website","Nonprofit_Mission","Nonprofit_Description","Goverment_Registration_Number","Goverment_Registration_Number_Type",
	   "Nonprofit_Registration_Date_Year","Nonprofit_Registration_Date_Month","Nonprofit_Registration_Date_Day",
	   "Gross_Income_yearly","Image_name","Domain_Scrapped","Specific_URL_Scrapped"]

##images folder
FOLDER = "../images/"
#list of accepted countries
COUNTRIES = ["India","United States of America","Pakistan","Nigeria",
     "Philippines","United Kingdom","Tanzania","South Africa","Kenya",
	 "Uganda","Canada","Ghana","Cameroon","Australia","Malawi","Zambia","Zimbabwe","Rwanda",
     "Burundi","South Sudan","Dominican Republic","Papua New Guinea",
     "Sierra Leone","Singapore","Liberia","Ireland","New Zealand","Eritrea","Jamaica",
     "Namibia","Gambia","Botswana","Lesotho","Trinidad and Tobago","Mauritius","Eswatini","Fiji",
     "Guyana","Solomon Islands","Micronesia","Malta","Belize","Bahamas","Barbados",
     "Samoa","Saint Lucia","Kiribati","Grenada"
     ]


#this sql statement for creating the in file sqlite table
CMD_SQLITE = """
	create table if not exists NonProfit(
	  Id integer primary key autoincrement,
          Organization_Name varchar(100),
          Nonprofit_Address varchar(100),
          Country varchar(100),
          State_Province_Territory varchar(100),
          Focus_Cause varchar(100),
          Email varchar(93),
          Phone varchar(20),
          Website varchar(163),
          Nonprofit_Mission varchar(10000) ,
          Nonprofit_Description varchar(5000),
          Goverment_Registration_Number varchar(100),
          Goverment_Registration_Number_Type varchar(50),
          Nonprofit_Registration_Date_Year varchar(30),
          Nonprofit_Registration_Date_Month varchar(30),
          Nonprofit_Registration_Date_Day varchar(30),
          Gross_Income_yearly varchar(10),
	  Image_name varchar(166),
	  Domain_Scrapped varchar(44) not null,
	  Specific_URL_Scrapped varchar(164)
	)
"""
def insert_to_db(conn,cur,data):
	name = data[0]
	stm = 'select * from nonprofit where Organization_Name="%s"'%name
	fields = str("%s,"*(len(COLUMNS)-1)).strip(",")
	insert_stm = "insert into nonprofit(%s) values(%s)" %(",".join(COLUMNS[1:]),fields)
	if not check_exists(cur,stm):
		cur.execute(insert_stm,data)
		conn.commit()

	
#open the database and return the cursor,db object
def open_db():
	try:
		conn = pymysql.connect(host='127.0.0.1',
    					user='falcon',
    					passwd='falcon',
    					db='Price'
    					)
	except:
		print("Database failed to open, check your login details")
		exit(-1)
	else:
		cur = conn.cursor()
		return conn,cur
		
def download_image(url,name,folder):	##download image from a given url, with a name provided
	path = folder+name.replace("/"," ")
	content = requests.get(url,headers={"user-agent":USER_AGENTS[0]},timeout=10.0)
	open(path,"wb").write(content.content)
	print('image download')

def create_folder():			##create the images folder if not exist
	try:
		os.mkdir(FOLDER)
	except:
		print("images folder => already exists")


def check_exists(cur,stm):		##check for duplicate
	cur.execute(stm)
	if cur.rowcount > 0:
		return True
	else:
		return False

def dump_to_sql(data):			##dump the result to database but using in file database
	conn = sqlite3.connect("../nonprofit.sql")
	cur  = conn.cursor()
	fields = str("?,"*(len(COLUMNS)-1)).strip(",")
	insert_stm = "insert into Nonprofit(%s) values(%s)" %(",".join(COLUMNS[1:]),fields)
	print(insert_stm) 
	cur.execute(CMD_SQLITE) 	##create the table if not exists 
	organization_name = data[0]
	if not check_exists(cur,'select * from nonprofit where Organization_Name="%s"'%organization_name): #filter duplicate
		cur.execute(insert_stm,data)
	conn.commit()
	conn.close()

def dump_to_csv():			##dump sql contents to csv file
	csv_path = "../nonprofit.csv"
	writer = csv.writer(open(csv_path,"a"))
	conn = sqlite3.connect("../nonprofit.sql")
	cur = conn.cursor()
	cur.execute("select * from nonprofit")
	writer.writerow(COLUMNS)
	for row in cur.fetchall():
		writer.writerow(row)
	conn.close()
	print("dumped to the csv file")

#map focus causes
def map_focus(causes):			#build list of causes and return it as json
	FocusCase = []
	for cause in causes.split(","):
                    if cause.strip() == 'Animals':
                        FocusCase.append("Animal Rights, Welfare, and Services")
                    if cause.strip() == 'Pets' or cause.strip() == 'Veterinary Services':
                        FocusCase.append("Zoos, Veterinary Services and Aquariums")
                    if cause.strip() == 'Diseases' or cause.strip() == 'Disorders':
                        FocusCase.append("Diseases, Disorders, and Disciplines")
                    if cause.strip() == 'Environment':
                        FocusCase.append("Environmental Protection and Conservation")
                    if cause.strip() == 'Food & Nutrition':
                        FocusCase.append("Food Banks, Food Pantries, and Food Distribution")
                    if cause.strip() == 'Nature Conservation':
                        FocusCase.append("Environmental Protection and Conservation")
                    if cause.strip() == 'Society':
                        FocusCase.append("Non-Medical Science & Technology Research")
                    if cause.strip() == 'Education':
                        FocusCase.append("Education") 
                    if cause.strip() == 'Health':
                        FocusCase.append("Health")
                    if cause.strip() == 'Mental Health':
                        FocusCase.append("Mental Health and Crisis Serices")
                    if cause.strip() == 'Disaster Relief':
                        FocusCase.append("Public Safety, Disaster Preparedness, and Relief ") 
                    if cause.strip() == 'Nature Conservation':
                        FocusCase.append("Environmental Protection and Conservation") 
                    if cause.strip() == 'Wildlife':
                        FocusCase.append("Wildlife Conservation") 
                    if cause.strip() == 'Museums':
                        FocusCase.append("Museums")
                    if cause.strip() == 'Art':
                        FocusCase.append("Arts, Culture, Humanities") 
                    if cause.strip() == 'Sports and Recreation':
                        FocusCase.append("Recreation and Sports")
                    if cause.strip() == 'Performing Arts':
                        FocusCase.append("Performing Arts" )
                    if cause.strip() == 'Youth Development':
                        FocusCase.append("Youth Development, Shelter, and Crisis Services")
                    if cause.strip() == 'Children & Family':
                        FocusCase.append("Children's and Family Services" )
                    if cause.strip() == 'Food & Nutrition':
                        FocusCase.append("Agriculture, Food and Nutrition" )
                    if cause.strip() == 'Science Research':
                        FocusCase.append("Non-Medical Science & Technology Research") 
                    if cause.strip() == 'Colleges and Universities':
                        FocusCase.append("College and University" )
                    if cause.strip() == 'Youth Development':
                        FocusCase.append("Youth Education Programs and Services")
                    if cause.strip() == 'Preschool':
                        FocusCase.append("Early Childhood Programs and Services") 
                    if cause.strip() == 'Medical Research':
                        FocusCase.append("Medical Research")
                    if cause.strip() == 'Mental Health':
                        FocusCase.append("Mental Health and Crisis Serices" )
                    if cause.strip() == 'Housing':
                        FocusCase.append("Housing and Neighborhood Development") 
	return json.dumps(FocusCase)

#filter output not allowed country
def is_country_allowed(country):
	if country in COUNTRIES:
		return country
	else:
		return None

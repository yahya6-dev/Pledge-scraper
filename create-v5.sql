CREATE TABLE nonprofit(
  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY
   ,Organization_Name                  VARCHAR(138) NOT NULL 
  ,Nonprofit_Address                  VARCHAR(1000)
  ,Country                            VARCHAR(52) NOT NULL
  ,State_Province_Territory             VARCHAR(47)
  ,Focus_Cause                       VARCHAR(450) NOT NULL
  ,Email                              VARCHAR(93)
  ,Website                            VARCHAR(109)
  ,Phone                              VARCHAR(30)
  ,Nonprofit_Mission                  TEXT
  ,Nonprofit_Description              VARCHAR(5000)
  ,Goverment_Registration_Number      VARCHAR(30)
  ,Goverment_Registration_Number_Type VARCHAR(30)
  ,Nonprofit_Registration_Date_Year    VARCHAR(30)
  ,Nonprofit_Registration_Date_Month   VARCHAR(30)
  ,Nonprofit_Registration_Date_Day     VARCHAR(30)
  ,Gross_Income_yearly                VARCHAR(30)
  ,Image_name                        VARCHAR(166)
  ,Domain_scrapped                    VARCHAR(44)
  ,Specific_URL_scrapped              VARCHAR(162) NOT NULL
  ,FIELD20                            VARCHAR(44)
);



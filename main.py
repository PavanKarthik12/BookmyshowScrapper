from ssl import VerifyFlags
from this import d
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time, re
from bs4 import BeautifulSoup as bs
from bms import get_collection
import snowflake.connector
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)
import bms
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
app = Flask(__name__)
option = Options()
option.add_argument('--disable-notifications')
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

def snowflake_connnect(query,type=None):
    conn = snowflake.connector.connect(
                    user='karthik777',
                    password='Pavan@123',
                    account='px65781.ap-southeast-1',
                    database='YOUTUBE_DB',
                    warehouse='YOUTUBE',
                    schema='PUBLIC',
                    )
    cur=conn.cursor()
    cur.execute('USE ROLE ACCOUNTADMIN')
    cur.execute(query)
    if type=='select':
        return cur.fetchall()
    cur.close()
    conn.commit()
    return "task done"
@app.route('/data',methods=['POST','GET'])
def get_city_data():
    if request.method == 'POST':
        city_name=request.form['city']
        movie_title=request.form['movie_name']
    with webdriver.Chrome(ChromeDriverManager().install(),chrome_options=option) as driver:
        url="https://in.bookmyshow.com/explore/movies-"+city_name
        driver.get(url)
        movie_name="-".join([each.lower() for each in movie_title.split(" ")])
        movie_links=driver.find_elements('css selector','a.eQiiBj')
        try:
            movie_hrefs=[each_movie_links.get_attribute('href') for each_movie_links in movie_links]
        except Exception as exc:
            print(exc)
        else:
            req_movie_href="".join([each_movie_href for each_movie_href in movie_hrefs if movie_name in each_movie_href])
            driver.get(req_movie_href)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(('css selector', "button.gsJmXR"))).click()
            time.sleep(10)
            theaters=driver.find_elements('id','venuelist')
            theater_html=bs(theaters[0].get_attribute('innerHTML'),"lxml")
            theaters_data=theater_html.find_all('li',{'class':'list'})
            table_name=url.split("-")[1]
            drop_query='''DROP TABLE if exists {0} ;'''.format(table_name)
            snowflake_connnect(drop_query)
            create_query="""create table {0} if not exists (s_no VARCHAR(250), theater_name VARCHAR(250)  NULL, show_time VARCHAR(250)  NULL, booked_gross VARCHAR(250)  NULL,total_gross VARCHAR(250) NULL);""".format(url.split("-")[1])
            snowflake_connnect(create_query)
            counter=0
            movie_theater={}
            for each_theater in theaters_data:
                #print(each_theater)
                time.sleep(2)
                venue_name=each_theater.find('a',{'class':'__venue-name'})
                total_collection={}
                for each_show in each_theater.find_all('a',{'class':'showtime-pill'}):
                    counter+=1
                    each_show_collection=dict.fromkeys(['total_gross','collected_gross'],)
                    try:
                        coll=get_collection('https://in.bookmyshow.com/'+each_show['href'])
                    except Exception as exc:
                        print(exc)
                    else:
                        print(venue_name.text,each_show['data-date-time'],coll)
                        each_show_collection['collected_gross']=coll[0]
                        each_show_collection['total_gross']=coll[1]
                        total_collection[each_show['data-date-time']]=each_show_collection
                        insert_query= '''INSERT INTO {0} VALUES ('{1}','{2}','{3}','{4}','{5}')'''.format(table_name,counter,venue_name.text,each_show['data-date-time'],coll[0],coll[1])
                        snowflake_connnect(insert_query)
                    movie_theater[venue_name.text]=total_collection
        print(movie_theater)
        return render_template('results.html',query_results=movie_theater)

if __name__ == "__main__":
    	app.run(debug=True)


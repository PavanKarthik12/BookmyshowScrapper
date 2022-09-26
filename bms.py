from ssl import VerifyFlags
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time, re
from bs4 import BeautifulSoup as bs
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)
option = Options()
option.add_argument('--disable-notifications')
 # route to show the review comments in a web UI
def get_collection(url):
    with webdriver.Chrome(ChromeDriverManager().install(),chrome_options=option) as driver:
        avg_cost=set()
        seats_no_cost=0
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(('css selector', "a._cuatro"))).click()
        time.sleep(2)
        try:
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(('id', "btnPopupAccept"))).click()
            time.sleep(2)
        except Exception as exc:
            try:
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(('id', "btnPopupOK"))).click()
            except Exception as exc:
                print(exc)
            else:
                time.sleep(3)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(('id', "proceed-Qty"))).click()
            time.sleep(2)
            seats_total=driver.find_element('css selector','table.setmain')
            seats_data=seats_total.get_attribute('innerHTML')
            seats_data=bs(seats_data, "html.parser")
            seats_rows=seats_data.find('tbody')
            no_cost=[]
            not_filled_seats=[]
            cost=0
            total_gross=0
            booked_gross=0
            for each in seats_rows:
                seats_avail_count=0
                if each.td.text.split(" ")==['\xa0']:
                    pass
                else:
                    try:
                        if each.td['class'][0]=='PriceB1':
                            try:
                                cost_tuple=each.div.text.split(" ")
                                if len(cost_tuple) > 1 :
                                    cost=float(cost_tuple[-1])
                                else:
                                    cost=7777777
                            except Exception as exc:
                                print(each.td)
                            else:
                                print("")
                    except Exception as exc:
                        if cost!=7777777:
                            print(cost)
                            avg_cost.add(cost)
                            seats_block_row=len(each.find_all('a',{'class':'_blocked'}))
                            seats_avail_row=len(each.find_all('div',{'data-seat-type':'1'}))
                            total_gross += (seats_avail_row+seats_block_row)*cost
                            booked_gross += seats_block_row*cost
                        else:
                            seats_block_row=len(each.find_all('a',{'class':'_blocked'}))
                            seats_avail_row=len(each.find_all('div',{'data-seat-type':'1'}))
                            seats_no_cost+=seats_block_row+seats_avail_row
                    else:
                        pass
            avg_cost_value=sum(int(i) for i in avg_cost)/len(avg_cost)
            total_gross+=avg_cost_value*seats_no_cost
            booked_gross+=avg_cost_value*seats_no_cost
            return [booked_gross,total_gross,seats_no_cost,avg_cost]
        else:
            time.sleep(3)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(('id', "proceed-Qty"))).click()
            time.sleep(2)
            seats_total=driver.find_element('css selector','table.setmain')
            seats_data=seats_total.get_attribute('innerHTML')
            seats_data=bs(seats_data, "html.parser")
            seats_rows=seats_data.find('tbody')
            no_cost=[]
            not_filled_seats=[]
            cost=0
            total_gross=0
            booked_gross=0
            for each in seats_rows:
                seats_avail_count=0
                if each.td.text.split(" ")==['\xa0']:
                    pass
                else:
                    try:
                        if each.td['class'][0]=='PriceB1':
                            try:
                                cost_tuple=each.div.text.split(" ")
                                if len(cost_tuple) > 1 :
                                    cost=float(cost_tuple[-1])
                                else:
                                    cost=7777777
                            except Exception as exc:
                                print(each.td)
                            else:
                                print("")
                    except Exception as exc:
                        if cost!=7777777:
                            print(cost)
                            avg_cost.add(cost)
                            seats_block_row=len(each.find_all('a',{'class':'_blocked'}))
                            seats_avail_row=len(each.find_all('div',{'data-seat-type':'1'}))
                            total_gross += (seats_avail_row+seats_block_row)*cost
                            booked_gross += seats_block_row*cost
                        else:
                            seats_block_row=len(each.find_all('a',{'class':'_blocked'}))
                            seats_avail_row=len(each.find_all('div',{'data-seat-type':'1'}))
                            seats_no_cost+=seats_block_row+seats_avail_row
                    else:
                        pass
        avg_cost_value=sum(int(i) for i in avg_cost)/len(avg_cost)
        total_gross+=avg_cost_value*seats_no_cost
        booked_gross+=avg_cost_value*seats_no_cost
        return [booked_gross,total_gross,seats_no_cost,avg_cost]


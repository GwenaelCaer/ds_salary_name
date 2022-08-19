# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 17:58:58 2022

@author: gwena
"""

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd

def get_jobs(keyword, num_jobs, verbose, path, slp_time):
    
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()
    
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    #options.add_argument('headless')
    
    #Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.set_window_size(1120, 1000)

    url = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="' + keyword + '"&clickSource=searchBox'
    #url = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="' + keyword + '"&locT=C&locId=1147401&locKeyword=San%20Francisco,%20CA&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    driver.get(url)
    jobs = []
    #print(url)

    while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.

        #Let the page load. Change this number based on your internet speed.
        #Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(slp_time)

        #Accepte les cookies 
        try:
            driver.find_element("id", "onetrust-accept-btn-handler").click()
        except ElementClickInterceptedException:
            pass
        
        time.sleep(5)
        
        #Test for the "Sign Up" prompt and get rid of it.
        try:
            driver.find_element("class name", "react-job-listing").click()
        except ElementClickInterceptedException:
            pass

        time.sleep(5)

        try:
            driver.find_element("css selector", '[alt="Close"]').click()  #clicking to the X.
        except NoSuchElementException:
            pass

        
        #Going through each job in this page
        job_buttons = driver.find_elements("class name", "react-job-listing")  #jl for Job Listing. These are the buttons we're going to click.
        N = -1
        for job_button in job_buttons:  

            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break
            
            job_button.click()  #You might 
            time.sleep(2)
            N += 1
            try:
                all_text = driver.find_element("xpath", './/div[@class="css-xuk5ye e1tk4kwz5"]').text
                rating = driver.find_element("xpath", './/span[@class="css-1m5m32b e1tk4kwz4"]').text
                company_name = all_text.replace(rating, '')

                location = driver.find_element("xpath", './/div[@class="css-56kyx5 e1tk4kwz1"]').text
                job_title = driver.find_element("xpath", './/div[contains(@class, "css-1j389vi e1tk4kwz2")]').text
                job_description = driver.find_element("xpath", './/div[@class="jobDescriptionContent desc"]').text
                print(f'SUCCED {N}')
            except:
                print(f'FAILED {N}')
                continue

            try:
                salary_estimate = driver.find_element("xpath", './/span[@class="css-1hbqxax e1wijj240"]').text
            except NoSuchElementException:
                salary_estimate = -1 #You need to set a "not found value. It's important."
                
            try:
                rating = driver.find_element("xpath", './/span[@class="css-1m5m32b e1tk4kwz4"]').text
            except NoSuchElementException:
                rating = -1 #You need to set a "not found value. It's important."

            #Printing for debugging
            if verbose:
                print("Job Title: {}".format(job_title))
                print("Salary Estimate: {}".format(salary_estimate))
                print("Job Description: {}".format(job_description[:500]))
                print("Rating: {}".format(rating))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))

            #Going to the Company tab...
            #clicking on this:
            #<div class="tab" data-tab-type="overview"><span>Company</span></div>
            
            
            company_infos = driver.find_elements("xpath", './/div[@class="d-flex justify-content-start css-daag8o e1pvx6aw2"]')
            info_names = {'Size': -1,
                          'Founded': -1,
                          'Type': -1,
                          'Industry': -1,
                          'Sector': -1,
                          'Revenue': -1}
            print(len(company_infos))
            for company_info in company_infos:
                try:
                    info_name = company_info.find_element("xpath", './/span[@class="css-1pldt9b e1pvx6aw1"]').text
                    info_content = company_info.find_element("xpath", './/span[@class="css-1ff36h2 e1pvx6aw0"]').text
                    info_names[info_name] = info_content
                except NoSuchElementException:
                    pass
                       
            size = info_names['Size']
            founded = info_names['Founded']
            type_of_ownership = info_names['Type']
            industry = info_names['Industry']
            sector = info_names['Sector']
            revenue = info_names['Revenue']

                
            if verbose:
                #print("Headquarters: {}".format(headquarters))
                print("Size: {}".format(size))
                print("Founded: {}".format(founded))
                print("Type of Ownership: {}".format(type_of_ownership))
                print("Industry: {}".format(industry))
                print("Sector: {}".format(sector))
                print("Revenue: {}".format(revenue))
                #print("Competitors: {}".format(competitors))
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"Job Title" : job_title,
            "Salary Estimate" : salary_estimate,
            "Job Description" : job_description,
            "Rating" : rating,
            "Company Name" : company_name,
            "Location" : location,
            #"Headquarters" : headquarters,
            "Size" : size,
            "Founded" : founded,
            "Type of ownership" : type_of_ownership,
            "Industry" : industry,
            "Sector" : sector,
            "Revenue" : revenue,
            #"Competitors" : competitors
            })
            #add job to jobs

        #Clicking on the "next page" button
        try:
            driver.find_element("xpath", './/li[@class="next"]//a').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break

    return pd.DataFrame(jobs)  #This line converts the dictionary object into a pandas DataFrame.
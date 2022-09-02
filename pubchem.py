
import re
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import warnings
import streamlit as st 
import pandas as pd
warnings.simplefilter("ignore", UserWarning)


cas_no = st.text_input('CAS Number')



def get_name(data):
    try:
        name = driver.find_element(By.CSS_SELECTOR, 'h1.m-zero')
        compound_name = name.text
        data['Name'] = compound_name
    except:
        print("[INFO] Name is not avialable")
        data['Name'] = 'None'

    return data


def get_summary(data):
    try:
        temp_list = ['Molecular Formula', 'Molecular Weight']
        summary = driver.find_element(By.CSS_SELECTOR, 'table.summary')
        tr_tags = summary.find_elements(By.CSS_SELECTOR, 'tr')
        
        if tr_tags:
            for check_string in temp_list:
                for tags in tr_tags:
                    if check_string in tags.text:
                        s = tags.text.split()
                        data[check_string] = s[2]

                        break
    except:
        print("[INFO] Molecule Formula and Molecule weight not found")
        data['Molecular Formula'] = 'None'
        data['Molecular Weight'] = 'None'

    return data


def get_smile(data):
    try:
        smile = driver.find_element(By.ID, 'Canonical-SMILES')
        smile_code = smile.find_element(By.CSS_SELECTOR, 'p').text
        data['Smile'] = smile_code
    except:
        print('[INFO] Smile not found')
        data['Smile'] = 'None'

    return data

def get_h_statemenmt(info, hazard):
    for j in info:
        r = re.findall(r'H[0-9][0-9][0-9].*', str(j.text))
        if r:
            temp = r[0].split(':')
            hazard[temp[0]] = temp[1]
    return hazard

def get_ghs(hazard):
    try:
        ghs = driver.find_element(By.ID, 'GHS-Classification')
        ghs_temp = ghs.find_elements(By.CSS_SELECTOR, 'div.breakword')
        hazard = get_h_statemenmt(ghs_temp, hazard)


        ghs_string = ghs.find_elements(By.CSS_SELECTOR, 'p')
        hazard = get_h_statemenmt(ghs_string, hazard)
    except:
        print('[INFO] GHS not found')

    
    return hazard


def quit_driver():
    return driver.quit()


def main():
    data = {}
    hazard = {}
    data = get_name(data)
    data = get_summary(data)
    data = get_smile(data)
    hazard = get_ghs(hazard)

    return (data, hazard)


def create_df_data(data):
    df = pd.DataFrame({'Name': [data['Name']],
                    'Molecular Formula': [data['Molecular Formula']],
                    'Molecular Weight': [data['Molecular Weight']],
                    'Smile': [data['Smile']]})

    return df

def create_df_hazard(hazard):
    df = pd.DataFrame({'Code': hazard.keys(),
                    'Statement': hazard.values()})

    return df

if st.button('Search'):

    try:
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options = option, service= service)
    except:
        print("[INFO] Driver not laoded")



    start_link = "https://pubchem.ncbi.nlm.nih.gov/#query=" + str(cas_no)

    driver.get(start_link)
    driver.implicitly_wait(5)
    try:
        tmp = driver.find_elements(By.CSS_SELECTOR, 'span.breakword')
        driver.implicitly_wait(4)
        cid = tmp[1].text
        n_link = start_link.split('#')[0]
        link = n_link + 'compound/' + cid
    except:
        print("[INFO] Compound not avialable")

    tmp = driver.find_elements(By.CSS_SELECTOR, 'span.breakword')
    driver.implicitly_wait(4)
    cid = tmp[1].text

    n_link = start_link.split('#')[0]
    link = n_link + 'compound/' + cid


    driver.get(link)
    data, hazard = main()
    quit_driver()
    df = create_df_data(data)
    st.write(df)    

    h_df = create_df_hazard(hazard)
    st.write(h_df)







        



import re
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import warnings
import streamlit as st 
import pandas as pd
warnings.simplefilter("ignore", UserWarning)


cas_no = st.text_input('CAS Number')



def get_name(data):
    # name = driver.title
    # name.split()
    name = driver.find_element(By.CSS_SELECTOR, 'h1.m-zero')
    compound_name = name.text
    data['Name'] = compound_name

    return data

def get_summary(data):
    
    temp_list = ['Molecular Formula', 'Molecular Weight']
    summary = driver.find_element(By.CSS_SELECTOR, 'table.summary')
    tr_tags = summary.find_elements(By.CSS_SELECTOR, 'tr')

    for check_string in temp_list:
        for tags in tr_tags:
            if check_string in tags.text:
                s = tags.text.split()
                print(s)
                data[check_string] = s[2]

                break

    return data


def get_smile(data):
    smile = driver.find_element(By.ID, 'Canonical-SMILES')
    smile_code = smile.find_element(By.CSS_SELECTOR, 'p').text
    data['Smile'] = smile_code

    return data

def get_ghs(hazard):
    ghs = driver.find_element(By.ID, 'GHS-Classification')
    ghs_string = ghs.find_elements(By.CSS_SELECTOR, 'p')
    
    for t in ghs_string:
        r = re.findall(r'H[0-9][0-9][0-9].*', str(t.text))
        if r:
            temp = r[0].split(':')
            hazard[temp[0]] = temp[1]
    
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


    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options = option, service= service)



    start_link = "https://pubchem.ncbi.nlm.nih.gov/#query=" + str(cas_no)

    driver.get(start_link)
    driver.implicitly_wait(5)
    tmp = driver.find_elements(By.CSS_SELECTOR, 'span.breakword')
#     st.write(tmp)
    driver.implicitly_wait(4)
    cid = tmp[1].text

    n_link = start_link.split('#')[0]
    link = n_link + 'compound/' + cid


    driver.get(link)
    data, hazard = main()
    quit_driver()
    st.write(hazard)

    df = create_df_data(data)
    st.write(df)    

    h_df = create_df_hazard(hazard)
    st.write(h_df)







        


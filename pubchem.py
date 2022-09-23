
import re
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import warnings
import streamlit as st 
import pandas as pd
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

import pyperclip
warnings.simplefilter("ignore", UserWarning)




category = {'Green' : ['H302','H312','H332','H333','H303','H305', 'H313','H315','H316','H319','H320','H335'],
           'Amber' : ['H301','H311','H331','H300','H310', 'H304', 'H314','H336'],
            'Red' : ['H330','H340','H350','H360', 'H317', 'H334', 'H318', 'H341', 'H351', 'H361', 'H370', 'H371','H372','H373']}


cas_no = st.text_input('CAS Number', '57-27-2')



def get_name(data):
    try:
        name = driver.find_element(By.CSS_SELECTOR, 'h1.m-zero')
        compound_name = name.text
        data['Name'] = compound_name
    except:
        st.write("[INFO] Name is not avialable")
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
        st.write("[INFO] Molecule Formula and Molecule weight not found")
        data['Molecular Formula'] = 'None'
        data['Molecular Weight'] = 'None'

    return data


def get_smile(data):
    try:
        smile = driver.find_element(By.ID, 'Canonical-SMILES')
        smile_code = smile.find_element(By.CSS_SELECTOR, 'p').text
        data['Smile'] = smile_code
    except:
        st.write('[INFO] Smile not found')
        data['Smile'] = 'None'

    return data

def get_density(data):
    match_string = '°C'
    try:
        density_tag = driver.find_element(By.ID, 'Density')
        denisty_content = density_tag.find_elements(By.CSS_SELECTOR, 'div.section-content-item')
        for i in range(len(denisty_content)):
            m = denisty_content[i].find_element(By.CSS_SELECTOR, 'p')
            if match_string in m.text:
                data['Density'] = m.text
    except:
        data['Density'] = None

    return data

def get_h_statemenmt(info, hazard):
    for j in info:
        r = re.findall(r'H[0-9][0-9][0-9].*', str(j.text))
        if r:
            temp = r[0].split(':')
            if '(' in temp[0]:
                z = temp[0].split(' ')
                hazard[z[0]] = temp[1]
            else:
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
        st.write('[INFO] GHS not found')

    
    return hazard

def check_category(category, hazard):
    category_item = {}
    tmp = list(hazard.keys())
    for i in tmp:
        if '(' in i:
            x = i.split(' ')
            y = x[0]
        else:
            y = i
    
        for j in category.keys():
            if y in category[j]:
                if j in category_item.keys():
                    category_item[j].append(y)
                else:
                    category_item[j] = [y]
                
    
    return category_item


def format_color_groups(df):
    colors = ['Yellow', 'Green', 'Red']
    x = df.copy()
    factors = list(category_item.keys())
    i = 0
    for i in range(df.shape[0]):
        for factor in factors:
             if df.iloc[i, 0] in category_item[factor]:
                    if factor == 'Amber':
                        style = f'background-color: {colors[0]}'
                        x.loc[i, :] = style
                    if factor == 'Green':
                        color = colors[0]
                        style = f'background-color: {colors[1]}'
                        x.loc[i, :] = style
                    if factor == 'Red':
                        color = colors[0]
                        style = f'background-color: {colors[2]}'
                        x.loc[i, :] = style
    return x


def quit_driver():
    return driver.quit()


def main():
    data = {}
    hazard = {}
    data = get_name(data)
    data = get_summary(data)
    data = get_smile(data)
    data = get_density(data)
    hazard = get_ghs(hazard)

    return (data, hazard)


def create_df_data(data):
    df = pd.DataFrame({'Name': [data['Name']],
                    'Molecular Formula': [data['Molecular Formula']],
                    'Molecular Weight': [data['Molecular Weight']],
                    'Smile': [data['Smile']],
                    'Density': [data['Density']]})

    return df

def create_df_hazard(hazard):
    df = pd.DataFrame({'Code': hazard.keys(),
                    'Statement': hazard.values()})

    return df

# df = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})

# st.dataframe(df)

# copy_button = Button(label="Copy DF")
# copy_button.js_on_event("button_click", CustomJS(args=dict(df=df.to_csv(sep='\t')), code="""
#     navigator.clipboard.writeText(df);
#     """))

# no_event = streamlit_bokeh_events(
#     copy_button,
#     events="GET_TEXT",
#     key="get_text",
#     refresh_on_update=True,
#     override_height=40,
#     debounce_time=0)
# if st.button('Press'):

#     pyperclip.copy(df.to_csv())

# no_event = streamlit_bokeh_events(
#     copy_button,
#     events="GET_TEXT",
#     key="get_text",
#     refresh_on_update=True,
#     override_height=40,
#     debounce_time=0)

if st.button('Search'):

    try:
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options = option, service= service)
    except:
        st.write("[INFO] Driver not laoded")



    start_link = "https://pubchem.ncbi.nlm.nih.gov/#query=" + str(cas_no)

    driver.get(start_link)
    driver.implicitly_wait(2)
    try:
        category_file = 'Categories.xlsx'
        tmp = driver.find_elements(By.CSS_SELECTOR, 'span.breakword')
        driver.implicitly_wait(2)
        if tmp:
            cid = tmp[1].text
            n_link = start_link.split('#')[0]
            link = n_link + 'compound/' + cid
            n_link = start_link.split('#')[0]
            link = n_link + 'compound/' + cid
            driver.get(link)

            data, hazard = main()
            quit_driver()
            df = create_df_data(data)
            st.write(df) 

            
        




            # copy button for molecule details
            # st.write('copy button')
            # copy_button = Button(label="Copy DF")
            # copy_button.js_on_event("button_click", CustomJS(args=dict(df=df.to_csv(sep='\t')), code="""
            #     navigator.clipboard.writeText(df);
            #     """))  
            # result = streamlit_bokeh_events(
            # copy_button,
            # events="GET_TEXT",
            # key="get_text",
            # refresh_on_update=True,
            # override_height=75,
            # debounce_time=0)

            # # st.write(result)

            h_df = create_df_hazard(hazard)
            st.write(h_df)

            category_item = check_category(category, hazard)

            ################
            #    check this line
            ###################


            #st.write(h_df.style.apply(format_color_groups, axis=None))


            # st.write(category_item)
            st.subheader('Category:')
            if 'Red' in category_item.keys():
                cat = pd.read_excel(category_file, sheet_name= 'Red')
                st.write(cat)
            elif 'Amber' in category_item.keys():
                cat = pd.read_excel(category_file, sheet_name= 'Amber')
                st.write(cat)
            elif 'Green' in category_item.keys():
                cat = pd.read_excel(category_file, sheet_name= 'Green')
                st.write(cat)
            else:
                cat = pd.read_excel(category_file, sheet_name= 'Special')
                st.write(cat)
            # for i in category_item.keys():
            #     if i == 'Green':
            #         st.success(category_item[i], icon = "✅")
            #     if i == 'Amber':
            #         st.warning(category_item[i], icon = "⚠️")
            #     if i == 'Red':
            #         st.error(category_item[i],icon = "🚨")
            
        else:
            
            st.write("[INFO] Compound not avialable")
    except:
        st.write("[INFO] Compound not avialable")

# if st.button('Press'):
#     pyperclip.copy(df.to_csv())

    


    








        


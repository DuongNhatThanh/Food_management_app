import sqlite3
import math
import time
#from st_aggrid import AgGrid
import pandas as pd
import streamlit as st
from streamlit_lottie import st_lottie
#from PIL import Image
import functions as ft
import interface as itf

import nltk

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import string
from ast import literal_eval

#background img
img = itf.get_img_as_base64("Picture2.png")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: 100%;
background-repeat: no-repeat;
background-attachment: local;
}}
</style>
"""

nutrition = pd.read_csv("Nutrition.csv")
portion = pd.read_csv("Portion.csv")
foodchoice = nutrition['Main food description']

# ---

con = sqlite3.connect("database.db")  # create a connection to the database database.db
cur = con.cursor()  # create cursor to execute SQL statements and fetch results from SQL queries
cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER, username VARCHAR PRIMARY KEY, password VARCHAR)''')
cur.execute(
    """CREATE TABLE IF NOT EXISTS storage (id INTEGER, foodname VARCHAR, foodcode INTEGER, foodweight FLOAT, exp VARCHAR, expstatus VARCHAR)""")
cur.execute("""CREATE TABLE IF NOT EXISTS usercalo(id INTEGER, calo FLOAT, datetakeout VARCHAR)""")

itf.local_css("style.css")

selected = itf.streamlit_menu()

if selected == "About Us":
    st.markdown(page_bg_img, unsafe_allow_html=True)
    flake1 = "🍞"
    flake2 = "🥦"
    flake3 = "🍗"
    flake4 = "🥗"
    flake5 = "🍙"
    flake6 = "🍜"
    flake7 = "🍏"
    flake8 = "🥝"
    st.markdown(
        f"""
        <div class="snowflake">{flake1}</div>
        <div class="snowflake">{flake2}</div>
        <div class="snowflake">{flake3}</div>
        <div class="snowflake">{flake4}</div>
        <div class="snowflake">{flake5}</div>
        <div class="snowflake">{flake6}</div>
        <div class="snowflake">{flake7}</div>
        <div class="snowflake">{flake8}</div>
    """,
        unsafe_allow_html=True, )
    st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 50px'>
                YOUR FOOD MANAGEMENT
                </h1>""", unsafe_allow_html=True)
    col0_1, col0_2 = st.columns([3,2])
    with col0_1:
        st.markdown("""<p style='text-align: center; color: #ffefd6;'>
                            useful for those who are on a diet to optimize overall health.
                            </p>""", unsafe_allow_html=True)
        st.image("Picture3.png")
    with col0_2:
        # insert gif
        ani_1 = itf.load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_TmewUx.json")
        st_lottie(ani_1, speed=1, reverse=False, loop=True, quality="high", height=None, width=None, key=None)
    col2_1, col2_2 = st.columns([4,2])
    with col2_1:
        st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 25px'>
                        Introduction
                        </h1>""", unsafe_allow_html=True)
    with col2_2:
        st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 25px'>
                                Our Team
                                </h1>""", unsafe_allow_html=True)
    col1_1, col1_2, col1_3= st.columns([4,1,1])
    with col1_1:
        st.markdown("""<p style='text-align: justify;'>
                        This app will help you discover food in the refrigerator and manage your
                        shopping for the entire week. For users who are perplexed about how to
                        manage the food in their storage, our app is a nutrition and healthy
                        enhancement tool. This will give you a clear view of the storage by
                        displaying the food management and calculating the calories consumed,
                        macro, for the entire meal. Additionally, our app offers menu suggestions
                        and a body indicator review. This tools tracks your calories and provides
                        advise regarding the macronutrients on your plate, making it particularly
                        useful for those who are on a diet to optimize overall health.
                        </p>""", unsafe_allow_html=True)
    with col1_2:
        st.image("duong_pic.jpg")
        st.image("ngoc_pic.jpg")
        st.image("loc_pic.jpg")
    with col1_3:
        st.image("ha_pic.jpg")
        st.image("thanh_pic.jpg")
        st.image("linh_pic.jpg")

elif selected == "Home Page":
    st.markdown(page_bg_img, unsafe_allow_html=True)
    col0_1, col0_2, col0_3, col0_4 = st.columns(4)
    with col0_1:
        pass
    with col0_2:
        st.image("Picture1.png", width=315)
    with col0_1:
        pass
    with col0_1:
        pass
    st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 50px'>
                        YOUR FOOD MANAGEMENT
                        </h1>""", unsafe_allow_html=True)

    col1_1, col1_2= st.sidebar.columns(2)
    with col1_1:
        signinbutton = st.button('Sign In')
    with col1_2:
        signupbutton = st.button('Sign Up')

    if 'signup' not in st.session_state:
        st.session_state.signup = False
    if (signupbutton or st.session_state.signup) and signinbutton == False:
        st.session_state.signup = True
        st.session_state.signin = False
        st.sidebar.write('Create New Account')
        new_user_id = ft.get_all_data('users')
        new_user_id = len(new_user_id) + 1
        new_username = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button('sign up'):
            try:
                cur.execute('''INSERT INTO users (id, username, password) VALUES (?, ?, ?)''',
                                (new_user_id, new_username, new_password))
                con.commit()
                st.sidebar.success("Succesfully. Sign In to begin")
            except:
                st.sidebar.warning('Username Already Exists.')

    if 'signin' not in st.session_state:
        st.session_state.signin = False
    if (signinbutton or st.session_state.signin) and signupbutton == False:
        st.session_state.signin = True
        st.session_state.signup = False
        st.sidebar.write('Sign In to Your Food Management')
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        if 'signinsubmit' not in st.session_state:
            st.session_state.signinsubmit = False
        if st.sidebar.button('sign in') or st.session_state.signinsubmit == True:
            st.session_state.signinsubmit = True
            check_signin = ft.check_signin(username, password)
            if not check_signin:
                st.sidebar.warning("Incorrect password/username.")
            else:
                st.sidebar.success(f"Logged in as {username}.")
                st.markdown(f"""<p style='text-align: center; font-size: 17px; color: #eaa928' >
                                        Welcome {username}
                                        </p>""", unsafe_allow_html=True)
                currentid = ft.get_data(tablename='users', category_find='username', category_select='id',
                                        data=username)
                currentdata = ft.get_data(tablename='storage', category_find='id', data=currentid, convert_list=False)
                ft.update_days_remained(currentid)
                ft.noti(currentdata)
                currentdata = pd.DataFrame(currentdata,
                                           columns=["ID", "Food Name", "Food Code", "Food Weight (Grams)", "EXP",
                                                    "Days Remained"])
                # new: delete id and foodcode column
                currentdataprint = currentdata
                del currentdataprint['ID']
                del currentdataprint['Food Code']
                currentdata.index += 1
                col3_1, col3_2 = st.columns([4,1])
                with col3_1:
                    currentdataprint['Food Weight (Grams)'] = ['{:.2f}'.format(i) for i in
                                                          currentdataprint['Food Weight (Grams)']]
                    st.table(currentdataprint.style.apply(ft.color_coding, axis=1))
                with col3_2:
                    st.markdown("""<style>
                                    div.stButton > button:first-child {
                                    background-color: #ffefd6;
                                    text-align: center;
                                    border-radius: 20px;
                                    }</style>
                                    """, unsafe_allow_html=True)
                    removebutton = st.button("Remove Expired Foods")
                    calovisual_button = st.button("Calo Visualization")
                    history_button = st.button("Food Take Out History")
                    # new: remove all expired food
                    if removebutton:
                        ft.delete_expired(currentid)
                        st.experimental_rerun()

                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    with st.expander("Add New"):
                        ft.add_new(currentid)
                with col2_2:
                    with st.expander("Take Out and Calculate Calories"):
                        ft.take_out(currentid)
                if 'calovisual' not in st.session_state:
                    st.session_state.calovisual = False
                if calovisual_button or st.session_state.calovisual:
                    st.session_state.calovisual = True
                    col5_1, col5_2 = st.columns(2)
                    with col5_1:
                        date1 = st.date_input("Enter the start date")
                        date2 = st.date_input("Enter the end date")
                        st.markdown("""
                                    <style>
                                    div.stButton > button:first-child 
                                    {
                                    text-align: center;
                                    border-radius: 20px;
                                    }
                                    </style>""", unsafe_allow_html=True)
                        if st.button('hide chart'):
                            st.session_state.calovisual = False
                            st.experimental_rerun()
                    with col5_2:
                        ft.visualization(currentid, date1, date2)
                # st.write(st.session_state)
                if 'history' not in st.session_state:
                    st.session_state.history = False
                if history_button or st.session_state.history:
                    history = ft.get_data(tablename='calohistory', category_find='id', data=currentid, convert_list=False)
                    historyframe = pd.DataFrame(history,
                                                columns=["ID", "Food Name", "Food Code", "Food Weight (Grams)",
                                                         "Date Take Out"])
                    del historyframe["Food Code"]
                    del historyframe["ID"]
                    historyframe.index += 1
                    historyframe["Food Weight (Grams)"] = ['{:.2f}'.format(i) for i in
                                                           historyframe["Food Weight (Grams)"]]
                    st.table(historyframe)
                    if st.button("hide table"):
                        st.session_state.history=False
                        st.experimental_rerun()


elif selected == "Body Calculating":
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 50px'>
                            BODY CALCULATING
                            </h1>""", unsafe_allow_html=True)
    #st.write('Function for body calculating')
    #image = Image.open("calories.jpg")
    #st.image(image)
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Enter you weight :")
    with col2:
        unit_w = st.radio("Choose your weight unit", ("KG", "Pound(Lbs)"))
        if unit_w == 'Pound':
            weight = round(weight * 2.20462262, 2)
        else:
            weight = weight
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Enter your height :", min_value=0.01)
    with col2:
        unit_h = st.radio("Choose your height unit", ("CM", 'Inch', 'Feet'))
        if unit_h == 'Inch':
            height = round(height * 2.54)
        elif unit_h == 'Feet':
            height = round(height * 30.48, 2)
        else:
            height = height
    age = st.number_input("Enter your age:")
    gender = st.selectbox("Choosing your gender", ("Male", "Female"))
    if gender == 'Male':
        gender_number = 1
    else:
        gender_number = 0
    bmi = weight / ((height / 100) * (height / 100))
    calBMR = st.button("Calculating BMR - BASAL METABOLIC RATE")
    if calBMR:
        with st.spinner("Calculating"):
            time.sleep(1)
            if gender_number == 1:
                bmr = round(66 + (13.7 * weight) + (5 * height) - (6.8 * age))
                st.subheader(f'Your maintainance calories is {round(bmr, 2)} calories')
            if gender_number != 1:
                bmr = round(655 + (9.6 * weight) + (1.8 * height) - (4.7 * age))
                st.subheader(f'Your maintainance calories is {round(bmr, 3)} calories')
            st.write("This based on the Harros - Benedict formula is based on total weight,height,age and gender")
    calBMI = st.button("Calculating BMI - BODY MASS INDEX")
    if calBMI:
        with st.spinner("Calculating"):
            time.sleep(1)
            st.subheader(f"Your BMI is {round(bmi, 2)}")
            bmi_range = pd.read_csv("bmi.csv")
            st.dataframe(bmi_range)

    if age < 18:
        body_fat = (1.51 * bmi) - (0.7 * age) - (3.6 * gender_number)
    else:
        body_fat = (1.39 * bmi) + (0.16 * age) - (10.34 * gender_number) - 9
    if st.button('Calculating Body fat percentage '):
        with st.spinner("Calculating"):
            time.sleep(1)
            st.subheader(f'Your body fat = {round(body_fat, 2)}')
            st.write("Healthy range")
            healthy_range = {"age": [20 - 39, 40 - 59, "above 60"], "Healthy percentage": []}
            df = pd.read_csv("body-fat-healthy-range.csv")
            st.dataframe(df)

    if gender_number == 1:
        tdee = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        tdee = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
    if st.button("Calculating TDEE - TOTAL DIARY ENERGY EXPENDITURE"):
        st.header("TDEE - TOTAL DIARY ENERGY EXPENDITURE")
        with st.spinner("Calculating"):
            time.sleep(1)
            tdee_data = [["SEDENTARY", round(tdee * 1.2, 2), "Little or no exercise, desk job"],
                         ["lIGHTLY ACTIVE", round(tdee * 1.375, 2), "light exercise/ sports 1-3 days/week"],
                         ["MODERATELY ACTIVE", round(tdee * 1.55, 2), "Moderate exercise/ sports 6-7 days/week"],
                         ["VERY ACTIVE", round(tdee * 1.725, 2), "Hard exercise every day, or exercising 2 xs/day"],
                         ["EXTRA ACTIVE", round(tdee * 1.99, 2),
                          "Hard exercise 2 or more times per day, or training for marathon, or triathlon, etc."]]
            col_names = ["Level of active", "TDEE", "Example of activities"]
            st.table(tdee_data)

    ffm = round(weight * (1 - (body_fat / 100)), 2)
    ffmi = round(ffm / math.sqrt(height))
    bdf = round((body_fat / 100) * weight, 2)
    if st.button("FFMI - FAT FREE MASS INDEX"):
        with st.spinner("Calculating"):
            time.sleep(1)
            st.header("Calculating Fat free mass")
            st.write(
                "Fat free mass is estimated using the following method: fat free mass = weight [kg] × (1 - (body fat [%]/ 100)). Result is also expressed in kilograms [kg]")
            st.subheader(f"FAT FREE MASS = {ffm} kg")
            st.write(
                "FFMI is calculated respectively: FFMI = fat free mass [kg]/ (height [m])². Expressed in kilograms per square meter [kg/m²].")
            st.subheader(f"FAT FREE MASS INDEX =  {ffmi} (kg/m²)")
            st.write(
                f"Body fat calculation bases on the simply equation: body fat = weight [kg] × (body fat [%] / 100). It is expressed in kilograms units [kg].")
            st.subheader(f"BODY FAT = {bdf} kg")

    st.write("")
    st.write("")
    col1, col2 = st.columns(2)
    protein_deficit = weight * 1.6
    fat_def = weight * 0.6
    protein_gain = weight * 1.8
    carb_gain = weight * 5.2
    with col1:
        level_activities = st.radio("Choosing your level of activities:",
                                    ("Sedentary", "Lightly active", "Moderate active", "Very active", "Extra active"))
        if level_activities == "Sedentary":
            gain = tdee * 1.2 + 200
            deficit = tdee * 1.2 - 200
        if level_activities == "Lightly active":
            gain = tdee * 1.375 + 200
            deficit = tdee * 1.375 - 215
        if level_activities == "Moderate active":
            gain = tdee * 1.55 + 200
            deficit = tdee * 1.55 - 200
        if level_activities == "Very active":
            gain = tdee * 1.725 + 200
            deficit = tdee * 1.725 * 0.8
        if level_activities == "Extra active":
            gain = tdee * 1.99 + 200
            deficit = tdee * 1.99 * 0.8
            protein_deficit = weight * 2.2
            fat_def = 0.5 * weight
    carb = (tdee - protein_deficit - fat_def) / 4
    with col2:
        st.caption("WEIGHT LOSS - CALORIES DEFICIT")
        if st.button("Calories deficit"):
            st.markdown("To lose fat, we typically recommend that using a caloric deficit")
            st.write(f"Your intake calories based on your TDEE : {round(deficit, 2)} calories")
            st.write("Your macro in your meal:")
            st.write(f"You should eat {round(protein_deficit, 2)} gram of protein")
            st.caption(f"Protein: 1.5 gram per pound of bodyweight.")
            st.write(f"You should eat {fat_def} gram of fat")
            st.caption("Fat: 0.3 - 0.5 grams per pound of bodyweight")
            st.write(f"You shoulde eat {carb} gram of carb")
            st.caption(
                "Carb:determined by subtracting your protein and fat calories from the daily calorie total, then dividing by 4 to get the number of carbs you eat per day (as each gram of carbohydrate contains 4 calories).")
            st.subheader("")
            st.warning(
                "Now, remember, the TDEE and BMR calculations are estimates. If you find, after performing your own calculations, that you’re not losing weight, then remove another 100 calories from your daily calorie intake and assess progress over the next 2 weeks.")

        st.caption("GAIN WEIGHT - CALORIES SURPLUS")
        if st.button("Calories surplus"):
            st.markdown(
                "Gaining weight, and preferably muscle, requires consuming more calories than your body expends on a daily basis.")
            st.write(f"Your intake calories based on your TDEE: {round(gain, 2) or round((gain + 100), 2)} calories")
            st.markdown(f"You should eat {protein_gain}  gram of protein")
            st.caption(f"Protein: 1.8 gram per pound of bodyweight.")
            st.write(f"You shoulde eat {carb_gain} gram of carb")
            st.caption("Carb for weight gain should be 4-7g /kg of body weight of carbohydrates per day ")
            st.warning(
                "Gaining weight, and preferably muscle, requires consuming more calories than your body expends on a daily basis.It is importatn to focus on your TDEE")
else:
    st.markdown(page_bg_img, unsafe_allow_html=True)
    nltk.download('omw-1.4')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

    st.markdown("""<h1 style='text-align: center; font-family: Candara; font-size: 50px'>
                                MENU SUGGESTIONS
                                </h1>""", unsafe_allow_html=True)
    st.markdown(
        "![Alt Text](https://media2.giphy.com/media/b5Hcaz7EPz26I/giphy.gif?cid=ecf05e47tniettz60x8aqh1eh7vjgjn6p08n0p63gzjrrvxo&rid=giphy.gif&ct=g)")
    st.write('Tell us what ingredients you have at home and we can suggest recipes for you to make!')
    st.write(
        'We can also filter this down depending on your skill level :zap:, dietary requirements :seedling: how much time '
        'you are willing to commit :watch: and what course you are looking to make 🍳')

    ingred = ''

    st.write("""
    ##### What ***ingredients*** do you have?
    """)
    ingred = st.text_input("separate ingredients with a comma. eg. eggs,rice,cheese")
    if ingred:
        st.write('✔️')
    elif ingred == '':
        st.write('🔮')

    st.write("""
    ##### Select any ***dietary*** requirements!:seedling:
    """)
    options1 = ['vegetarian', 'vegan', 'none']
    diet_requirements = st.selectbox('diet', options1)

    st.write("""
    ##### How much ***time*** do you want to spend cooking?(in minutes):watch:
    """)
    n = st.slider('time', 0, 200)

    st.write("""
    ##### What ***course*** would you like to make?🍳
    """)
    options = ['starter', 'main', 'dessert']
    course = st.selectbox('course', options)

    st.write("""
    ##### What is your ***skill level***:zap:?
    """)
    option = ['beginner', 'intermediate', 'advanced']
    skill_level = st.selectbox('skill level', option)

    submit = st.button("Show me recipe's")

    #################################
    diet = ''
    skill = ''

    if diet_requirements == 'vegetarian':
        diet = 'vegetarian'
    elif diet_requirements == 'vegan':
        diet = 'vegan'
    elif diet_requirements == 'none':
        diet = None

    if skill_level == 'beginner':
        skill = 'beginner'
    elif skill_level == 'intermediate':
        skill = 'intermediate'
    elif skill_level == 'advanced':
        skill = 'advanced'


    ###########################################

    # function to give recipe recommendations

    def suggest_recipes(diet, n, course, skill, ingred):
        # load in the recipe dataset
        df = pd.read_csv('clean_recipe2_5.csv',
                         converters={'ingredients_clean': literal_eval})

        # Defining the lemmatizer and stopwords list
        lemmatizer = WordNetLemmatizer()
        stpwrd = nltk.corpus.stopwords.words('english')
        stpwrd.extend(string.punctuation)

        ingred = ingred.lower()

        ingred = word_tokenize(ingred)

        ingred = [word for word in ingred if word not in stpwrd]

        ingred = [word for word in ingred if word.isalpha()]

        ingred = [lemmatizer.lemmatize(word) for word in ingred]

        # filter recipes to those less than or equal to users time
        recipe = df.loc[df['cook_time'] <= n]

        # filter by course type
        if course == 'starter':
            recipe = recipe[recipe['course'] == 'starter'].copy()
        elif course == 'main':
            recipe = recipe[recipe['course'] == 'main'].copy()
        elif course == 'dessert':
            recipe = recipe[recipe['course'] == 'dessert'].copy()

        # filter recipes to skill level
        if skill == 'beginner':
            recipe = recipe[recipe['skill_level'] == 'beginner'].copy()
        elif skill == 'intermediate':
            recipe = recipe[recipe['skill_level'] == 'intermediate'].copy()
        elif skill == 'advanced':
            recipe = recipe[recipe['skill_level'] == 'advanced'].copy()

        # filter recipes to only vegetarian or vegan
        if diet == 'vegetarian':
            recipe = recipe[recipe['vegetarian'] == 1].copy()
        elif diet == 'vegan':
            recipe = recipe[recipe['vegan'] == 1].copy()

        # matching ingredients between recipes and the users input
        recipe['match'] = recipe['ingredients_clean'].apply(lambda x: set(ingred).intersection(set(x)))
        recipe['count'] = recipe['match'].apply(lambda x: len(x))

        # sorting recipes by macth count and displaying top 5 matches
        recipe.sort_values(by='count', ascending=False, inplace=True)
        recipe = recipe[:5]

        recipe = recipe[['recipe_name', 'ingredients', 'recipe_urls', 'cook_time']]

        return recipe


    if submit:
        with st.spinner('Waiting...'):
            time.sleep(2)
        st.success('Get Cooking... 👨🏼‍🍳')

        recipe = suggest_recipes(diet, n, course, skill, ingred)
        recipe










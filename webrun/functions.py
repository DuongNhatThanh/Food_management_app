import sqlite3
from datetime import datetime, date

import pandas
import streamlit as st
from pretty_notification_box import notification_box
import pandas as pd
import altair as alt

connect = sqlite3.connect("database.db", check_same_thread=False)
cur = connect.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS calohistory (id INTEGER, foodname VARCHAR, foodcode VARCHAR, foodweight FLOAT,
            datetakeout VARCHAR)""")

nutrition = pd.read_csv("Nutrition.csv")
portion = pd.read_csv("Portion.csv")
foodchoice = nutrition['Main food description']


def get_data(tablename, category_find, data, category_select='*', convert_list=True, get_one=True):
    command = f'SELECT {category_select} FROM {tablename} WHERE {category_find} = ?'
    cur.execute(command, (data,))
    result = cur.fetchall()
    if convert_list:
        result = [list(i)[0] for i in result]
        if get_one:
            result = result[0]
    return result


def get_all_data(table_name):
    command = f'SELECT * FROM {table_name}'
    cur.execute(command)
    result = cur.fetchall()
    return result


def get_current_food(currentid, foodcode, foodexp, category_select='*', get_one=True):
    command = f"SELECT {category_select} FROM storage WHERE id =? AND foodcode=? AND exp=?"
    cur.execute(command, (currentid, foodcode, foodexp))
    result = cur.fetchall()
    result = [list(i)[0] for i in result]
    if get_one:
        result = result[0]
    return result


def check_signin(username, password):
    cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    result = cur.fetchall()
    return result


def take_out_food(currentid, foodcode, foodexp, foodweight):
    currentweight = get_current_food(currentid, foodcode, foodexp, 'foodweight')
    currentweight = currentweight - foodweight
    if currentweight > 0.01:
        cur.execute('UPDATE storage SET foodweight=? WHERE foodcode=? AND exp = ?', (currentweight, foodcode, foodexp))
        connect.commit()
    else:
        cur.execute("DELETE FROM storage WHERE id = ? AND foodcode = ? AND exp = ?", (currentid, foodcode, foodexp))
        connect.commit()


# test
def expiry_date(foodexp):
    today_date = date.today()
    time_gap = foodexp - today_date
    if time_gap.days < 0:
        expstatus = 'expired'
    else:
        expstatus = time_gap.days
    return expstatus


# color table
def color_coding(data):
    if data["Days Remained"].lower() == 'expired':
        color = '#eaa928'
    elif 0 <= int(data["Days Remained"]) <= 2:
        color = '#9dddb7'
    else:
        color = '#ffefd6'
    return [f'background-color: {color}'] * len(data)


# new: delete all expired
def delete_expired(currentid):
    currentdata = get_data(tablename='storage', category_find='id', data=currentid, convert_list=False)
    for i in currentdata:
        if i[-1].lower() == 'expired':
            cur.execute("DELETE FROM storage WHERE id = ? AND foodcode = ? AND exp = ?", (currentid, i[2], i[-2]))
            connect.commit()


# new: update days remained (when new day begins)
def update_days_remained(currentid):
    currentdata = get_data(tablename='storage', category_find='id', data=currentid, convert_list=False)
    for i in currentdata:
        exp = datetime.strptime(i[-2], "%Y-%m-%d").date()
        currentdayremained = expiry_date(exp)
        cur.execute('UPDATE storage SET expstatus=? WHERE id=? AND foodcode=? AND exp = ?',
                    (currentdayremained, currentid, i[2], exp))
        connect.commit()


# new: noti
def noti(currentdata):
    key = 0
    usernutrition = {'carbohydrates': 0,
                      'protein': 0,
                      'fat': 0,
                      'fibre': 0}
    for i in currentdata:
        key += 1
        if i[-1] == 'expired':
            notification_box(icon='warning', title='Warning',
                             textDisplay=f"{i[1]} has expired",
                             styles=None, key=key, externalLink=None, url=None)
        elif 0 <= int(i[-1]) <= 2:
            key += 1
            notification_box(icon='warning', title='Warning',
                             textDisplay=f"{i[1]} has {i[-1]} days left",
                             styles=None, key=key, externalLink=None, url=None)
        foodinfo = nutrition.loc[nutrition['Food code'] == i[2]].to_dict('records')[0]#.to_dict('records')[0]: chuyen 1 row trong dataframe ve dict, index row = 0
        usernutrition['carbohydrates'] += foodinfo['Carbohydrate (g)']*i[3]/100
        usernutrition['protein'] += foodinfo['Protein (g)'] * i[3] / 100
        usernutrition['fat'] += foodinfo['Total Fat (g)'] * i[3] / 100
        usernutrition['fibre'] += foodinfo['Fiber, total dietary (g)'] * i[3] / 100
    if usernutrition['carbohydrates'] < 310:
        key += 1
        notification_box(icon='warning', title='Warning',
                         textDisplay="Running out of carbohydrates",
                         styles=None, key=key, externalLink=None, url=None)
    if usernutrition['protein'] < 50:
        key += 1
        notification_box(icon='warning', title='Warning',
                         textDisplay="Running out of protein",
                         styles=None, key=key, externalLink=None, url=None)
    if usernutrition['fat'] < 70:
        key += 1
        notification_box(icon='warning', title='Warning',
                         textDisplay="Running out of fat",
                         styles=None, key=key, externalLink=None, url=None)
    if usernutrition['fibre'] < 30:
        key += 1
        notification_box(icon='warning', title='Warning',
                         textDisplay="Running out of fibre",
                         styles=None, key=key, externalLink=None, url=None)
def update_calo(currentid, calo):
    cur.execute("SELECT calo FROM usercalo WHERE id=? AND datetakeout=?", (currentid, date.today()))
    oldcalo = cur.fetchone()
    if not oldcalo:
        cur.execute("INSERT INTO usercalo VALUES (?,?,?)", (currentid, calo, date.today()))
        connect.commit()
    else:
        calo += oldcalo[0]
        cur.execute("UPDATE usercalo SET calo = ? WHERE id=? AND datetakeout=?", (calo, currentid, date.today()))
        connect.commit()


def visualization(currentid, date1, date2):
    cur.execute("SELECT datetakeout, calo FROM usercalo WHERE id=? AND datetakeout BETWEEN ? AND ? ",
                (currentid, date1, date2))
    calo1 = cur.fetchall()
    res_dict = {}
    date_list = []
    calo_list = []
    for option in calo1:
        date_list.append(option[0])
        calo_list.append(option[1])
    res_dict['Date'] = date_list
    res_dict['Calo'] = calo_list
    chart = alt.Chart(pd.DataFrame(res_dict)).mark_bar().encode(
        x='Date',
        y='Calo',
        color=alt.value("#eaa928")
    )
    chart_text = chart.mark_text().encode(text="Calo", color=alt.value("#0e5e6f"))#chua di chuyen duoc mark_text len phia tren
    st.altair_chart(chart + chart_text, use_container_width=True)


def calculatecalo(foodcode, currentid, i, food_removed, foodname):
    portion = pd.read_csv("Portion.csv")
    nutrion = pd.read_csv("Nutrition.csv")
    unitchoice_0 = portion.loc[portion['Food code'] == foodcode]
    unitchoice_0 = unitchoice_0.loc[unitchoice_0['weight'] != 0]['Descr']
    unitchoice = unitchoice_0.tolist()
    unitchoice.append('1 grams')
#with st.container():
    foodunit = st.selectbox('Choose the unit:', unitchoice, key=i + 1)
#with st.container():
    cur.execute('''SELECT exp FROM storage WHERE id=? AND foodcode=?''', (currentid, foodcode))
    expchoice = cur.fetchall()
    expchoice = [list(exp)[0] for exp in expchoice]
    foodexp = st.selectbox("EXP", expchoice, key=i+2)
#with st.container():
    cur.execute("SELECT foodweight FROM storage WHERE id=? AND foodcode=? AND exp=?",
                (currentid, foodcode, foodexp))
    foodweight_limit = cur.fetchall()
    foodweight_limit = list(foodweight_limit[0])[0]
    if foodunit != '1 grams':
        portionratio = portion.loc[(portion['Food code'] == foodcode) & (unitchoice_0 == foodunit)]
        foodweight_limit = foodweight_limit/int(portionratio['weight'])
    foodweight = st.number_input('Enter the number you want to have:', max_value=foodweight_limit, key=i + 3)
    if foodunit != '1 grams':
        portionratio = portion.loc[(portion['Food code'] == foodcode) & (unitchoice_0 == foodunit)]
        foodweight = int(portionratio['weight']) * foodweight
    nutri = nutrion.loc[nutrion['Food code'] == foodcode]
    temp = {'id': currentid, 'foodcode': foodcode, 'foodexp': foodexp, 'foodweight': foodweight, 'foodname': foodname}
    food_removed.append(temp)
    return foodweight, nutri, food_removed


def add(options, i, calo, protein, carb, fat, currentid, food_removed):
    foodcode = get_data(tablename='storage', category_find='foodname', category_select='foodcode', data=options)
    st.write('Product:', options)
    foodweight, nutri, food_removed = calculatecalo(foodcode, currentid, i, food_removed, options)
    calo += int(nutri['Energy']) * (foodweight / 100)
    protein += int(nutri['Protein (g)']) * (foodweight / 100)
    carb += int(nutri['Carbohydrate (g)']) * (foodweight / 100)
    fat += int(nutri['Total Fat (g)']) * (foodweight / 100)
    i += 3
    return calo, protein, carb, fat, i, food_removed


def finish(calo, protein, carb, fat):
    st.write(f'Total Calo: {round(calo)} kcal')
    st.write(f'Total Carb: {round(carb)} g')
    st.write(f'Total Protein: {round(protein)} g')
    st.write(f'Total Fat: {round(fat)} g')


def take_out(currentid):
    prd_data = set(get_data(tablename='storage', category_select='foodname', category_find='id',
                            data=currentid, get_one=False))
    gram, calo, protein, carb, fat, i = 0, 0, 0, 0, 0, 0
    food_removed = []
    multichoice = st.multiselect('Pick ingredients', prd_data)
    for options in multichoice:
        calo, protein, carb, fat, i, food_removed = add(options, i, calo, protein, carb, fat, currentid, food_removed)
    finish(calo, protein, carb, fat)
    if st.button('take out'):
        for i in food_removed:
            take_out_food(currentid=i['id'], foodcode=i['foodcode'], foodexp=i['foodexp'], foodweight=i['foodweight'])
        update_calo(currentid, calo)
        history(currentid, food_removed)
        st.experimental_rerun()


def add_new(currentid):
    foodname = st.selectbox("Ingredient", foodchoice)
    st.write(foodname)
    unitchoice = portion.loc[portion['Main food description'] == foodname]
    unitchoice = unitchoice.loc[unitchoice['weight'] != 0]['Descr'].tolist()
    unitchoice.append('1 grams')
    foodunit = st.selectbox("Unit", unitchoice)
    foodweight = st.number_input("Quantity", min_value=0.01)
    foodcode = nutrition.loc[nutrition['Main food description'] == foodname]['Food code'].tolist()[0]
    foodexp = st.date_input("Expiry Day")
    foodexpstatus = expiry_date(foodexp)
    submitted = st.button("add new")
    if submitted:
        if foodunit != '1 grams':
            portionratio = portion.loc[(portion['Main food description'] == foodname)]
            portionratio = portionratio.loc[portionratio['Descr'] == foodunit]['weight'].tolist()[0]
            foodweight = round(foodweight * portionratio)
        cur.execute("SELECT * FROM storage WHERE id = ? AND foodcode = ? AND exp = ?", (currentid,foodcode,foodexp))
        datacheck = cur.fetchall()

        if not datacheck:
            cur.execute(
                'INSERT INTO storage (id, foodname, foodcode, foodweight, exp, expstatus)'
                'VALUES (?, ?, ?, ?, ?, ?)',
                (currentid, foodname, foodcode, foodweight, foodexp, foodexpstatus))
            connect.commit()
        else:
            currentweight = list(datacheck[0])[-3]
            foodweight += currentweight
            foodweight = round(foodweight)
            # new: edit (foodweight, currentid, foodcode...) - old (currentid, foodweight, foodcode...)
            cur.execute('UPDATE storage SET foodweight=? WHERE id=? AND foodcode=? AND exp = ?',
                        (foodweight, currentid, foodcode, foodexp))
            connect.commit()
        st.experimental_rerun()


def history(currentid, foodremoved):
    # st.write(foodremoved)
    today_date = date.today()
    for i in foodremoved:
        if i['foodweight'] != 0:
            cur.execute(
                'INSERT INTO calohistory (id, foodname, foodcode, foodweight, datetakeout) VALUES (?, ?, ?, ?, ?)',
                (currentid, i['foodname'], i['foodcode'], i['foodweight'], today_date))
            connect.commit()


# def add_new(currentid):
#     # foodname = st.selectbox("Ingredient", foodchoice)
#     foodoptions = st.multiselect("Ingredient", foodchoice)
#     foodchosing = []
#     key = 1000000
#     for foodname in foodoptions:
#         st.write(foodname)
#         unitchoice = portion.loc[portion['Main food description'] == foodname]
#         unitchoice = unitchoice.loc[unitchoice['weight'] != 0]['Descr'].tolist()
#         unitchoice.append('1 grams')
#         foodunit = st.selectbox("Unit", unitchoice, key=key+1)
#         foodweight = st.number_input("Quantity", key=key+2)
#         foodcode = nutrition.loc[nutrition['Main food description'] == foodname]['Food code'].tolist()[0]
#         foodexp = st.date_input("Expiry Day", key=key+3)
#         foodexpstatus = expiry_date(foodexp)
#         temp = {'foodname': foodname, 'foodcode': foodcode, 'foodunit': foodunit,'foodweight': foodweight,
#                 'foodexp': foodexp, 'foodexpstatus': foodexpstatus}
#         foodchosing.append(temp)
#         key += 3
#
#     if st.button("Submit"):
#         for i in foodchosing:
#             if i['foodunit'] != '1 grams':
#                 portionratio = portion.loc[(portion['Main food description'] == i['foodname'])]
#                 portionratio = portionratio.loc[portionratio['Descr'] == foodunit]['weight'].tolist()[0]
#                 i['foodweight'] = i['foodweight'] * portionratio
#             cur.execute("SELECT * FROM storage WHERE id = ? AND foodcode = ? AND exp = ?", (currentid,
#                                                                                             i['foodcode'],
#                                                                                             i['foodexp']))
#             datacheck = cur.fetchall()
#             if not datacheck:
#                 cur.execute(
#                     'INSERT INTO storage (id, foodname, foodcode, foodweight, exp, expstatus)'
#                     'VALUES (?, ?, ?, ?, ?, ?)',
#                     (currentid, i['foodname'], i['foodcode'], i['foodweight'], i['foodexp'], i['foodexpstatus']))
#                 connect.commit()
#             else:
#                 currentweight = list(datacheck[0])[-3]
#                 i['foodweight'] += currentweight
#                 # new: edit (foodweight, currentid, foodcode...) - old (currentid, foodweight, foodcode...)
#                 cur.execute('UPDATE storage SET foodweight=? WHERE id=? AND foodcode=? AND exp = ?',
#                             (i['foodweight'], currentid, i['foodcode'], i['foodexp']))
#                 connect.commit()
#         st.experimental_rerun()
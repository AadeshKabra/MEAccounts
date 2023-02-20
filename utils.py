from flask_pymongo import pymongo
import pandas as pd
import datetime
import plotly.graph_objs as go
import plotly

mongo_client = pymongo.MongoClient("mongodb+srv://sagar:sagar@cluster0.gwnjuq6.mongodb.net/?retryWrites=true&w=majority", maxPoolSize=50, connect=False)
db = pymongo.database.Database(mongo_client, 'ME')


def get_raw_material_names():
    raw = mongo_client.db.raw_material
    raw_materials = []
    for i in raw.find({}, {"name": 1, "_id": 0}):
        if i['name']:
            raw_materials.append(i["name"])

    return raw_materials


def add_Employee(name, age, number, rate):
    employees = mongo_client.db.employees
    details = {
        "Name": name,
        "Age": age,
        "Contact": number,
        "Rate": rate
    }
    employees.insert_one(details)


def get_employee_names():
    employees = mongo_client.db.employees
    names = list(employees.find({}, {"Name": 1, "_id": 0}))
    list_names = []
    for i in range(len(names)):
        list_names.append(names[i]['Name'])
    # print(list_names)
    return list_names


def get_production_names():
    production = mongo_client.db.production
    names = list(production.find({}, {"Name": 1, "_id": 0}))
    list_names = []
    for i in names:
        list_names.append(i["Name"])
    # print(list_names)
    return list_names


def add_creditor(name, date, amount):
    doc = {
        date: float(amount)
    }
    document = {
        "Name": name,
        "30 Days": float(amount),
        "60 Days": 0,
        "90 Days": 0,
        "90 Onwards": 0,
        "Production": doc
    }
    creditors = mongo_client.db.creditors
    creditors.insert_one(document)


def release_due(document, name, amount):
    creditors = mongo_client.db.creditors
    if document["90 Onwards"] > 0:
        initial = document["90 Onwards"]
        count = float(initial) - float(amount)
        if count<0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        creditors.update_one({"Name": name}, {"$set": {"90 Onwards": count}})
    if document["90 Days"] > 0 and float(amount) > 0:
        initial = document["90 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        creditors.update_one({"Name": name}, {"$set": {"90 Days": count}})
    if document["60 Days"] > 0 and float(amount) > 0:
        initial = document["60 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        creditors.update_one({"Name": name}, {"$set": {"60 Days": count}})
    if document["30 Days"] > 0 and float(amount) > 0:
        initial = document["30 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        creditors.update_one({"Name": name}, {"$set": {"30 Days": count}})


def add_debitor(name, amount, date):
    doc = {
        date: amount
    }
    document = {
        "Name": name,
        "30 Days": float(amount),
        "60 Days": 0,
        "90 Days": 0,
        "90 Onwards": 0,
        "Dates": doc
    }
    debitors = mongo_client.db.debitors
    debitors.insert_one(document)


def release_outstanding(document, name, amount):
    debitors = mongo_client.db.debitors
    if document["90 Onwards"] > 0:
        initial = document["90 Onwards"]
        count = float(initial) - float(amount)
        if count<0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        debitors.update_one({"Name": name}, {"$set": {"90 Onwards": count}})
    if document["90 Days"] > 0 and float(amount) > 0:
        initial = document["90 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        debitors.update_one({"Name": name}, {"$set": {"90 Days": count}})
    if document["60 Days"] > 0 and float(amount) > 0:
        initial = document["60 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        debitors.update_one({"Name": name}, {"$set": {"60 Days": count}})
    if document["30 Days"] > 0 and float(amount) > 0:
        initial = document["30 Days"]
        count = float(initial) - float(amount)
        if count < 0:
            amount = abs(count)
            count = 0
        else:
            amount = 0
        debitors.update_one({"Name": name}, {"$set": {"30 Days": count}})


def view_raw_material_sheet():
    raw = mongo_client.db.raw_material
    items = mongo_client.db.prodItems
    production = mongo_client.db.production

    groups = {}
    documents = items.find({})
    for doc in documents:
        raw_material = doc['RawMaterial']
        name = doc['Name']

        if raw_material in groups:
            groups[raw_material].append(name)
        else:
            groups[raw_material] = [name]

    list_quantity = {}
    for i in groups:
        total_quantity = 0
        for j in groups[i]:
            document = production.find_one({"Name": j})
            total_quantity += float(document['Kgs'])
        list_quantity[i] = total_quantity

    names = list(raw.find({}, {"name": 1, "_id": 0}))
    list_names = []
    for i in names:
        list_names.append(i['name'])

    list_issued = []
    for i in list_names:
        if i not in list_quantity:
            list_issued.append(0)
        else:
            list_issued.append(list_quantity[i])

    units = list(raw.find({}, {"units": 1, "_id": 0}))
    list_units = []
    for i in units:
        list_units.append(i['units'])

    opening = list(raw.find({}, {"opening": 1, "_id": 0}))
    list_opening = []
    for i in opening:
        list_opening.append(float(i['opening']))

    received = list(raw.find({}, {"received": 1, "_id": 0}))
    list_received = []
    for i in received:
        list_received.append(float(i['received']))

    rate = list(raw.find({}, {"rate": 1, "_id": 0}))
    list_rate = []
    for i in rate:
        list_rate.append(float(i['rate']))

    bal = []
    for i in range(len(list_opening)):
        bal.append(float(list_opening[i]) + float(list_received[i]) - float(list_issued[i]))

    opening_value = []
    received_value = []
    issued_value = []
    for i in range(len(list_rate)):
        opening_value.append(float(list_opening[i]) * float(list_rate[i]))
        received_value.append(float(list_received[i]) * float(list_rate[i]))
        issued_value.append(float(list_issued[i]) * float(list_rate[i]))

    data = pd.DataFrame(list(
        zip(list_names, list_units, list_opening, list_received, list_issued, bal, list_rate, opening_value,
            received_value, issued_value)),
                        columns=['Description', 'UNITS', 'OPENING', 'RECEIVED', 'ISSUED', 'BALANCE', 'RATE',
                                 'OPENING by Value', 'RECEIVED by Value', 'ISSUED by Value'])

    data['BALANCE by Value'] = data['BALANCE'] * data['RATE']

    data_total = data.append(data.sum(axis=0), ignore_index=True)

    # Set the name of the last row to "Total"
    data_total.loc[data_total.index[-1], 'Description'] = "Total"
    data_total.loc[data_total.index[-1], 'UNITS'] = ""
    data_total.loc[data_total.index[-1], 'RATE'] = ""
    data_total.style.set_properties(subset=['Description'], **{'font-weight': 'bold'})
    return data_total

def add_new_prod_item(name, weight, raw, rate):
    prodItems = mongo_client.db.prodItems
    item = {
        "Name": name,
        "Weight": weight,
        "RawMaterial": raw,
        "Rate": rate
    }
    prodItems.insert_one(item)
    items = []
    for i in prodItems.find({}, {"Name": 1}):
        items.append(i['Name'])
    print(items)
    return items


def view_production_sheet():
    # print("Production report")
    # app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    raw_material = mongo_client.db.raw_material
    items = mongo_client.db.prodItems
    production = mongo_client.db.production

    documents = raw_material.find({}, {"name": 1})
    raw_materials = []
    for doc in documents:
        raw_materials.append(doc['name'])
    print(raw_materials)

    groups = {}
    documents = items.find({})
    for doc in documents:
        raw_material = doc['RawMaterial']
        name = doc['Name']

        if raw_material in groups:
            groups[raw_material].append(name)
        else:
            groups[raw_material] = [name]

    print(groups)
    list_quantity = {}
    for i in groups:
        total_quantity = 0
        for j in groups[i]:
            document = production.find_one({"Name": j})
            total_quantity += float(document['Kgs'])
        list_quantity[i] = total_quantity
    print("List Quantity", list_quantity)

    raw_material_data = []
    prod_items = []
    prod_docs = production.find({}, {"Name": 1, "_id": 0})
    for prod_doc in prod_docs:
        prod_items.append(prod_doc['Name'])
    for i in prod_items:
        doc = items.find_one({"Name": i})
        raw_material_data.append(doc['RawMaterial'])

    quantity_data = []
    for i in list_quantity:
        quantity_data.append(list_quantity[i])

    list_items = []
    items = production.find({}, {"Name": 1, "_id": 0})
    for item in items:
        list_items.append(item['Name'])

    dic_production = {}
    day_by_day_production = production.find({}, {"Name": 1, "Production": 1, "_id": 0})
    for i in day_by_day_production:
        dic_production[i['Name']] = i['Production']

    kgs = []
    quantities = production.find({}, {"Name": 1, "Kgs": 1, "_id": 0})
    for quantity in quantities:
        kgs.append(quantity['Kgs'])

    items = mongo_client.db.prodItems
    weights = []
    for item in list_items:
        item_weight = items.find_one({"Name": item})
        weights.append(item_weight['Weight'])

    data1 = pd.DataFrame(list(zip(list_items, weights, raw_material_data, kgs)), columns=['Items', 'Weight', 'Raw Material used', 'Quantity (Kgs)'])

    data2 = pd.DataFrame(dic_production)
    data2 = data2.transpose()
    data2 = data2.reset_index()
    data2.drop(['index'], axis=1, inplace=True)
    data2 = data2.reset_index()

    data2 = data2.drop(['index'], axis=1)
    data2['Total'] = data2.sum(axis=1)

    result = pd.concat([data1, data2], axis=1, join='outer')
    list_total = []
    for i in dic_production:
        total = 0
        for j in dic_production[i]:
            total += float(dic_production[i][j])
        list_total.append(total)
    print(list_total)
    result['Total'] = list_total

    # Dataframe 2
    raw = []
    for i in groups:
        raw.append(i)
    print(raw)
    data3 = pd.DataFrame(list(zip(raw, quantity_data)), columns=['Raw Material', 'Quantity of material used'])

    return result, data3


def view_attendance_sheet():
    attendance = mongo_client.db.attendance
    employees = mongo_client.db.employees
    names = list(attendance.find({}, {"Name": 1, "_id": 0}))
    # print(names)
    employee_names = []
    for i in names:
        employee_names.append(i['Name'])
    attend = list(attendance.find({}, {"Attendance": 1, "_id": 0}))
    print(attend)
    data1 = pd.DataFrame(employee_names, columns=['Name of Employee'])
    data2 = pd.DataFrame()
    for i in range(len(employee_names)):
        temp_data = pd.DataFrame([attend[i]["Attendance"]])
        data2 = data2.append(temp_data, ignore_index=True)
    print(data2)

    data = pd.concat([data1, data2], axis=1)
    data['Total'] = data.sum(axis=1)

    rate = list(employees.find({}, {"Rate": 1, "_id": 0}))
    print(rate)
    list_rate = []
    for i in rate:
        list_rate.append(float(i["Rate"]))

    temp_data = pd.DataFrame(list_rate, columns=["Rate"])
    data = pd.concat([data, temp_data], axis=1)
    data['Days'] = data['Total'] / 8
    data["Net Amount"] = data["Days"] * data["Rate"]

    return data


def view_dispatch_sheet():
    items = mongo_client.db.prodItems
    dispatch = mongo_client.db.dispatch
    schedule = mongo_client.db.schedule
    prodItems = mongo_client.db.prodItems
    names_list = []
    schedule_list = []
    dispatch_list = []
    total_list = []
    po_rate_list = []
    documents = dispatch.find({})
    # print(documents)
    for doc in documents:
        # print(doc)
        names_list.append(doc["Name"])
        name = doc["Name"]
        sch_doc = schedule.find_one({"Name": name})
        schedule_list.append(sch_doc["Schedule"])
        dispatch_list.append(doc["Dispatch"])
        item_doc = prodItems.find_one({"Name":name})
        po_rate_list.append(item_doc["Rate"])

    print(names_list)
    print(schedule_list)
    print(dispatch_list)

    d = {}
    for i, item in enumerate(names_list):
        d[item] = dispatch_list[i]

    days = len(dispatch_list[0])
    # create the dataframe
    df = pd.DataFrame.from_dict(d, orient='index')
    df.index.name = 'Name'
    df.columns = ['Schedule'] + list(range(1, days))

    # add the values from l2
    df['Schedule'] = schedule_list
    total = []
    for i in range(len(dispatch_list)):
        sum1 = 0
        for j in dispatch_list[i]:
            sum1 += dispatch_list[i][j]
        total.append(sum1)

    df["Total"] = total

    return df



def view_creditors_sheet():
    creditors = mongo_client.db.creditors

    list_names = []
    names = creditors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i['Name'])

    list_30 = []
    for i in creditors.find({}, {"30 Days": 1, "_id": 0}):
        list_30.append(i['30 Days'])

    list_60 = []
    for i in creditors.find({}, {"60 Days": 1, "_id": 0}):
        list_60.append(i['60 Days'])

    list_90 = []
    for i in creditors.find({}, {"90 Days": 1, "_id": 0}):
        list_90.append(i['90 Days'])

    list_90_onwards = []
    for i in creditors.find({}, {"90 Onwards": 1, "_id": 0}):
        list_90_onwards.append(i['90 Onwards'])

    data = pd.DataFrame(list(zip(list_names, list_30, list_60, list_90, list_90_onwards)),
                        columns=['Name', '30 Days', '60 Days', '90 Days', '90 Onwards'])

    data['Total'] = data.sum(axis=1)
    return data


def view_debitors_sheet():
    debitors = mongo_client.db.debitors
    list_names = []
    names = debitors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i['Name'])

    list_30 = []
    for i in debitors.find({}, {"30 Days": 1, "_id": 0}):
        list_30.append(i['30 Days'])

    list_60 = []
    for i in debitors.find({}, {"60 Days": 1, "_id": 0}):
        list_60.append(i['60 Days'])

    list_90 = []
    for i in debitors.find({}, {"90 Days": 1, "_id": 0}):
        list_90.append(i['90 Days'])

    list_90_onwards = []
    for i in debitors.find({}, {"90 Onwards": 1, "_id": 0}):
        list_90_onwards.append(i['90 Onwards'])

    data = pd.DataFrame(list(zip(list_names, list_30, list_60, list_90, list_90_onwards)),
                        columns=['Name', '30 Days', '60 Days', '90 Days', '90 Onwards'])

    data['Total'] = data.sum(axis=1)

    return data


def view_finish_sheet():
    items = mongo_client.db.prodItems
    production = mongo_client.db.production
    dispatch = mongo_client.db.dispatch
    opening = mongo_client.db.opening

    list_names = []
    for i in items.find({}, {"Name": 1, "_id": 0}):
        list_names.append(i['Name'])
    print(list_names)

    list_opening = []
    for i in list_names:
        document = opening.find_one({"Name": i})
        if document:
            list_opening.append(float(document["Opening"]))
        else:
            list_opening.append(0)
    print(list_opening)

    list_production = []
    for i in list_names:
        total = 0
        document = production.find_one({"Name": i})
        if document:
            pro_dic = document["Production"]
            for j in pro_dic:
                total += float(pro_dic[j])
            list_production.append(total)
        else:
            list_production.append(0)

    list_dispatch = []
    for i in list_names:
        total = 0
        document = dispatch.find_one({"Name": i})
        if document:
            dis_dic = document["Dispatch"]

            for j in dis_dic:
                total += float(dis_dic[j])
            list_dispatch.append(total)
        else:
            list_dispatch.append(0)

    rates = []
    for i in list_names:
        document = items.find_one({"Name": i})
        if document:
            rates.append(float(document["Rate"]))
        else:
            rates.append(0)

    data = pd.DataFrame(list(zip(list_names, list_opening, list_production, list_dispatch, rates)),
                        columns=['Item Description', 'Opening', 'Production', 'Dispatched', 'Rate'])

    data['Opening Value'] = data['Opening'] * data['Rate']
    data['Production Value'] = data['Production'] * data['Rate']
    data['Dispatched Value'] = data['Dispatched'] * data['Rate']

    row_sum = data.sum(numeric_only=True)

    data = data.append(row_sum, ignore_index=True)

    data.at[len(data) - 1, 'Item Description'] = 'Total'
    data.at[len(data) - 1, 'Rate'] = 0

    return data


def production_graph():
    df1, df2 = view_production_sheet()

    total = df1['Total'].tolist()
    items = df1['Items'].tolist()

    data = [go.Bar(x=items, y=total)]
    layout = go.Layout(title='Production of different items', xaxis=dict(title='Production Items'), yaxis=dict(title='Production Quantity'), width=600)
    fig = go.Figure(data=data, layout=layout)
    plot_div1 = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

    raw_material = df2['Raw Material']
    quantity = df2['Quantity of material used']
    data = [go.Bar(x=raw_material, y=quantity)]
    layout = go.Layout(title='Raw Material Consumption', xaxis=dict(title='Raw Material'), yaxis=dict(title='Consumption'), width=600)
    fig = go.Figure(data=data, layout=layout)
    plot_div2 = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

    return plot_div1, plot_div2


def create_pie_chart(list1, list2, name):
    data = [go.Pie(labels=list1, values=list2)]
    fig = go.Figure(data=data)
    fig.update_layout(title=name, width=600)
    plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    return plot_div


def production_pie():
    df1, df2 = view_production_sheet()
    total = df1['Total'].tolist()
    items = df1['Items'].tolist()
    plot_div = create_pie_chart(items, total, "Production Pie")
    return plot_div


def creditors_pie():
    df = view_creditors_sheet()
    names = df['Name'].tolist()
    total = df['Total'].tolist()
    plot_div = create_pie_chart(names, total, "Creditors Pie")
    return plot_div


def debitors_pie():
    df = view_debitors_sheet()
    names = df['Name'].tolist()
    total = df['Total'].tolist()
    plot_div = create_pie_chart(names, total, "Debitors Pie")
    return plot_div


def dispatch_graph():
    df = view_finish_sheet()
    names = df['Item Description'].tolist()[:-1]
    dispatch = df['Dispatched'].tolist()[:-1]
    data = [go.Bar(x=names, y=dispatch)]
    layout = go.Layout(title='Dispatch', xaxis=dict(title='Produced Items'), yaxis=dict(title='Dispatched'), width=600)
    fig = go.Figure(data=data, layout=layout)
    plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    return plot_div


def raw_dispatch_graph():
    df1 = view_raw_material_sheet()
    raw_material_value = (df1['OPENING by Value'][:-1] + df1['RECEIVED by Value'][:-1]).tolist()
    print("Raw Material Value", raw_material_value)
    items = mongo_client.db.prodItems
    dispatch = mongo_client.db.dispatch
    result = items.find({}, {"Name": 1, "RawMaterial": 1, "_id": 0})
    temp = []
    for record in result:
        temp.append([record["Name"], record["RawMaterial"]])
        # print(record)
    print("Temporary list: ", temp)

    raw_names = df1['Description'].tolist()[:-1]
    print("Raw Material: ", raw_names)


    temp_dic = {}
    for raw in raw_names:
        temp_dic[raw] = []

    for i in temp:
        name = i[1]
        temp_dic[name].append(i[0])
    print("Temp Dic: ", temp_dic)

    raw_dic = {}
    for raw in raw_names:
        raw_dic[raw] = 0

    production_value = []

    for raw in temp_dic:
        total_value = 0
        for item in temp_dic[raw]:
            rate = items.find_one({"Name": item})["Rate"]
            dispatch_res = dispatch.find_one({"Name": item})
            sum1 = 0
            if dispatch_res:
                dispatch_dic = dispatch_res["Dispatch"]
                sum1 += sum(dispatch_dic.values())
            total_value += (int(sum1)*int(rate))
        production_value.append(total_value)


    # print("Production Value: ", production_value)
    data = [go.Bar(x=raw_names, y=raw_material_value, name='Raw Material Value', marker=dict(color='red')), go.Bar(x=raw_names, y=production_value, name='Production Value', marker=dict(color='green'))]

    layout = go.Layout(title='Production and Raw Material Value Comparison', xaxis=dict(title='Raw Material'), yaxis=dict(title='Value (Rs.)'))

    fig = go.Figure(data=data, layout=layout)
    plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    return plot_div


def attendance_graph():
    df = view_attendance_sheet()
    attendance = mongo_client.db.attendance
    names = df['Name of Employee'].tolist()
    att_dic = {}
    for i in names:
        res = attendance.find_one({"Name": i})
        att_dic[i] = res["Attendance"]

    # print(att_dic)
    traces = []
    for key, values in att_dic.items():
        trace = go.Scatter(x=list(values.keys()), y=list(values.values()), name=key)
        traces.append(trace)

    layout = go.Layout(title='Attendance over Days', xaxis=dict(title='Days'), yaxis=dict(title='Attendance'))

    fig = go.Figure(data=traces, layout=layout)
    plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    return plot_div


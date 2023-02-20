from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file
import pandas as pd
from utils import *
from datetime import datetime
import os
from pymongo import MongoClient
import datetime
from gridfs import GridFS
import io

# 101

app = Flask(__name__)
app.config["SECRET_KEY"] = "013a658d9c8323f8e0af1f8ba8b4bcf30456a4c0"
app.config["MONGO_URI"] = "mongodb+srv://sagar:sagar@cluster0.gwnjuq6.mongodb.net/?retryWrites=true&w=majority"


employee_names = []

current_month = datetime.datetime.now().strftime("%B")
current_year = datetime.datetime.now().year

mongo_client = pymongo.MongoClient("mongodb+srv://sagar:sagar@cluster0.gwnjuq6.mongodb.net/?retryWrites=true&w=majority", maxPoolSize=50, connect=False)
db = pymongo.database.Database(mongo_client, 'ME')
users = pymongo.collection.Collection(db, 'users')

file_path = "static/" + str(current_month) + str(current_year) + ".xlsx"
writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

# Raw Material Section


# Displaying raw material page
@app.route("/raw_material", methods=['GET'])
def raw_material():
    return render_template("rawMaterial.html")


# Displaying page for insertion of raw material
@app.route("/insert_raw", methods=["POST"])
def insert():
    return render_template("insert.html")


# Insertion of raw material
@app.route("/insert_raw_material", methods=['POST', 'GET'])
def insert_raw():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    raw = mongo_client.db.raw_material
    element = {
        "name": request.form.get("raw_name"),
        "units": request.form.get("units"),
        "opening": request.form.get("opening"),
        "received": request.form.get("received"),
        "rate": request.form.get("rate")
    }
    document = raw.find_one({"name": request.form.get("raw_name")})
    if document:
        print("Raw Material exists")
        return render_template("rawMaterial.html", insertMessage=True)
    else:
        raw.insert_one(element)
        return render_template("index.html")

    return render_template("index.html")


# Displaying page for updating of raw material
@app.route("/update_raw", methods=['POST'])
def update():
    list_names = []
    raw = mongo_client.db.raw_material
    documents = raw.find({})
    for i in documents:
        list_names.append(i["name"])
    return render_template("update.html", raw_materials=list_names)


# Updating the raw material
@app.route("/update_raw_material", methods=['POST', 'GET'])
def update_raw():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    raw = mongo_client.db.raw_material
    u_name = request.form.get("item")
    u_received = request.form.get("received")
    u_rate = request.form.get("rate")
    original = list(raw.find({
        "name": {"$eq": u_name}
    }))
    received = int(u_received) + int(original[0]['received'])
    rate = float(float(u_rate) + float(original[0]['rate'])) / 2
    print(original[0])
    raw.find_one_and_update({"name": u_name}, {"$set": {"received": received, "rate": rate}})

    return render_template("index.html")


# Displaying the report of raw material
@app.route("/open_raw", methods=['GET'])
def view():
    data_total = view_raw_material_sheet()

    table = data_total.to_html()
    return render_template("view.html", table=table)


# Production section

# Displaying the production page
@app.route("/production", methods=['POST', 'GET'])
def prod():
    return render_template("production.html")


# Displaying page of insertion of production item
@app.route("/insertItem", methods=['POST', 'GET'])
def insertItem():
    raw_materials = get_raw_material_names()
    return render_template("insertItem.html", raw_materials=raw_materials)


# Inserting new production item
@app.route("/newProd", methods=['POST'])
def newProd():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"

    name = request.form.get("name")
    weight = request.form.get("weight")
    raw = request.form.get("raw")
    rate = request.form.get("rate")
    items = add_new_prod_item(name, weight, raw, rate)
    prodItems = mongo_client.db.prodItems
    list1 = []
    items_res = prodItems.find({}, {"Name": 1})
    for i in items_res:
        list1.append(i["Name"])
    # return render_template("updateProd.html", items=items)
    return render_template("Dispatch/schedule.html", items=list1)

# Displaying the page for updation of production item
@app.route("/updateProd", methods=['POST', 'GET'])
def updateProd():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    prodItems = mongo_client.db.prodItems
    production_items = list(prodItems.find({}, {"_id": 0, "Name": 1}))
    list_prod_items = []
    for i in range(len(production_items)):
        list_prod_items.append(production_items[i]['Name'])
    print(list_prod_items)
    return render_template("updateProd.html", items=list_prod_items)


# Updating production item
@app.route("/uProduction", methods=['POST', 'GET'])
def uProduction():
    date = request.form.get("date")
    item = request.form.get("item")
    quantity = request.form.get("prodQuan")
    print(date, item, quantity)
    day = int(date[8] + date[9])
    month = int(date[5] + date[6])
    odd = True
    if month not in [1, 3, 5, 7, 8, 10, 12]:
        odd = False
    print(day, month)
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    production = mongo_client.db.production
    items = mongo_client.db.prodItems

    cursor = production.find_one({"Name": item})
    if cursor:
        print("Document exists")
        doc = cursor['Production']
        initial = doc[str(day)]
        count = int(initial) + int(quantity)
        cursor['Production'][str(day)] = count

        doc_del = production.find_one({"Name": item})

        doc_item = items.find_one({"Name": item})
        weight = float(doc_item['Weight'])
        total_quantity = 0
        if odd:
            for i in range(1, 32):
                total_quantity += int(cursor['Production'][str(i)])
        else:
            for i in range(1, 31):
                total_quantity += int(cursor['Production'][str(i)])
        kgs = weight * total_quantity
        cursor["Kgs"] = kgs

        production.delete_one(doc_del)
        production.insert_one(cursor)
    else:
        print("Document does not exist")
        doc = {}
        if odd:
            for i in range(1, 32):
                if day == i:
                    doc[str(i)] = quantity
                else:
                    doc[str(i)] = 0
        else:
            for i in range(1, 31):
                if day == i:
                    doc[str(i)] = quantity
                else:
                    doc[str(i)] = 0

        document = {
            "Name": item,
            "Production": doc
        }

        doc_item = items.find_one({"Name": item})
        weight = float(doc_item['Weight'])
        total_quantity = 0
        if odd:
            for i in range(1, 32):
                total_quantity += int(document['Production'][str(i)])
        else:
            for i in range(1, 31):
                total_quantity += int(document['Production'][str(i)])

        print("Weight", weight)
        print("Quantity", total_quantity)
        kgs = weight * total_quantity
        print("Kgs", kgs)
        document["Kgs"] = kgs
        production.insert_one(document)

    return render_template("index.html")


# Displaying report of production
@app.route("/viewProd", methods=['POST', 'GET'])
def viewProduction():
    result1, result2 = view_production_sheet()

    table1 = result1.to_html()
    table2 = result2.to_html()

    return render_template("prodView.html", report1=table1, report2=table2)


# TRAUB Attendance section

# Displaying employees page
@app.route("/attendanceT", methods=['POST', 'GET'])
def attendanceT():
    return render_template("Employees/employees.html")


# Displaying the page for adding new employee
@app.route("/addE", methods=['POST'])
def addE():
    return render_template("Employees/addEmploy.html")


# Adding new employee
@app.route("/addEmployee", methods=['POST'])
def add_employee():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"

    name = request.form.get("eName")
    age = request.form.get("eAge")
    number = request.form.get("eNumber")
    rate = request.form.get("eRate")
    add_Employee(name, age, number, rate)
    global employee_names
    employee_names.append(name)
    return render_template("Employees/employees.html")


# Displaying page for marking the attendance of employee
@app.route("/markE", methods=['POST'])
def markEmployee():
    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/ME"
    list_names = get_employee_names()
    return render_template("Employees/markEmployee.html", employees=list_names)


# Marking the attendance of employee
@app.route("/attendance", methods=['POST'])
def attendance():
    date = request.form.get("date")
    hours = request.form.getlist("hours")
    employees = mongo_client.db.employees
    names = list(employees.find({}, {"Name": 1, "_id": 0}))
    list_names = []
    for i in range(len(names)):
        list_names.append(names[i]['Name'])

    day = int(date[8] + date[9])
    month = int(date[5] + date[6])

    odd = [1, 3, 5, 7, 8, 10, 12]
    attend = mongo_client.db.attendance
    for i in range(len(list_names)):
        a_doc = attend.find_one({"Name": list_names[i]})
        if a_doc:
            doc_del = attend.find_one({"Name": list_names[i]})
            dic = doc_del["Attendance"]
            dic[str(day)] = int(hours[i])
            attend.update_one({"Name": list_names[i]}, {"$set": {"Attendance": dic}})
        else:
            document = {
                "Name": list_names[i],
            }
            doc = {}
            if month in odd:
                for j in range(1, 32):
                    if j == day:
                        doc[str(day)] = int(hours[i])
                    else:
                        doc[str(j)] = 0
            else:
                for j in range(1, 31):
                    if j == day:
                        doc[str(day)] = int(hours[i])
                    else:
                        doc[str(j)] = 0
            document["Attendance"] = doc
            attend.insert_one(document)
    return render_template("Employees/employees.html")


# Displaying the page for removal of employee
@app.route("/removeE", methods=['POST'])
def removeE():
    return render_template("Employees/removeEmployee.html")


# Removing employee
@app.route("/remove", methods=['POST'])
def remove():
    name = request.form.get("name")
    employees = mongo_client.db.employees
    employees.delete_one({"Name": name})
    return render_template("Employees/employees.html")


# Displaying attendance report
@app.route("/viewAttendance", methods=['POST'])
def viewAttendance():
    data = view_attendance_sheet()

    table = data.to_html()
    return render_template("Employees/viewAttendance.html", table=table)


# Dispatch section


@app.route("/dispatch", methods=['GET'])
def dispatchProduction():
    return render_template("Dispatch/dispatch.html")


@app.route("/dispatchInsert", methods=["GET"])
def dispatchInsert():
    list_names = get_production_names()
    return render_template("Dispatch/insertDispatch.html", items=list_names)


flag = True


@app.route("/updateDispatch", methods=['POST'])
def updateDispatch():
    name = request.form.get("item")
    date = request.form.get("date")
    quantity = request.form.get("quantity")
    items = mongo_client.db.prodItems
    dispatch = mongo_client.db.dispatch
    # print(name, date)
    day = int(date[8] + date[9])
    month = int(date[5] + date[6])
    odd = [1, 3, 5, 7, 8, 10, 12]

    names = list(items.find({}, {"Name": 1, "_id": 0}))
    list_names = []
    for i in names:
        list_names.append(i['Name'])

    doc = dispatch.find_one({"Name": name})
    if doc:
        dispatch_dic = doc["Dispatch"]
        initial = dispatch_dic[str(day)]
        count = int(initial) + int(quantity)
        dispatch_dic[str(day)] = count
        dispatch.update_one({"Name": name}, {"$set": {"Dispatch": dispatch_dic}})
    else:
        for i in list_names:
            document = {
                "Name": i,
                "Quantity": 0
            }
            doc = {}
            if month in odd:
                for j in range(1, 32):
                    doc[str(j)] = 0
            else:
                for j in range(1, 31):
                    doc[str(j)] = 0
            document["Dispatch"] = doc

            dispatch.insert_one(document)

        document = dispatch.find_one({"Name": name})
        # document["Dispatch"][str(day)] = quantity
        dispatch_dic = document['Dispatch']
        dispatch_dic[str(day)] = int(quantity)
        dispatch.update_one({"Name": name}, {"$set": {"Dispatch": dispatch_dic}})

    return render_template("Dispatch/dispatch.html")


@app.route("/updateSchedule", methods=['GET'])
def schedule():
    list_names = get_production_names()
    return render_template("Dispatch/schedule.html", items=list_names)


@app.route("/insertSchedule", methods=['POST'])
def insertSchedule():
    name = request.form.get("item")
    quantity = request.form.get("schedule")
    schedule = mongo_client.db.schedule
    document = {
        "Name": name,
        "Schedule": quantity
    }
    schedule.insert_one(document)
    prodItems = mongo_client.db.prodItems
    items_res = prodItems.find({}, {"Name": 1})
    list_names = []
    for i in items_res:
        list_names.append(i["Name"])

    return render_template("updateProd.html", items=list_names)


@app.route("/viewScheduleReport", methods=['post'])
def view_report():
    data = view_dispatch_sheet()

    table = data.to_html()

    return render_template("Dispatch/viewReport.html", table=table)


# Creditors Section

# Displaying Creditors Section
@app.route("/creditors", methods=['GET'])
def creditors():
    return render_template("Creditors/creditors.html")


# Displaying page for adding creditors
@app.route("/addCreditor", methods=['POST'])
def addCreditor():
    return render_template("Creditors/addCreditor.html")


# Adding Creditor
@app.route("/aCreditor", methods=['POST'])
def aCreditor():
    name = request.form.get("name")
    date = request.form.get("date")
    amount = request.form.get("amount")
    add_creditor(name, date, amount)
    return render_template("Creditors/creditors.html")


# Displaying page for adding new Due amount
@app.route("/addDue", methods=['POST'])
def addDue():
    list_names = []
    creditors = mongo_client.db.creditors
    names = creditors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i["Name"])

    return render_template("Creditors/addDue.html", creditors=list_names)


# Adding new Due amount
@app.route("/aDue", methods=['POST'])
def aDue():
    name = request.form.get("name")
    amount = request.form.get("amount")
    date = request.form.get("date")
    creditors = mongo_client.db.creditors
    document = creditors.find_one({"Name": name})
    doc = document['Production']

    today = datetime.date.today().strftime('%Y-%m-%d')

    date1 = datetime.datetime.strptime(date, '%Y-%m-%d')
    date2 = datetime.datetime.strptime(today, '%Y-%m-%d')
    difference = (date1 - date2).days

    difference = abs(difference)
    if difference <= 30:
        initial = document["30 Days"]
        count = float(initial) + float(amount)
        creditors.update_one({"Name": name}, {"$set": {"30 Days": count}})
    elif difference <= 60:
        initial = document["60 Days"]
        count = float(initial) + float(amount)
        creditors.update_one({"Name": name}, {"$set": {"60 Days": count}})
    elif difference <= 90:
        initial = document["90 Days"]
        count = float(initial) + float(amount)
        creditors.update_one({"Name": name}, {"$set": {"90 Days": count}})
    else:
        initial = document["90 Onwards"]
        count = float(initial) + float(amount)
        creditors.update_one({"Name": name}, {"$set": {"90 Onwards": count}})


    if date in doc:
        initial = float(doc['Production'][date])
        count = initial + float(amount)
        creditors.update_one({"Name": name}, {"$set": {"Production." + date: count}})
    else:
        creditors.update_one({"Name": name}, {"$set": {"Production." + date: float(amount)}})

    return render_template("Creditors/creditors.html")


# Displaying page for releasing new amount
@app.route("/releaseDue", methods=['POST'])
def releaseDue():
    list_names = []
    creditors = mongo_client.db.creditors
    names = creditors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i["Name"])
    return render_template("Creditors/releaseDue.html", creditors=list_names)


# Releasing amount
@app.route("/rDue", methods=['POST'])
def rDue():
    name = request.form.get("name")
    amount = request.form.get("amount")
    creditors = mongo_client.db.creditors
    document = creditors.find_one({"Name": name})
    release_due(document, name, amount)
    return render_template("Creditors/creditors.html")


# Displaying page for creditors report
@app.route("/viewCreditors", methods=['POST'])
def viewCreditors():
    data = view_creditors_sheet()

    table = data.to_html()

    return render_template("Creditors/viewCreditors.html", table=table)


# Debitors Section

# Displaying debitors page
@app.route("/debitors", methods=['GET'])
def debitors():
    return render_template("Debitors/debitors.html")


# Displaying page for adding new debitor
@app.route("/addDebitor", methods=['POST'])
def addDebitor():
    return render_template("Debitors/addDebitor.html")


# Adding new Debitor
@app.route("/aDebitor", methods=['POST'])
def aDebitor():
    name = request.form.get("name")
    date = request.form.get("date")
    amount = request.form.get("amount")
    add_debitor(name, amount, date)
    return render_template("Debitors/debitors.html")


# Displaying page for adding outstanding
@app.route("/addOutstanding", methods=['POST'])
def addOutstanding():
    debitors = mongo_client.db.debitors
    list_names = []
    names = debitors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i["Name"])
    return render_template("Debitors/addOutstanding.html", debitors=list_names)


# Adding outstanding amount
@app.route("/aOutstanding", methods=['POST'])
def aOutstanding():
    debitors = mongo_client.db.debitors
    name = request.form.get("name")
    date = request.form.get("date")
    amount = request.form.get("amount")
    document = debitors.find_one({"Name": name})
    doc = document['Dates']

    today = datetime.today().strftime('%Y-%m-%d')

    date1 = datetime.strptime(date, '%Y-%m-%d')
    date2 = datetime.strptime(today, '%Y-%m-%d')
    difference = (date1 - date2).days

    difference = abs(difference)

    if difference <= 30:
        initial = document["30 Days"]
        count = float(initial) + float(amount)
        debitors.update_one({"Name": name}, {"$set": {"30 Days": count}})
    elif difference <= 60:
        initial = document["60 Days"]
        count = float(initial) + float(amount)
        debitors.update_one({"Name": name}, {"$set": {"60 Days": count}})
    elif difference <= 90:
        initial = document["90 Days"]
        count = float(initial) + float(amount)
        debitors.update_one({"Name": name}, {"$set": {"90 Days": count}})
    else:
        initial = document["90 Onwards"]
        count = float(initial) + float(amount)
        debitors.update_one({"Name": name}, {"$set": {"90 Onwards": count}})

    if date in doc:
        initial = float(doc['Production'][date])
        count = initial + float(amount)
        debitors.update_one({"Name": name}, {"$set": {"Dates." + date: count}})
    else:
        debitors.update_one({"Name": name}, {"$set": {"Dates." + date: float(amount)}})

    return render_template("Debitors/debitors.html")


# Displaying page for releasing outstanding
@app.route("/releaseOutstanding", methods=['POST'])
def releaseOutstanding():
    debitors = mongo_client.db.debitors
    list_names = []
    names = debitors.find({}, {"Name": 1, "_id": 0})
    for i in names:
        list_names.append(i["Name"])
    return render_template("Debitors/releaseOutstanding.html", debitors=list_names)


# Releasing outstanding amount
@app.route("/rOutstanding", methods=['POST'])
def rOutstanding():
    name = request.form.get("name")
    amount = request.form.get("amount")
    debitors = mongo_client.db.debitors
    document = debitors.find_one({"Name": name})
    release_outstanding(document, name, amount)
    return render_template("Debitors/debitors.html")


# Displaying page for viewing debitors page
@app.route("/viewDebitors", methods=['POST'])
def viewDebitors():
    data = view_debitors_sheet()

    table = data.to_html()

    return render_template("Debitors/viewDebitors.html", table=table)


# Finish Section

@app.route("/finish", methods=['GET'])
def finish():
    return render_template("Finish/finish.html")


@app.route("/addOpening", methods=['POST'])
def addOpening():
    items = mongo_client.db.prodItems
    list_names = []
    for i in items.find({}, {"Name": 1, "_id": 0}):
        list_names.append(i['Name'])

    return render_template("Finish/addOpening.html", items=list_names)


@app.route("/addO", methods=['POST'])
def addO():
    item = request.form.get("item")
    quantity = request.form.get("quantity")
    opening = mongo_client.db.opening
    document = {
        "Name": item,
        "Opening": quantity
    }
    opening.insert_one(document)
    return render_template("Finish/finish.html")


@app.route("/viewFinish", methods=['POST'])
def viewFinish():
    data = view_finish_sheet()

    table = data.to_html()

    return render_template("Finish/viewFinish.html", table=table)


@app.route("/downloadC", methods=['POST', 'GET'])
def downloadC():
    raw_material_data = view_raw_material_sheet()
    production1_data, production2_data = view_production_sheet()
    dispatch_data = view_dispatch_sheet()
    finish_data = view_finish_sheet()
    creditors_data = view_creditors_sheet()
    debitors_data = view_debitors_sheet()
    attendance_data = view_attendance_sheet()
    print(production1_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        raw_material_data.to_excel(writer, sheet_name="Raw Material", index=False)
        production1_data.to_excel(writer, sheet_name="Production 1", index=False)
        production2_data.to_excel(writer, sheet_name="Production 2", index=False)
        dispatch_data.to_excel(writer, sheet_name="Dispatch", index=False)
        finish_data.to_excel(writer, sheet_name="Finish", index=False)
        creditors_data.to_excel(writer, sheet_name="Creditors", index=False)
        debitors_data.to_excel(writer, sheet_name="Debitors", index=False)
        attendance_data.to_excel(writer, sheet_name="Attendance TRAUB", index=False)

    output.seek(0)
    response = send_file(output, as_attachment=True, attachment_filename=file_path,mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Set the response headers to trigger a browser download
    response.headers['Content-Disposition'] = 'attachment; filename=data.xlsx'
    response.headers['Cache-Control'] = 'no-cache'

    return response



@app.route("/downloadP", methods=['POST', 'GET'])
def downloadP():
    today = datetime.datetime.today()
    first = today.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    file_path = prev_month.strftime("%B%Y") + ".xlsx"
    try:
        return send_from_directory(directory='static', filename=file_path, as_attachment=True)
    except Exception as e:
        return str(e)


# Analysis Graphs


@app.route("/analysis", methods=['GET'])
def analysis():
    plot_div1, plot_div2 = production_graph()
    plot_pie1 = production_pie()
    plot_pie2 = creditors_pie()
    plot_pie3 = debitors_pie()
    plot_div3 = dispatch_graph()
    plot_div4 = raw_dispatch_graph()
    plot_div5 = attendance_graph()

    return render_template("Analysis/analysis2.html", plot_div1=plot_div1, plot_div2=plot_div2, plot_div3=plot_pie1, plot_div4=plot_pie2, plot_div5=plot_pie3, plot_div6=plot_div3, plot_div7=plot_div4, plot_div8=plot_div5)
    # return render_template("Analysis/analysis.html")


@app.route("/index")
def index():
    client = MongoClient()
    db = client.ME

    if 'attendance' not in db.list_collection_names():
        db.create_collection('attendance')
    if 'creditors' not in db.list_collection_names():
        db.create_collection('creditors')
    if 'debitors' not in db.list_collection_names():
        db.create_collection('debitors')
    if 'dispatch' not in db.list_collection_names():
        db.create_collection('dispatch')
    if 'employees' not in db.list_collection_names():
        db.create_collection('employees')
    if 'opening' not in db.list_collection_names():
        db.create_collection('opening')
    if 'prodItems' not in db.list_collection_names():
        db.create_collection('prodItems')
    if 'production' not in db.list_collection_names():
        db.create_collection('production')
    if 'raw_material' not in db.list_collection_names():
        db.create_collection('raw_material')
    if 'schedule' not in db.list_collection_names():
        db.create_collection('schedule')

    today = datetime.datetime.now().date()

    if (today.month != 12 and today.day == (datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)).day) or (today.month == 12 and today.day == 31):
        # Today is the last day of the month

        # Download the excel sheet
        pass


    if 'username' in session:
        return redirect(url_for('dashboard'))


    # return render_template('index.html')
    return render_template("index.html")


@app.route("/", methods=['POST', 'GET'])
def login():
    return render_template("login.html")


@app.route("/login", methods=['POST', 'GET'])
def login_next():
    if request.method == 'POST':
        users = mongo_client.db.users
        login_user = users.find_one({"Username": request.form["username"]})
        print("User exists")
        if login_user:
            if request.form["password"] == login_user["Password"]:
                session["username"] = request.form["username"]
                return redirect('/index')
            return "Invalid username/password"

        return "Invalid username/password"
    else:
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = mongo_client.db.users
        existing_user = users.find_one({"Username": request.form["username"]})

        if existing_user is None:
            users.insert_one({
                "Username": request.form["username"],
                "Password": request.form["password"]
            })
            session["username"] = request.form["username"]
            # mongo.db.createCollection(request.form["username"])
            return redirect("/")
        return "The username already exists"

    return render_template("register.html")


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', username=session['username'])


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")



if __name__ == '__main__':
    # Timer(1, lambda: ui("http://127.0.0.1:5000/")).start()
    app.run()
    # ui.run()


# 2023-01-03

# Tasks to do on system reset

# Clear Databases
# 1. Production
# 2. Dispatch

# Creating Login system

# 421
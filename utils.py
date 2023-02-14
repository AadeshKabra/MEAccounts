from flask_pymongo import PyMongo, pymongo

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

import pymongo
client = pymongo.MongoClient(host='localhost', port=27017)

db = client.test

collect = db.students

student =  {
        'id': '20170101',
        'name': 'AAA',
        'age': 20,
        'gender': 'male'
        }
result = collect.insert_one(student)

st2 = {
    'id': '20170102',
    'name': 'BBB',
    'gender': 'female'
}
st3 = {
    'id': '20170103',
    'name': 'CCC',
    'age': 24
}

st4 = {
    'id': '20170204',
    'name': 'Mike',
    'age': 21,
    'gender': 'male'
}

st5 = {
    'id': '20170205',
    'name': 'DD',
    'age': 16,
    'gender': 'male'
}

result2 = collect.insert_many([st2, st3])
result = collect.insert_one(st5)

q = collect.find_one({'name': 'AAA'})
q = collect.find().sort('age', pymongo.ASCENDING)
q = collect.find().sort('age')


print([i['name'] for i in q])

for i in q:
    print(i)
    print(i['name'])

upitem = collect.find_one({'age': 16})
upitem['name'] = 'ff'
q = collect.update_one({'age':16}, {'$set': upitem})






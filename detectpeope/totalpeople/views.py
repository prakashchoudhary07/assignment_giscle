from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


from pymongo import MongoClient


import matplotlib.pyplot as plt


def graph(x, y):
    plt.plot(x, y, color='green', linestyle='dashed', linewidth=3,
             marker='o', markerfacecolor='blue', markersize=12)
    plt.xlabel('Time')
    plt.ylabel('No of people')
    plt.title('Persons Count')
    plt.show()
    return


def count_people(cursor):
    x = list()
    y = list()
    count = 0
    old_count = 0
    new_count = 0
    total_count = 0
    for record in cursor:
        # print(record)
        new_count = record["Output"]["total_person"]
        if(new_count-old_count > 0):
            total_count = total_count + (new_count-old_count)
            old_count = new_count
        elif(new_count-old_count < 0):
            old_count = new_count
        y.append(total_count)
        count = count + 1
        x.append(count)
    print("Total people", total_count)
    graph(x, y)
    return


def totalpeople(request):
    try:
        connection = MongoClient('localhost', 27017)
        print("Connected successfully!!!")

        database = connection.body_detect
        collection = database.people_count
        print(database.collection_names())
        print("Total Documents", collection.count())

        cursor = database.people_count.find()

        count_people(cursor)

    except:
        print("Could not connect to MongoDB, Please try again ")

    finally:
        connection.close()
        print("Connection closed")

    return render(request, 'index.html')

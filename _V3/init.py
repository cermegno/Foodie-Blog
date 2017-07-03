#!/usr/bin/env python3
import redis

r = redis.Redis(host='127.0.0.1', port='6379')
print (r)

print ("CLEANING REDIS")
print ("==============")

print ("Display all keys first")
for k in sorted(r.keys('meal*')):
    print (" - ", str(k,'utf-8'))

input("Press ENTER to continue with key deletion ")

for k in r.keys('meal*'):
    print (" - removing ... " + str(k,'utf-8'))
    r.delete(str(k,'utf-8'))

print ("Now it should be empty")
for k in r.keys('meal*'):
    print (" - "+ str(k,'utf-8'))
print ("")

##############################
print ("The current value of the -counter_meal- counter is " + str(r.get("counter_meal"),'utf-8'))
input("Press ENTER to reset it to zero ")
print (r.set("counter_meal","0"))

print ("The current value of the -caloriecount- counter is " + str(r.get("caloriecount"),'utf-8'))
input("Press ENTER to reset it to zero ")
print (r.set("caloriecount","0"))


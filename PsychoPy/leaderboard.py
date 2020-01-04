import pickle
import heapq
import os
pointData = (-13, "sfdg")
point_list = list()

mode = 'a' if os.path.exists("./leaderboard.pickle") else 'w'
with open("./leaderboard.pickle", mode) as f:
    f = f

with open("./leaderboard.pickle", 'rb') as f:
    try : 
        point_list = pickle.load(f)
    except : 
        point_list = list()
print(point_list)
with open("./leaderboard.pickle", 'wb') as f: 
    point_list.append(pointData)
    heapq.heapify(point_list)
    pickle.dump(point_list, f, pickle.HIGHEST_PROTOCOL)
print(point_list)
print("Highest scores:", point_list[0][1] + " " + str(-point_list[0][0]))
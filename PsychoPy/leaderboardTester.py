import pickle
import heapq
import os

leaderboard_filename = "./leaderboard_short.pickle"

mode = 'a' if os.path.exists(leaderboard_filename) else 'w'
with open(leaderboard_filename, mode) as f:
    f = f

with open(leaderboard_filename, 'rb') as f:
    try : 
        point_list = pickle.load(f)
    except : 
        point_list = list()
print(point_list)

# Write to point list
# pointData = (10, "asdf")
# point_list = list()
# with open(leaderboard_filename, 'wb') as f: 
#     point_list.append(pointData)
#     heapq.heapify(point_list)
#     pickle.dump(point_list, f, pickle.HIGHEST_PROTOCOL)
# print(point_list)
# print("Highest scores:", point_list[0][1] + " " + str(-point_list[0][0]))


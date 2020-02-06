from PsychoPyConstants import *

import pickle
import heapq
import os

MAX_NUM_IN_LEADERBOARD = 20
DEFAULT_NUM_IN_LEADERBOARD = 3

class Leaderboard: 

    def __init__(self, num_in_leaderboard=DEFAULT_NUM_IN_LEADERBOARD):
        if run_type == RUN_TYPE_DEBUG: 
            self.leaderboard_path = "./leaderboard_debug.pickle"
        if run_type == RUN_TYPE_START: 
            self.leaderboard_path = "./leaderboard_start.pickle"
        if run_type == RUN_TYPE_SHORT: 
            self.leaderboard_path = "./leaderboard_short.pickle"
        if run_type == RUN_TYPE_LONG: 
            self.leaderboard_path = "./leaderboard_long.pickle"
        self.__setNumInLeaderboard(num_in_leaderboard)
        
    def __setNumInLeaderboard(self, num_in_leaderboard=DEFAULT_NUM_IN_LEADERBOARD) :
        # Sets the number of places in the leaderboard
        if (num_in_leaderboard >= 0) and (num_in_leaderboard <= MAX_NUM_IN_LEADERBOARD):
            self.num_in_leaderboard = num_in_leaderboard
        else :
            print("Invalid num_in_leaderboard (must be value [0,20]). Setting default value = " + str(DEFAULT_NUM_IN_LEADERBOARD))
            num_in_leaderboard = DEFAULT_NUM_IN_LEADERBOARD
    
    def __getPointList(self): 
        # Gets the point list 

        point_list = list()
        mode = 'a' if os.path.exists(self.leaderboard_path) else 'w'
        # Create file if does not exist
        with open(self.leaderboard_path, mode) as f:
            f = f # Do nothing

        with open(self.leaderboard_path, 'rb+') as f:
            try : 
                point_list = pickle.load(f)
            except : 
                point_list = list()
        return point_list

    def update(self, new_point_value, new_point_name): 
        # newPointValue is a tuple that contains (points, name)
        # Adds the new point value to the leaderboard points pickle
        # Points are stored as negative values to be able to utilize heapify to get max values
        # Number of stored points are pruned to the MAX_NUM_IN_LEADERBOARD

        new_point_data = (-new_point_value, new_point_name)
        
        point_list = self.__getPointList()
        point_list.append(new_point_data)
        heapq.heapify(point_list)

        highest_scores_list = list()
        for i in range(len(point_list) if len(point_list) < MAX_NUM_IN_LEADERBOARD else MAX_NUM_IN_LEADERBOARD):
            high_score = heapq.heappop(point_list)
            highest_scores_list.append(high_score)

        with open(self.leaderboard_path, 'wb') as f: 
            pickle.dump(highest_scores_list, f, pickle.HIGHEST_PROTOCOL)


    def getHighscoresText(self) :
        # Returns a formatted string containing the top # scores

        highest_scores_text = "Highest scores:"
        highest_scores_list = list()
        point_list = self.__getPointList()
        for i in range(len(point_list) if len(point_list) < self.num_in_leaderboard else self.num_in_leaderboard):
            high_score = heapq.heappop(point_list)
            highest_scores_list.append(high_score)
            score_report = high_score[1] + "\t---\t" + str(-high_score[0])
            highest_scores_text = highest_scores_text + "\n" + str(i+1) + ". " + score_report

        return highest_scores_text

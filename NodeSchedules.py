from datetime import time as t
from datetime import date as d
"""
Stores start and end times in lists. Each node has a key stored in the DB that
tells the NodeScheduler which schedule to use. 0 will disable the scheduler.
"""

ScheduleDict = {0 : [None, None],
                1 : [t(18, 30, 00), t(06, 30, 00)]}

HolidayList = [d(2015, 11, 26),     #Thanksgiving
                d(2015, 12, 25),    #Christmas
                d(2015, 12, 15),    #Test
                d(2015, 12, 31),    #New Years
                ]    

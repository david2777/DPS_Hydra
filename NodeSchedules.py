from datetime import time as t
"""
Stores start and end times in lists. Each node has a key stored in the DB that
tells the NodeScheduler which schedule to use. 0 will disable the scheduler.
"""

ScheduleDict = {0 : [None, None],
                1 : [t(18, 30, 00), t(20, 00, 00)]
}

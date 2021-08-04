import time
import gps

class cansat(object):
    def __init__(self):
        self.gps = gps.GPS()

    def setup(self):
        self.gps.setupGPS()
        
    def writeData(self):
        self.gps.gpsread()
        timer = 1000*(time.time() - start_time)
        timer = int(timer)
        datalog = str(timer) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon)
    
        with open("test.txt",mode = 'a') as test:
            test.write(datalog + '\n')


start_time = time.time()
cansat = cansat() 
cansat.setup()
while True:
    cansat.writeData()   
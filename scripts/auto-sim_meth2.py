#!/usr/bin/python

import math
import pickle
import csv
import time

PIK = "axis-database.pkl"

# Output per second (Hz) [Default = 60]
OutputRate = 60
AxisStorage = []
FRAME = 0
"""Class definitions"""

class Axis:
    def __init__(self, AxisNumber, AxisName=None, Accel=None, Decel=None, HighSoft=16000, LowSoft=1000, Speed = 400, Position = 0):
        self.AxisNumber = AxisNumber
        self.HighSoft = HighSoft
        self.LowSoft = LowSoft
        self.Position = Position
        self.Target = None
        self.Deads = {}
        self.Decel = None
        self.AxisType = None
        self.Time = 0
        self.Complete = False
        self.MovedBy = 0
        if AxisName == None:
            self.Text = "Axis {0}".format(AxisNumber)
        else:
            self.Text = AxisName

    def print_me(self):
        print(self.__dict__)

    def PrintMove(self):
        print(f"Flybar: {self.AxisNumber}\tPosition: {self.Position},\tIncrement Per 1/{OutputRate} second: {self.Increment}")

    def set_target(self, Target):
        self.Target = Target
        self.Complete = False

    def calc_move_distance(self):
        if self.Target > self.Position:
            self.Distance = self.Target - self.Position
        elif self.Target < self.Position:
            self.Distance = self.Position - self.Target
        return self.Distance

    def calc_increment(self, Target, Time):
        return self.calc_move_distance()



    def go(self):
        self.StartPosit = self.Position
        print(self.StartPosit, self.Position)
        self.AccelEndLimit = round(self.Position + self.Distance*0.25)
        self.DecelStartLimit = round(self.Target - self.Distance*0.25)
        print(self.AccelEndLimit, self.DecelStartLimit)
        increment = self.calc_increment(self.Target, self.Time/OutputRate)
        self.Complete = False
        while self.Complete == False:
            print(self.StartPosit, self.Position, self.AccelEndLimit, self.DecelStartLimit,self.Target)
            if self.Position < self.AccelEndLimit:
                # If position is in the accel phase
                print(increment)
                self.move(self.calc_displacement())
                print(self.Position)
            elif self.Position > self.Position+self.AccelEndLimit and self.Position < self.Target-self.DecelDistance:
                # If position is between phases (linear velocity)
                self.move(increment)
                self.PrintMove()
            elif self.Position > self.DecelStartLimit:
                # If position is in the decel phase
                self.move(increment/2)
                self.PrintMove
            else:
                ExitCondition = True

    def move(self, increment, OutputRate = None):
        self.Position += increment
        return self.Position


    def calc_displacement(self):
        u = self.Speed
        t = self.Time
        a = 1
        s = u * t + (a+t**2) * 0.5
        # s = distance travelled in the 1/60th of a second.
        return s/1000


    def add_dead(self, dead_no, position):
        # Format for dead_list must be [1: 14100, 2: 7000, ... ]
        self.Deads[dead_no] = position

    def print_deads(self):
        if len(self.Deads.items()) == 0:
            print("No deads have been set for {0}".format(AxisName))
        for key, value in sorted(self.Deads.items()):
            print(key, value)



    def calc_speed(self):
        if self.Speed != None:
            self.Speed = self.Target / self.Time
        elif self.Time != None:
            self.calc_move_distance()
            self.Time = self.Position

    def calc_accel(self):
        pass

    def calc_decel(self):
        pass

    def send_OSC(self):
        #For this axis, send a thing.
        pass

    def snooze(self, SleepValue):
        time.sleep(SleepValue)



class Flybar(Axis):
    def __init__(self, AxisNumber, AxisName = None):
        self.MaxSpeed = 5000
        super().__init__(AxisNumber, AxisName)


class ChainHoist(Axis):
    def __init__(self, AxisNumber, AxisName = None):
        self.MaxSpeed = 400
        super().__init__(AxisNumber, AxisName)


"""Function Definitions"""
def load_db(db_file="axis-database_default.pkl"):
    print("Reading {0}".format(db_file))
    with open(db_file, "rb") as f:
        axis_db = pickle.load(f)
    return axis_db


def write_db(data, db_file="axis-database_default.pkl"):
    print("Writing {0}".format(db_file))
    with open(db_file, "wb") as f:
        pickle.dump(data, f)


def setup_Axes():
    AxisReturn = []
    NumberAxes = int(input("How many axes do you want to add to the system?"))
    for iteration in range(NumberAxes):
        AxisNumber = iteration + 1
        Type = str(input("Chainhoist or Flybar? [ C | F ]"))
        if Type == "C":
            AxisReturn.append(ChainHoist(AxisNumber))
        elif Type == "F":
            AxisReturn.append(Flybar(AxisNumber))
    return AxisReturn


def read_cues():
    """Open the cues file, containing:
    Cue Number, Cue Text, Cue Duration, Cue Travel, Cue Speed, Initial Position, Target Position"""
    pass


def trigger_cue(OSC_input, cuelist):
    if OSC_input == cuelist:
        pass


def writeCue():
    """Add a cue into the system"""
    pass


def setup_deads(AxisStorage):
    ExitCondition = False
    while ExitCondition == False:
        usr_Input = str(input("Enter Axis Number, or 'Q' to Quit"))
        for axis in AxisStorage:
            if axis.AxisNumber == int(usr_Input):
                axis.print_deads()
                dead_no = int(input("Please enter your dead number: "))
                dead_position = int(input("Enter position: "))
                axis.Deads[dead_no] = dead_position
        if usr_Input == "Q":
            ExitCondition = True


def printAxes(AxisStorage):
    for Ax in AxisStorage:
        Ax.print_me()


def menu():
    print("""
    1 - Add axes.
    2 - Add cues.
    3 - Add deads.
    4 - List axes info.
    99 - Playback cues.
    0 - Quit.
""")
    menu_response = int(input("Which option from the menu?"))
    return menu_response


def main(menu_response, AxisStorage = None):
    if menu_response == 1:
        AxisStorage = setup_Axes()
    if menu_response == 2:
        CueStorage = setup_Cues()
    elif menu_response == 4:
        printAxes(AxisStorage)
    elif menu_response == 99:
        #Load Axis Target and Position info.
        axis = [1]
        """
        Need to look into threading to update multiple Axes simultaneously.

        something like:
        load Axis moves to parameters,
        for Axis in Cue Axes:
            Thread.start(Axis.go())
        that should start all moves, but it doesn't allow for any delay at the start of move.

        """
        for Ax in AxisStorage:
            if Ax.AxisNumber == 1:
                # Set up pre axis moves things
                Ax.Position = 0
                Ax.Target = 1000
                Ax.Time = 10 * OutputRate
                """
                Change Ax.Increment based on % move complete, then put the increment as a square till 1
                or some other mathmatical function to create a curve - sqrt increment squared + 1 or something.
                """
                Ax.Increment = Ax.calc_move_distance() / Ax.Time
                Ax.Speed = Ax.Distance / Ax.Time
                # Work out how long to sleep per frame.
                SleepValue = 1/OutputRate - (1/OutputRate)/100 * 10.1
                Ax.snooze(SleepValue)
                Ax.go()
                Ax.Position = Ax.move(Ax.Increment, OutputRate)
                Ax.PrintMove()
                print(ExitCondition)
                Ax.send_OSC()
    elif menu_response == 0:
        return True
    else:
        print("Not there yet!")


def importAxes():
    AxisStorage = []
    with open('axis_table.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print("Found columns: {0}".format(", ".join(row)))
                line_count += 1
            else:

                if row[2] == "C":
                    AxisStorage.append(ChainHoist(row[0], row[1]))
                elif row[2] == "F":
                    AxisStorage.append(Flybar(row[0],row[1]))
                    line_count += 1
        print('Processed {0} lines.'.format(line_count))


if __name__ == "__main__":
    DB_FILE = "axis-db.pkl"
    ExitCondition = False
    while ExitCondition == False:
        try:
            # Try loading the axes file from the default place first.
            AxisStorage = load_db(DB_FILE)
        except BaseException as e:
            print(e)
            # Otherwise, add them.
            print("No Axis DB found! (' {0} ')".format(DB_FILE))
            AxisStorage = setup_Axes()
            write_db(AxisStorage, DB_FILE)
        try:
            menu_response = menu()
            ExitCondition = main(menu_response, AxisStorage)
            if ExitCondition:
                print("We're gettin outta here cap'n!")
                write_db(AxisStorage)
        except:
            raise
            write_db(AxisStorage)

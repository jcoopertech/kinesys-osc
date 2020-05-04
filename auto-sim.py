#!/usr/bin python

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
        print(self.__dict__)
        self.Target = None
        self.Deads = {}
        self.Decel = None
        self.AxisType = None
        self.Time : float = 0
        if AxisName == None:
            self.Text = "Axis {0}".format(AxisNumber)
        else:
            self.Text = AxisName

    def print_me(self):
        for attribute,value in self.__dict__.items():
            print(attribute, value)

    def set_target(self, Target):
        self.Target = Target

    def calc_increment(self, Target, Time):
        pass

    def move(self, increment):
        if self.Target != None:
            self.Position += increment

    def add_dead(self, dead_no, position):
        # Format for dead_list must be [1: 14100, 2: 7000, ... ]
        self.Deads[dead_no] = position

    def print_deads(self):
        if len(self.Deads.items()) == 0:
            print("No deads have been set for {0}".format(AxisName))
        for key, value in sorted(self.Deads.items()):
            print(key, value)

    def calc_move_distance(self):
        if self.Target > self.Position:
            self.Distance = self.Target - self.Position
        elif self.Target < self.Position:
            self.Distance = self.Position - self.Target
        return self.Distance

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
    elif menu_response == 4:
        printAxes(AxisStorage)
    elif menu_response == 99:
        #Load Axis Target and Position info.
        axis = [1]
        for Ax in AxisStorage:
            if Ax.AxisNumber == 1:
                Ax.Position = 0
                Ax.Target = 100000
                Ax.calc_move_distance()
                Ax.Time = 100 * OutputRate

                Ax.Speed = Ax.Distance / Ax.Time
                SleepValue = 1/OutputRate - (1/OutputRate)/100 * 10.1
                time_now = time.time()
                while Ax.Position < Ax.Target:
                    time.sleep(SleepValue)
                    Ax.move(Ax.Speed)
                    print(Ax.Position, Ax.Speed)
                time_end = time.time()
                print(time_end-time_now)
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
                print(f'Found columns: {", ".join(row)}')
                line_count += 1
            else:

                print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
        print(f'Processed {line_count} lines.')


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

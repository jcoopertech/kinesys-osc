#!/usr/bin/python

"""
Using a Frame calculated pre determined move thing.

"""

import math
import pickle
import csv
import time
from error_handling import *
from classes import *

DB_FILE = "axis-db.pkl"
CueStorageFile = "cue_storage.pkl"

# Output per second (Hz) [Default = 60]
OutputRate = 60
AxisStorage = []
CueStorage = []

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

def Quser_input(query):
    if input(query) not in ["Q", "q", "quit"]:
        return str(query)
    else:
        return True

def setup_MoveEventInCue(CueNumber, AxisStorage):
    printAxes(AxisStorage)
    AxisID = Quser_input("Enter which Axis you'd like to move: ")
    AxisStorage[0].print_me()
    Target = Quser_input(f"Enter the target for '{[Axis.AxisName for Axis in AxisStorage if Axis.AxisNumber == AxisID]}': '")
    Time = Quser_input(f"How many seconds should this move take?")
    Move = MoveEvent(Target, Time, AxisID)
    return Move




def setup_Cues(CueStorage, AxisStorage):
    """Runtime here"""
    ExitCondition = False
    while ExitCondition == False:
        CueMoves = {}
        CueNumber = Quser_input("Enter Cue number we're listening for: ")
        CueMoves = setup_MoveEventInCue(CueNumber, AxisStorage)
        CurrentCue = Cue(CueNumber, CueMoves)
        CueStorage.append(CurrentCue)



def read_cues():
    """Open the cues file, containing:
    Cue Number, Cue Text, Cue Duration, Cue Travel, Cue Speed, Initial Position, Target Position"""
    pass


def trigger_cue(OSC_input, cuelist):
    if OSC_input == cuelist:
        pass


"""# Cue . moves =
[MoveEventList[Axis] = Target]
"""


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
        print(Ax.Text, Ax.Position)


def importAxes(axisTable="axis_table.csv"):
    AxisStorage = []
    with open(axisTable, "r") as csv_file:
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
    return AxisStorage


def menu():
    print("""
    1 - Add axes.
    2 - Add cues.
    3 - Add deads.
    4 - List axes info.
    5 - Load axes from CSV file.
    99 - Playback cues.
    0 - Quit.
""")
    menu_response = int(input("Which option from the menu?"))
    return menu_response


def main(menu_response, AxisStorage = None, CueStorage = None):
    if menu_response == 1:
        AxisStorage = setup_Axes()
    if menu_response == 2:
        CueStorage = setup_Cues(CueStorage, AxisStorage)
    elif menu_response == 4:
        printAxes(AxisStorage)
    elif menu_response == 5:
        AxisStorage = importAxes()
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
        CurrentCue = 1 # Get this from OSC input
        for Ax in AxisStorage:
            if CurrentCue == [Cue.CueNumber for Cue in CueStorage if Cue.CueNumber == CurrentCue][0]:
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
                Ax.go()
                Ax.Position = Ax.move(Ax.Increment, OutputRate)
                Ax.PrintMove()
                if Ax.Position >= Ax.Target:
                    Ax.Complete = True
                print(ExitCondition)
    elif menu_response == 0:
        return True
    else:
        print("Not there yet!")


if __name__ == "__main__":
    ExitCondition = False
    while ExitCondition == False:
        try:
            """Try loading the axes file from the default place first."""
            AxisStorage = load_db(DB_FILE)
            CueStorage = load_db(CueStorageFile)
        except FileNotFoundError as e:
            print(e)
            write_db(AxisStorage, DB_FILE)
            write_db(CueStorage, CueStorageFile)

        except Exception as e:
            print(e)
            # Otherwise, add them.
            AxisStorage = setup_Axes()
            write_db(AxisStorage, DB_FILE)
            write_db(CueStorage, CueStorageFile)
        try:
            """Start running from here"""
            menu_response = menu()
            ExitCondition = main(menu_response, AxisStorage, CueStorage)
            if ExitCondition:
                print("We're gettin outta here cap'n!")
                write_db(AxisStorage)
                write_db(CueStorage, CueStorageFile)
        except:
            raise
            write_db(AxisStorage)
            write_db(CueStorage, CueStorageFile)

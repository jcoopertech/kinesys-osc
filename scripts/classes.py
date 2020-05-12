"""Class definitions"""

# How we define a move, and incremental OSC pulse values

class Cue():
    def __init__(self,CueNumber, MoveList):
        # Creating a new cue
        self.Moves = MoveList
        self.Axes = [keys for keys in self.Moves.items()]
        print(self.Axes)
        self.CueNumber = CueNumber
        for move in MoveList:
            self.Moves.append(move)

    def go(self):
        for move in self.Moves:
            print(move)
            #Start move threads here.

    def edit_Cue(self):
        pass


class MoveEvent(Cue):
    def __init__(self, Target, Time, Axis, Position=None):
        self.Target = Target
        self.Time = Time
        self.Position = Position
        self.Distance = self.calc_move_distance()
        self.MoveSteps = []
        self.NumberMovePulses = round(int(self.Distance/self.Time * OutputRate))
        self.Axis = Axis
        try:
            if SafeToMove():
                calculateMoveSteps()
        except MoveError as e:
            print(e)
        except:
            raise

    def SafeToMove(self):
        # Is the target within the limits, and in the time frame?
        if self.Target > self.Axis.HighSoft:
            raise HighSoftStruck(self.Target)
            return False
        if self.Target < self.Axis.LowSoft:
            raise LowSoftStruck(self.Target)
            return False
        if self.Speed < self.Axis.MaxSpeed:
            raise Overspeed(self.Speed)
            return False
        if self.Speed > self.Axis.MinSpeed:
            raise Underspeed(self.Speed)
            return False
        return True

    def calc_move_distance(self):
        if self.SafeToMove():
            if self.Axis.Target > self.Axis.Position:
                self.Axis.Distance = self.Axis.Target - self.Axis.Position
            elif self.Axis.Target < self.Axis.Position:
                self.Distance = self.Axis.Position - self.Axis.Target
        print(f"Distance is {self.Distance}, between {self.Axis.Position} and {self.Axis.Target}")
        return self.Distance

    def calc_pulse_move(self):
        # Get part of total move we need to complete in this pulse.
        self.pulse_move = self.Distance * OutputRate

    def calculateMoveSteps(self):
        self.Distance = self.calc_move_distance()
        self.MoveStepsList = []
        # Work out linear move for each pulse, based on overall D=S*T calc
        pulsemove = calc_pulse_move()
        for step in range(self.NumberMovePulses):
            # Add pulses for each move thing to list
            self.MoveStepsList.append(pulsemove)


class Axis:
    def __init__(self, AxisNumber, AxisName=None, Accel=None, Decel=None, HighSoft=16000, LowSoft=1000, Speed = 400, Position = 0):
        self.AxisNumber = AxisNumber
        self.HighSoft = HighSoft
        self.LowSoft = LowSoft
        self.Position = Position
        self.Target = None
        self.Deads = {}
        self.Decel = None
        self.Time = 0
        self.Complete = False
        if AxisName == None:
            self.Text = "Axis {0}".format(AxisNumber)
        else:
            self.Text = AxisName
        self.CurrentMove = None


    def print_me(self):
        print(self.__dict__)

    def PrintMove(self):
        print(f"Flybar: {self.AxisNumber}\tPosition: {self.Position},\tIncrement Per 1/{OutputRate} second: {self.Increment}")

    def set_target(self, Target):
        self.Target = Target

    def calc_increment(self, Target, Time):
        return self.calc_move_distance()

    def doMove(self):
        self.CurrentCue = None # Cue object
        self.CurrentMove = MoveEvent(self.Target, self.Time, self.Position)

    def go(self):
        self.StartPosit = self.Position
        print(self.StartPosit, self.Position)
        print(self.Target)
        self.AccelEndLimit = round(self.Position + self.Distance*0.25)
        self.DecelStartLimit = round(self.Target - self.Distance*0.25)
        print(self.AccelEndLimit, self.DecelStartLimit)
        increment = self.calc_increment(self.Target, self.Time/OutputRate)


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


class Flybar(Axis):
    def __init__(self, AxisNumber, AxisName = None):
        self.MaxSpeed = 5000
        super().__init__(AxisNumber, AxisName)


class ChainHoist(Axis):
    def __init__(self, AxisNumber, AxisName = None):
        self.MaxSpeed = 400
        super().__init__(AxisNumber, AxisName)

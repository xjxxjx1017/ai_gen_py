from SurvivalGames import AutoConfig
from SurvivalGames import Environment
from ThirdParty import SystemPlus
from Testers import OneWayBuffer
import traceback

class TextConsole:

    inst = None

    def __init__(self, outputBuffer:"OneWayBuffer"):
        self.lastTest = []
        self.lastCommand = []
        self.outputBuffer = outputBuffer
        TextConsole.inst = self

    # < These are the interfaces that connected to the simulations
    def doExternal_generateAutoConfig(self, seed):
        return AutoConfig.generate(seed)

    def doExternal_runEnvironment(self, seed):
        u = Environment.Environment()
        u.run(seed)
        return u

    def doExternal_filterEnvironment(self, u, limitListMin, limitListMax):
        a1 = u.rlt_endYear >= limitListMin[0] and u.rlt_endYear <= limitListMax[0]
        a2 = u.rlt_creatureCount >= limitListMin[1] and u.rlt_creatureCount <= limitListMax[1]
        return a1 and a2

    def doExternal_getResult(self, u, id):
        return "ID: " + str(id) + "\tSeed: " + str(u.seed) + "\tEnd year: " + \
               str(u.rlt_endYear) + "\tCreature count: " + str(u.rlt_creatureCount)
    # </

    # $ Run the tester
    def run(self, command, showHelp):
        # * Show some 'help' at the start of the program
        if showHelp == True:
            self.printHelp()
        if command is not "quit":
            # * Do some command
            # [] Stop any false command from breaking the program
            try:
                # * Do some command
                self.doCommand(command)
            except Exception:
                self.consolePrintL(traceback.format_exc())
                self.consolePrintL( "You can still continue with the terminal:")
                self.consolePrintL( "///////////////////////////////////////////////")

    # $ Run a command
    def doCommand( self, command ):
        # # parse command as a lower case string
        command = command.lower()
        # * Split the command into little commands
        commands = SystemPlus.splitCommand( command )
        # * Save the command as the last command
        if len(commands) > 0 and commands[0] != 'r' and ( len(commands) == 0 or command != self.lastCommand ):
            self.lastCommand += command
        # * Parse commands and run it!
        self.parseCommand( commands )

    # $ Parse a command
    def parseCommand(self, commands):
        parameters = []
        if commands[0] == "help":
            # * Show some 'help'
            self.printHelp()
        elif commands[0] == "start":
            # * Run a standard test
            self.runTest()
        elif commands[0] == "filter":
            # * Run a filter test, only record the test we wanted
            parameters += [ int(commands[1]) ]
            parameters += [ int(commands[2]) ]
            parameters += [ int(commands[3]) ]
            parameters += [ int(commands[4]) ]
            self.runFilterTest(10, parameters[0], parameters[1], parameters[2], parameters[3])
        elif commands[0] == "single":
            # * Run a serials test for a single configuration generated by a certain seed
            parameters += [ int(commands[1]) ]
            parameters += [ int(commands[2]) ]
            self.runSingleTest(parameters[0], parameters[1])
        elif commands[0] == "r":
            # * Redo the last 'n' command
            if commands.Count > 1:
                parameters += [ int(commands[1]) ]
                commandL = self.lastCommand[len(self.lastCommand) - parameters[0]]
                self.doCommand(commandL)
            else:
                self.doCommand(self.lastCommand[len(self.lastCommand) - 1])
        else:
            # * If the input is an integer, print the config id
            id = int(commands[0])
            if id > 0:
                index = id - 1
                seed = self.lastTest[index].seed
                configDisc = self.doExternal_generateAutoConfig(seed).toString()
                self.consolePrintL(configDisc)
                self.consolePrintL(self.lastTest[index].toStringLimit(20))

    # $ Run a series of tests for a single seed
    def runSingleTest(self, seed, times):
        # * Config params for testing
        uList = []
        universeMax = times
        # * Run test for a fixed seed
        while len(uList) < universeMax:
            u = self.doExternal_runEnvironment( seed )
            uList += [ u ]
        # [] Print results
        self.printResult(uList)
        self.lastTest = uList

    # $ Run a series of tests, filter the result
    def runFilterTest(self, count, minYear, maxYear, minCreature, maxCreature):
        # * Config params for testing
        uList = []
        universeMax = 10
        # * Run test
        seed = 1
        while len(uList) < universeMax:
            u = self.doExternal_runEnvironment( seed )
            if self.doExternal_filterEnvironment(u, [minYear, minCreature], [maxYear, maxCreature]):
                uList += [ u ]
            seed += 1
        # [] Print results
        self.printResult(uList)
        self.lastTest = uList

    # $ Run a standard test
    def runTest(self):
        uList = []
        universeMax = 30
        # * Run test
        seed = 1
        while len(uList) < universeMax:
            u = self.doExternal_runEnvironment( seed )
            uList += [ u ]
            seed += 1
        # [] Print results
        self.printResult(uList)
        self.lastTest = uList

    # $ Print result for all tests
    def printResult(self, uList):
        self.consoleClear()
        for i in range(0, len(uList)):
            u = uList[i]
            self.consolePrintL( self.doExternal_getResult( u, i+1 ))

    ################## APIs #################

    # $ Print line
    def consolePrintL(self, content):
        self.outputBuffer.add( content + "\n" )
        SystemPlus.consolePrintL( content )

    # $ Clear all
    def consoleClear(self):
        self.outputBuffer.clear()
        SystemPlus.consoleClear()

    # $ Print help
    def printHelp(self):
        self.consolePrintL("""
////////////// HELP //////////////////
help                For help
quit                Quit the console
start               Run a standard test
filter x x x x      Run a filter test, only record the test we wanted
                        p1: min years
                        p2: max years
                        p3: min creatures
                        p4: max creatures
single x x          Run series of tests for a single configuration generated
                    by a certain seed
                        p1: a fixed seed for the simulation
                        p2: number of times for the simulation
r (x)               Redo the last 'n' command
                        p1 (=1): the previous 'n' test that you want to execute
[integer]           If the input is an integer, print the detail of a test has
                    the same ID as the integer
//////////////////////////////////////
""")
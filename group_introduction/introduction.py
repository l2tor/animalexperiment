""" Introduction less """


# DONT FORGET TO UPDATE THE ROBOT IP ADDRESS IN THE MAIN!!!!!
import sys
import time
import csv

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

class IntroLesModule(ALModule):
    """ A simple module able to react
    to facedetection events

    """
    def __init__(self, name):
        ALModule.__init__(self, name)

        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")
        self.postureProxy = ALProxy("ALRobotPosture")
        self.motionProxy = ALProxy("ALMotion")
        self.managerProxy = ALProxy("ALBehaviorManager")
        self.leds = ALProxy("ALLeds")

        self.leds.fade('FaceLeds',1.0,1.0)


        # set volume
        self.tts.setLanguage("Dutch")
        self.tts.setVolume(1)
        self.tts.setParameter("speed",85)
        self.LedsOn(self.leds)
        print 'First lesson started'
        self.readCSV()
        # Subscribe to the FaceDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("FaceDetected",
            "HumanGreeter",
            "onFaceDetected")

    def readCSV(self):
        path = 'introduction.csv'
        with open (path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                action = row[2]
                print ', '.join(row)
                if 'Text' in row:
                    self.tts.setLanguage(row[1])
                    if row[1] == 'English':                 
                        self.tts.setParameter("pitchShift", 0.0)
    ##    #Deactivates double voice
                    #    tts.setVolume(0.6)
                        self.tts.setParameter("doubleVoice", 1.0)                            
                    self.tts.setParameter("defaultVoiceSpeed", 80)
                    self.tts.setParameter("pitchShift", 1.2)
                    s = "  " + action + " "
                    self.tts.say(s)                
                elif 'Posture' in row:
                    self.lookForward(self.motionProxy)
                    self.postureProxy.goToPosture(action, 0.8)
                    self.motionProxy.setStiffnesses("Body", 0.0) 
                elif 'Move' in row:
                    if 'Handje' in action:
                        self.lookAtHand(self.motionProxy)
                    elif action == 'lookForward':
                        self.lookForward(self.motionProxy)
                    elif action == 'waving' :
                        self.waving(self.motionProxy)
                    elif 'LEDS' in action:
                        self.leds.rasta(8.0)
                elif 'Dansje' in row:
                    self.launchAndStopBehavior(self.managerProxy,action)
                elif 'End' in row:
                    self.LedsOff(self.leds)
                else:
                    raw_input("Press Enter to continue...")

                    
    def launchAndStopBehavior(self, managerProxy, behaviorName):
      ''' Launch and stop a behavior, if possible. '''

      # Check that the behavior exists.
      if (managerProxy.isBehaviorInstalled(behaviorName)):

        # Check that it is not already running.
        if (not managerProxy.isBehaviorRunning(behaviorName)):
          # Launch behavior. This is a blocking call, use post if you do not
          # want to wait for the behavior to finish.
          managerProxy.post.runBehavior(behaviorName)
          time.sleep(0.5)
        else:
          print "Behavior is already running."

      else:
        print "Behavior not found."
        return

      names = managerProxy.getRunningBehaviors()
      print "Running behaviors:"
      print names

      # Stop the behavior.
      if (managerProxy.isBehaviorRunning(behaviorName)):
        managerProxy.stopBehavior(behaviorName)
        time.sleep(1.0)
      else:
        print "Behavior is already stopped."

      names = managerProxy.getRunningBehaviors()
      print "Running behaviors:"
      print names

      """Behaviors"""


        
    def lookAtHand(self, motionProxy):
        motionProxy.setStiffnesses("Head", 1.0)
        motionProxy.setStiffnesses("RHand",1.0)
        names = "Head"
        angleLists = [-0.3,0.7]
        
        times = 1.0
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, times, isAbsolute)
        motionProxy.openHand('RHand')
        
        time.sleep(3.0)
        motionProxy.setStiffnesses("Head", 0.0)

    def lookForward(self, motionProxy):
        motionProxy.setStiffnesses("Head", 1.0)
        names = "Head"
        angleLists = [0.0,0.0]
        times = 1.0
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, times, isAbsolute)
        time.sleep(3.0)
        motionProxy.setStiffnesses("Head", 0.0)
        motionProxy.closeHand('RHand')
        motionProxy.setStiffnesses("RHand", 0.0)



    def waving(self, motionProxy):
        motionProxy.setStiffnesses("Body", 1.0)
        names = list()
        times = list()
        keys = list()

        names.append("LElbowRoll")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[-1.04615, [3, -0.533333, 0], [3, 0.4, 0]], [-0.928028, [3, -0.4, 0], [3, 0.133333, 0]], [-0.928028, [3, -0.133333, 0], [3, 0.16, 0]], [-0.928028, [3, -0.16, 0], [3, 0.16, 0]], [-0.928028, [3, -0.16, 0], [3, 0.16, 0]], [-0.928028, [3, -0.16, 0], [3, 0.16, 0]], [-0.928028, [3, -0.16, 0], [3, 0.16, 0]], [-0.928028, [3, -0.16, 0], [3, 0.44, 0]], [-1.04615, [3, -0.44, 0], [3, 0, 0]]])

        names.append("LElbowYaw")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[-0.780848, [3, -0.533333, 0], [3, 0.4, 0]], [-0.83147, [3, -0.4, 0], [3, 0.133333, 0]], [-0.83147, [3, -0.133333, 0], [3, 0.16, 0]], [-0.83147, [3, -0.16, 0], [3, 0.16, 0]], [-0.83147, [3, -0.16, 0], [3, 0.16, 0]], [-0.83147, [3, -0.16, 0], [3, 0.16, 0]], [-0.83147, [3, -0.16, 0], [3, 0.16, 0]], [-0.83147, [3, -0.16, 0], [3, 0.44, 0]], [-0.780848, [3, -0.44, 0], [3, 0, 0]]])

        names.append("LHand")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[0.0144, [3, -0.533333, 0], [3, 0.4, 0]], [0.0144, [3, -0.4, 0], [3, 0.133333, 0]], [0.0144, [3, -0.133333, 0], [3, 0.16, 0]], [0.0144, [3, -0.16, 0], [3, 0.16, 0]], [0.0144, [3, -0.16, 0], [3, 0.16, 0]], [0.0144, [3, -0.16, 0], [3, 0.16, 0]], [0.0144, [3, -0.16, 0], [3, 0.16, 0]], [0.0144, [3, -0.16, 0], [3, 0.44, 0]], [0.0144, [3, -0.44, 0], [3, 0, 0]]])

        names.append("LShoulderPitch")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[1.43271, [3, -0.533333, 0], [3, 0.4, 0]], [1.42044, [3, -0.4, 0], [3, 0.133333, 0]], [1.42044, [3, -0.133333, 0], [3, 0.16, 0]], [1.42044, [3, -0.16, 0], [3, 0.16, 0]], [1.42044, [3, -0.16, 0], [3, 0.16, 0]], [1.42044, [3, -0.16, 0], [3, 0.16, 0]], [1.42044, [3, -0.16, 0], [3, 0.16, 0]], [1.42044, [3, -0.16, 0], [3, 0.44, 0]], [1.43271, [3, -0.44, 0], [3, 0, 0]]])

        names.append("LShoulderRoll")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[0.156426, [3, -0.533333, 0], [3, 0.4, 0]], [0.0966001, [3, -0.4, 0], [3, 0.133333, 0]], [0.0966001, [3, -0.133333, 0], [3, 0.16, 0]], [0.0966001, [3, -0.16, 0], [3, 0.16, 0]], [0.0966001, [3, -0.16, 0], [3, 0.16, 0]], [0.0966001, [3, -0.16, 0], [3, 0.16, 0]], [0.0966001, [3, -0.16, 0], [3, 0.16, 0]], [0.0966001, [3, -0.16, 0], [3, 0.44, 0]], [0.156426, [3, -0.44, 0], [3, 0, 0]]])

        names.append("LWristYaw")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[0.16563, [3, -0.533333, 0], [3, 0.4, 0]], [-0.300706, [3, -0.4, 0], [3, 0.133333, 0]], [-0.300706, [3, -0.133333, 0], [3, 0.16, 0]], [-0.300706, [3, -0.16, 0], [3, 0.16, 0]], [-0.300706, [3, -0.16, 0], [3, 0.16, 0]], [-0.300706, [3, -0.16, 0], [3, 0.16, 0]], [-0.300706, [3, -0.16, 0], [3, 0.16, 0]], [-0.300706, [3, -0.16, 0], [3, 0.44, 0]], [0.16563, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RElbowRoll")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[1.04776, [3, -0.533333, 0], [3, 0.4, 0]], [0.897433, [3, -0.4, 0], [3, 0.133333, 0]], [1.00021, [3, -0.133333, 0], [3, 0.16, 0]], [0.570689, [3, -0.16, 0], [3, 0.16, 0]], [1.00021, [3, -0.16, 0], [3, 0.16, 0]], [0.570689, [3, -0.16, 0], [3, 0.16, 0]], [1.00021, [3, -0.16, 0], [3, 0.16, 0]], [0.570689, [3, -0.16, 0], [3, 0.44, 0]], [1.04776, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[0.783833, [3, -0.533333, 0], [3, 0.4, 0]], [0.487771, [3, -0.4, 0.114667], [3, 0.133333, -0.0382223]], [0.325165, [3, -0.133333, 0], [3, 0.16, 0]], [0.477032, [3, -0.16, 0], [3, 0.16, 0]], [0.325165, [3, -0.16, 0], [3, 0.16, 0]], [0.477032, [3, -0.16, 0], [3, 0.16, 0]], [0.325165, [3, -0.16, 0], [3, 0.16, 0]], [0.477032, [3, -0.16, -0.0407704], [3, 0.44, 0.112119]], [0.783833, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[0.0228, [3, -0.533333, 0], [3, 0.4, 0]], [0.0228, [3, -0.4, 0], [3, 0.133333, 0]], [0.0228, [3, -0.133333, 0], [3, 0.16, 0]], [0.0228, [3, -0.16, 0], [3, 0.16, 0]], [0.0228, [3, -0.16, 0], [3, 0.16, 0]], [0.0228, [3, -0.16, 0], [3, 0.16, 0]], [0.0228, [3, -0.16, 0], [3, 0.16, 0]], [0.0228, [3, -0.16, 0], [3, 0.44, 0]], [0.0228, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RShoulderPitch")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[1.4328, [3, -0.533333, 0], [3, 0.4, 0]], [-1.09523, [3, -0.4, 0.280722], [3, 0.133333, -0.0935741]], [-1.18881, [3, -0.133333, 0], [3, 0.16, 0]], [-1.18881, [3, -0.16, 0], [3, 0.16, 0]], [-1.18881, [3, -0.16, 0], [3, 0.16, 0]], [-1.18881, [3, -0.16, 0], [3, 0.16, 0]], [-1.18881, [3, -0.16, 0], [3, 0.16, 0]], [-1.18881, [3, -0.16, 0], [3, 0.44, 0]], [1.4328, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[-0.158044, [3, -0.533333, 0], [3, 0.4, 0]], [-0.679603, [3, -0.4, 0], [3, 0.133333, 0]], [-0.383541, [3, -0.133333, 0], [3, 0.16, 0]], [-1.00328, [3, -0.16, 0], [3, 0.16, 0]], [-0.383541, [3, -0.16, 0], [3, 0.16, 0]], [-1.00328, [3, -0.16, 0], [3, 0.16, 0]], [-0.383541, [3, -0.16, 0], [3, 0.16, 0]], [-1.00328, [3, -0.16, 0], [3, 0.44, 0]], [-0.158044, [3, -0.44, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([1.6, 2.8, 3.2, 3.68, 4.16, 4.64, 5.12, 5.6, 6.92])
        keys.append([[-0.136568, [3, -0.533333, 0], [3, 0.4, 0]], [-0.385075, [3, -0.4, 0], [3, 0.133333, 0]], [-0.385075, [3, -0.133333, 0], [3, 0.16, 0]], [-0.385075, [3, -0.16, 0], [3, 0.16, 0]], [-0.385075, [3, -0.16, 0], [3, 0.16, 0]], [-0.385075, [3, -0.16, 0], [3, 0.16, 0]], [-0.385075, [3, -0.16, 0], [3, 0.16, 0]], [-0.385075, [3, -0.16, 0], [3, 0.44, 0]], [-0.136568, [3, -0.44, 0], [3, 0, 0]]])

        motionProxy.angleInterpolationBezier(names, times, keys)
        motionProxy.setStiffnesses("Body", 0.0)

    def LedsOff(self, leds):
        intensity = 0.0;
        duration = 1.5;
        name = 'FaceLeds'
        self.leds.fade(name,intensity,duration)
        name = 'EarLeds'
        self.leds.fade(name,intensity,duration)

    def LedsOn(self, leds):
        intensity = 1.0;
        duration = 1.5;
        name = 'FaceLeds'
        self.leds.fade(name,intensity,duration)
        name = 'EarLeds'
        self.leds.fade(name,intensity,duration)
    
def main():
    """ Main entry point
    """
    NAO_IP = '169.254.221.206'
    #NAO_IP = '192.168.1.242'
    #NAO_IP = '127.0.0.1'
    port = 9559

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       NAO_IP,         # parent broker IP
       port)       # parent broker port


    # Warning: IntroLesModule must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global IntroLesModule
    IntroLesModule = IntroLesModule("IntroLesModule")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        self.tts = ALProxy("ALTextToSpeech")
        self.postureProxy = ALProxy("ALRobotPosture")
        self.motionProxy = ALProxy("ALMotion")      
        print
        print "Interrupted by user, shutting down"
        self.tts.say('Oef, ik ben echt moe. Ik ga rusten')
        self.motionProxy.setStiffnesses("Body", 0.0)
        self.myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":    
    main()

    ## rondkijkend


    ## waits for head press

    ## zitten op grond

    ## vertellen dat hij robot in

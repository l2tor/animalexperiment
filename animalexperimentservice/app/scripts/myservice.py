"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'Jan de Wit'
__email__ = 'j.m.s.dewit@uvt.nl'


import qi

import stk.runner
import stk.events
import stk.services
import stk.logging
import random
import json
import time
import datetime

# This class can be considered the "output manager" of the animal experiment.
# It handles all communication with the actual robot -- speech and gesture output, mostly.

# The main flow of the experiment is as follows:
# 1. start_event: robot explains the game and asks whether the child understands
# 2a. did_not_understand: child indicated they did not understand the game (red smiley face on the tablet), game pauses allowing researcher to step in.
# 2b. test_run_event(true): start the first practice round in Dutch.
# 3. practice_event is called, which results in introduce_word_event to say the first practice round in Dutch.
# 4. show_validation_event is called after the child selects an animal on the tablet.
# 5a. If the answer was correct, practice_event is called again, followed by introduce_word_event but now to practice once in English.
# 5b. If the answer was incorrect, the robot gives negative (corrective) feedback and we go back to #3 (but with less distractor items on the tablet screen)
# 6. show_validation_event is called again, now for the English practice round.
# 7a. If the answer was correct, we end the practice round and move on to the actual game rounds.
# 7b. If the answer was incorrect, the robot gives negative (corrective) feedback and we go back to #6 (but with less distractor items on the tablet screen)
# 8. test_run_event(false): disable the test mode and wait for the child to press the green smiley to begin the actual game rounds.
# 9. start_button_clicked_event: introduce the first "real" round, calls describe_object on the interactionmanager which in turn will call introduce_word_event.
# 10. show_validation_event is called for this round.
# 11a. If the answer was correct, positive feedback is given and we proceed to the next round.
# 11b. If the answer was incorrect, negative feedback is given and the child is asked to answer the same question once more -> back to step 10.
# 12. After 30 rounds (or however much was configured), the experiment ends.

class ALAnimalExperimentService(object):
    "NAOqi service for animal experiment."
    APP_ID = "com.aldebaran.ALMyService"

    def __init__(self, qiapp):

        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.gestures = True
        self.gesture_variation = False
        self.paused = False

        # The concepts to be taught, update here if needed!
        self.target_words = {
            "BRIDGE": {
                "English": "bridge",
                "Dutch": "brug",
                "Gesture": {
                    "Id": "VariationGestures/Bridge1",
                    "Pause_before": 2.5,
                    "Pause_after": 2
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Bridge1",
                        "Pause_before": 2.5,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Bridge2",
                        "Pause_before": 2.5,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Bridge3",
                        "Pause_before": 2.5,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Bridge4",
                        "Pause_before": 5,
                        "Pause_after": 3
                    },                
                    {
                        "Id": "VariationGestures/Bridge5",
                        "Pause_before": 1.5,
                        "Pause_after": 1.5
                    }             
                ]
            },
            "STAIRS": {
                "English": "stairs",
                "Dutch": "trap",
                "Gesture": {
                    "Id": "VariationGestures/Stairs2",
                    "Pause_before": 2.5,
                    "Pause_after": 0.5
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Stairs1",
                        "Pause_before": 2.5,
                        "Pause_after": 0.5
                    },                
                    {
                        "Id": "VariationGestures/Stairs2",
                        "Pause_before": 2.5,
                        "Pause_after": 0.5
                    },                
                    {
                        "Id": "VariationGestures/Stairs3",
                        "Pause_before": 4,
                        "Pause_after": 9
                    },                
                    {
                        "Id": "VariationGestures/Stairs4",
                        "Pause_before": 4,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Stairs5",
                        "Pause_before": 4,
                        "Pause_after": 2
                    } 
                ]
            },
            "HORSE": {
                "English": "horse",
                "Dutch": "paard",
                "Gesture": {
                    "Id": "VariationGestures/Horse3",
                    "Pause_before": 4,
                    "Pause_after": 3
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Horse1",
                        "Pause_before": 2.5,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Horse2",
                        "Pause_before": 2.5,
                        "Pause_after": 2
                    },                
                    {
                        "Id": "VariationGestures/Horse3",
                        "Pause_before": 4,
                        "Pause_after": 3
                    },                
                    {
                        "Id": "VariationGestures/Horse4",
                        "Pause_before": 4,
                        "Pause_after": 3
                    },                
                    {
                        "Id": "VariationGestures/Horse5",
                        "Pause_before": 2.5,
                        "Pause_after": 2.5
                    } 
                ]                
            },
            "TURTLE": {
                "English": "turtle",
                "Dutch": "schildpad",
                "Gesture": {
                    "Id": "VariationGestures/Turtle3",
                    "Pause_before": 2.5,
                    "Pause_after": 5
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Turtle1",
                        "Pause_before": 4,
                        "Pause_after": 5.5
                    },                
                    {
                        "Id": "VariationGestures/Turtle2",
                        "Pause_before": 4,
                        "Pause_after": 4
                    },                
                    {
                        "Id": "VariationGestures/Turtle3",
                        "Pause_before": 2.5,
                        "Pause_after": 5
                    },                
                    {
                        "Id": "VariationGestures/Turtle4",
                        "Pause_before": 2.5,
                        "Pause_after": 4
                    },                
                    {
                        "Id": "VariationGestures/Turtle5",
                        "Pause_before": 4,
                        "Pause_after": 1.5
                    } 
                ]                 
            },
            "SPOON": {
                "English": "spoon",
                "Dutch": "lepel",
                "Gesture": {
                    "Id": "VariationGestures/Spoon1",
                    "Pause_before": 2.5,
                    "Pause_after": 5
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Spoon1",
                        "Pause_before": 2.5,
                        "Pause_after": 5
                    },                
                    {
                        "Id": "VariationGestures/Spoon2",
                        "Pause_before": 2,
                        "Pause_after": 7
                    },                
                    {
                        "Id": "VariationGestures/Spoon3",
                        "Pause_before": 4,
                        "Pause_after": 5
                    },                
                    {
                        "Id": "VariationGestures/Spoon4",
                        "Pause_before": 1,
                        "Pause_after": 5.5
                    },                
                    {
                        "Id": "VariationGestures/Spoon5",
                        "Pause_before": 1,
                        "Pause_after": 5
                    } 
                ]    
            },
            "PENCIL": {
                "English": "pencil",
                "Dutch": "potlood",
                "Gesture": {
                    "Id": "VariationGestures/Pencil5",
                    "Pause_before": 1.5,
                    "Pause_after": 5
                },
                "Gestures": [
                    {
                        "Id": "VariationGestures/Pencil1",
                        "Pause_before": 2.5,
                        "Pause_after": 6.5
                    },                
                    {
                        "Id": "VariationGestures/Pencil2",
                        "Pause_before": 2.5,
                        "Pause_after": 2.5
                    },                
                    {
                        "Id": "VariationGestures/Pencil3",
                        "Pause_before": 1.5,
                        "Pause_after": 2.5
                    },                
                    {
                        "Id": "VariationGestures/Pencil4",
                        "Pause_before": 1.5,
                        "Pause_after": 2.5
                    },                
                    {
                        "Id": "VariationGestures/Pencil5",
                        "Pause_before": 1.5,
                        "Pause_after": 5
                    } 
                ]                
            }
        }

        for k, v in self.target_words.iteritems():
            random.shuffle(v['Gestures'])

        #self.isDutchIntro = True
        self.isFirstTestRun = True
        self.isTestRun = True
        self.isLastAnswerWrong = False

        self.round_number = 1
        self.num_rounds = 30

        # Subscribe to events we can expect from the interaction manager
        self.s.ALMemory.subscribeToEvent("animated_tts", "ALAnimalExperimentService", "animated_tts_event")
        self.s.ALMemory.subscribeToEvent("describe_object", "ALAnimalExperimentService", "describe_object_event")
        self.s.ALMemory.subscribeToEvent("skip_object", "ALAnimalExperimentService", "skip_object_event")
        self.s.ALMemory.subscribeToEvent("explain_skill", "ALAnimalExperimentService", "explain_skill_event")
        self.s.ALMemory.subscribeToEvent("dialog_stop", "ALAnimalExperimentService", "stop_tts_event")
        self.s.ALMemory.subscribeToEvent("motivate_request", "ALAnimalExperimentService", "motivate_request_event")
        self.s.ALMemory.subscribeToEvent("sing_a_song", "ALAnimalExperimentService", "sing_a_song_event")
        self.s.ALMemory.subscribeToEvent("repeat_answer", "ALAnimalExperimentService", "repeat_answer_event")
        self.s.ALMemory.subscribeToEvent("look_at", "ALAnimalExperimentService", "look_at_event")
        self.s.ALMemory.subscribeToEvent("round_nr", "ALAnimalExperimentService", "round_number_update_event")
        self.s.ALMemory.subscribeToEvent("gui/buttons", "ALAnimalExperimentService", "gui_buttons_event")
        
        # So far, these are actually used for the animal experiment
        self.s.ALMemory.subscribeToEvent("start", "ALAnimalExperimentService", "start_event")
        self.s.ALMemory.subscribeToEvent("pause", "ALAnimalExperimentService", "pause_event")
        self.s.ALMemory.subscribeToEvent("did_not_understand", "ALAnimalExperimentService", "did_not_understand_event")
        self.s.ALMemory.subscribeToEvent("resume", "ALAnimalExperimentService", "resume_event")
        self.s.ALMemory.subscribeToEvent("test_run", "ALAnimalExperimentService", "test_run_event")
        self.s.ALMemory.subscribeToEvent("introduce_word", "ALAnimalExperimentService", "introduce_word_event")
        self.s.ALMemory.subscribeToEvent("practice", "ALAnimalExperimentService", "practice_event")
        self.s.ALMemory.subscribeToEvent("validation", "ALAnimalExperimentService", "show_validation_event")
        self.s.ALMemory.subscribeToEvent("start_button_clicked", "ALAnimalExperimentService", "start_button_clicked_event")
        self.s.ALMemory.subscribeToEvent("gesture_condition", "ALAnimalExperimentService", "gesture_condition_event")
        self.s.ALMemory.subscribeToEvent("gesture_variation", "ALAnimalExperimentService", "gesture_variation_event")
        self.s.ALMemory.subscribeToEvent("tts", "ALAnimalExperimentService", "tts_event")
        self.s.ALMemory.subscribeToEvent("say_target_word", "ALAnimalExperimentService", "say_target_word_event")

        # Selection of positive feedback sentences
        self.pos_feedback = ["Goed gedaan!",
                        "Helemaal goed!",
                        "Wauw wat goed!",
                        "Ja, dat kloptt!",
                        "Goed zo!",
                        "Supergoed!"]

        self.last_pos_feedback_pick = ''

    # At this moment, we actually never switch out of Dutch.
    # However, this function is still used to set certain language properties such as speed, volume and pitch.
    def tts_set_language(self, lang):
        self.s.ALTextToSpeech.setLanguage(lang)

        if lang == "English":
            self.s.ALTextToSpeech.setParameter("defaultVoiceSpeed", 75)
            self.s.ALTextToSpeech.setParameter("pitchShift", 1.1)
            self.s.ALTextToSpeech.setVolume(1.0)
        else:
            self.s.ALTextToSpeech.setVolume(0.6)
            self.s.ALTextToSpeech.setParameter("defaultVoiceSpeed", 80)
            self.s.ALTextToSpeech.setParameter("pitchShift", 1.2)

    # Called through an event to be able to output any text entered into the control panel.
    def tts_event(self, key, value):
        self.tts_set_language('Dutch')
        self.s.ALAnimatedSpeech.say(value)

    # Selects a positive feedback option while avoiding repetition of the same exact sentence.
    def pos_feedback_picker(self):
        current = self.last_pos_feedback_pick    
        while self.last_pos_feedback_pick == current:
            current = random.choice(self.pos_feedback)

        self.last_pos_feedback_pick = current
        return current

    # Event to set the gesture condition (sent from interactionmanager)
    def gesture_condition_event(self, key, value):
        self.logger.info("Gesture condition is set to: " + str(value))
        if value == 1:
            self.gestures = True
        else:
            self.gestures = False

    # Event to set the gesture variation condition (sent from interactionmanager)
    def gesture_variation_event(self, key, value):
        self.logger.info("Gesture variation is set to: " + str(value))
        if value == 1:
            self.gesture_variation = True
        else:
            self.gesture_variation = False

    # This event is triggered after the robot explains the game, if the participant
    # selects the red smiley face (indicating they did not understand the instructions).
    # This stops the interaction so that the experimenter can step in. The remaining green
    # smiley can be used to resume the interaction.
    def did_not_understand_event(self, key, value):
        self.logger.info("did_not_understand_event")
        print "== Child did not understand the game =="
        self.s.ALTextToSpeech.say("Ok, dat geeft niet, dan leggen we het gewoon nog een keer uit!")

    # Unused event.
    def animated_tts_event(self, key, value):
        self.logger.info("animated_tts_event")

    # Unused event.        
    def describe_object_event(self, key, value):
        self.logger.info("describe_object_event")

    # Unused event.        
    def skip_object_event(self, key, value):
        self.logger.info("skip_object_event")

    # Unused event.
    def explain_skill_event(self, key, value):
        self.logger.info("explain_skill_event")

    # Unused event.
    def stop_tts_event(self, key, value):
        self.logger.info("stop_tts_event")

    # Unused event.
    def motivate_request_event(self, key, value):
        self.logger.info("motivate_request_event")

    # Unused event.    
    def sing_a_song_event(self, key, value):
        self.logger.info("sing_a_song_event")

    # This starts the actual experiment (after two practice rounds).
    def start_button_clicked_event(self, key, value):
        self.experiment_start = datetime.datetime.now()
        self.s.ALTextToSpeech.say("Joepie!")
        self.s.ALTextToSpeech.say("Daar gaan we dan.")

        # This is a call to the interactionmanager, essentially triggering the start of the next round.
        self.s.ALMemory.raiseEvent("describe_object", "")

    # This is a practice round (first in Dutch, then in English).
    def practice_event(self, key, value):       
        self.tts_set_language("Dutch") 

        # If this is the first practice round, and the first attempt at answering it, we add some explanation
        # of what is happening on the tablet screen, and introduce the task.
        if self.isFirstTestRun and not self.isLastAnswerWrong:
            self.s.ALMemory.raiseEvent("show_images", False)
            practice_1 = ["Kijk!",
                    "Op de \prn=t E: b l @ t \ zijn een boell plaatjes verschenen.",
                    "\\pau=500\\Ok.",
                    "Nu gaan we oefenen\\pau=250\\"]
            
            for line in practice_1:
                print line
                self.s.ALTextToSpeech.say(line)

        self.introduce_word_event(key, value)
    
    # Introduce a new task by playing "I spy with my little eye..."
    def introduce_word_event(self, key, value):
        self.tts_set_language("Dutch")

        if self.paused:
            return

        self.logger.info("introduce_word_event")
        
        # This is the first introduction round (in Dutch)
        if self.isFirstTestRun:
            the_item = self.target_words["HORSE"]

            # If this is the first time the item is presented, the robot pronounces the entire task.
            if not self.isLastAnswerWrong:
                if self.gestures:
                    self.s.ALTextToSpeech.say('Ik zie ik zie wat jij niet ziet, en het is een')
                    self.s.ALBehaviorManager.startBehavior(the_item["Gesture"]["Id"])        
                    # self.s.ALAudioDevice.setOutputVolume(80)
                    time.sleep(the_item["Gesture"]["Pause_before"])
                    self.s.ALTextToSpeech.say(the_item["Dutch"])
                    # self.s.ALAudioDevice.setOutputVolume(60)
                    time.sleep(the_item["Gesture"]["Pause_after"])
                    self.s.ALTextToSpeech.say('Tik maar op het ' + the_item["Dutch"])
                    # self.s.ALAnimatedSpeech.say("Ik zie ik zie wat jij niet ziet, en het is een ^start(Animals/Chicken) \\pau=2600\\. ^runSound(Test/kip) ^wait(Animals/Chicken). Tik maar op de \\pau=500\\ ^runSound(Test/kip)")
                
                else: 
                    self.s.ALTextToSpeech.say('Ik zie ik zie wat jij niet ziet, en het is een..')
                    self.s.ALTextToSpeech.say(the_item["Dutch"])
                    self.s.ALTextToSpeech.say('Tik maar op het..')
                    self.s.ALTextToSpeech.say(the_item["Dutch"])

                    # self.s.ALAnimatedSpeech.say("Ik zie ik zie wat jij niet ziet, en het is een.. ^runSound(Test/kip). \\pau=500\\ Tik maar op de \\pau=500\\ ^runSound(Test/kip)")
           
            # If this is a correction step (after incorrect answer), we don't introduce the full task but only repeat the target word
            else:#if self.isLastAnswerWrong:
                if self.gestures:
                    self.s.ALTextToSpeech.say('Tik maar op het')
                    self.s.ALBehaviorManager.startBehavior(the_item["Gesture"]["Id"])        
                    # self.s.ALAudioDevice.setOutputVolume(80)
                    time.sleep(the_item["Gesture"]["Pause_before"])
                    self.s.ALTextToSpeech.say(the_item["Dutch"])
                    # self.s.ALAudioDevice.setOutputVolume(60)
                    time.sleep(the_item["Gesture"]["Pause_after"])        

                    # self.s.ALAnimatedSpeech.say("Tik maar op de ^start(Animals/Chicken) \\pau=3100\\. ^runSound(Test/kip) ^wait(Animals/Chicken).")

                else:
                    self.s.ALTextToSpeech.say('Tik maar op het..')
                    self.s.ALTextToSpeech.say(the_item["Dutch"])

                    # self.s.ALAnimatedSpeech.say("Tik maar op de \\pau=500\\ ^runSound(Test/kip)")
            
        # This is either the English test run or an actual round (not the Dutch test run)
        else:
            # If this is the first time the item is presented, the robot pronounces the entire task.
            if not self.isLastAnswerWrong:

                # When introducing some specific rounds, we let the robot make a small motivational statement to indicate that progress is being made.
                if self.round_number > 1:
                    if self.num_rounds / float(self.round_number - 1) == 2: # half way
                        self.s.ALTextToSpeech.say("We zijn al op de helft! \\pau=250\\") 
                    if self.num_rounds / float(self.round_number - 1) == 1.5: # 20/30
                        self.s.ALTextToSpeech.say("We zijn al best wel ver! \\pau=250\\")
                    if self.num_rounds / float(self.round_number - 1) == 1.2: # 25/30
                        self.s.ALTextToSpeech.say("We zijn bijna klaar! \\pau=250\\")
                    if self.num_rounds - self.round_number == 0:
                        self.s.ALTextToSpeech.say("Nu komt de laatste! \\pau=250\\")

                # In earlier rounds, we also have the robot announce the next round but we gradually drop this as the child gets to know the game.
                if not self.isTestRun and self.round_number == 2:
                    self.s.ALTextToSpeech.say("Laten we doorgaan met de volgende. \\pau=250\\")
                if self.round_number > 2 and self.round_number < 6:
                    self.s.ALTextToSpeech.say("Nu komt het volgende ding. \\pau=250\\")
                if self.round_number > 5 and self.round_number < 9:
                    self.s.ALTextToSpeech.say("Volgende! \\pau=250\\")

                if self.gestures:
                    the_gesture = self.target_words[value]["Gesture"]

                    if self.gesture_variation and not self.isTestRun:
                        the_gesture = self.target_words[value]["Gestures"][int((self.round_number - 1) / 6)]
                        self.s.ALMemory.raiseEvent("log", "gesture_performed: " + the_gesture["Id"])
                        print "taking index " + str(int((self.round_number - 1) / 6)) + " for gesture in round " + str(self.round_number)

                    self.s.ALTextToSpeech.say('Ik zie ik zie wat jij niet ziet, en het is een')
                    if the_gesture["Id"] == 'VariationGestures/Bridge3' or the_gesture["Id"] == 'VariationGestures/Turtle5':
                        self.s.ALMotion.moveTo(0.0, 0.0, 1.0, [["MaxStepFrequency", 0.25]])

                    self.s.ALBehaviorManager.startBehavior(the_gesture["Id"])        
                    self.s.ALAudioDevice.setOutputVolume(80)
                    time.sleep(the_gesture["Pause_before"])
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)
                    time.sleep(the_gesture["Pause_after"])
                    self.s.ALTextToSpeech.say('Tik maar op de')
                    self.s.ALAudioDevice.setOutputVolume(80)
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)
                    if the_gesture["Id"] == 'VariationGestures/Bridge3' or the_gesture["Id"] == 'VariationGestures/Turtle5':
                        self.s.ALMotion.moveTo(0.0, 0.0, -0.75, [["MaxStepFrequency", 0.25]])
                    # self.s.ALAnimatedSpeech.say("Ik zie ik zie wat jij niet ziet, en het is een " + self.target_words[value]['AnimatedSpeechTag'] + ". Tik maar op de \\pau=500\\ ^runSound(" + self.target_words[value]['SoundSetName'] + ")")

                else:
                    self.s.ALTextToSpeech.say('Ik zie ik zie wat jij niet ziet, en het is een..')
                    self.s.ALAudioDevice.setOutputVolume(80)
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)
                    self.s.ALTextToSpeech.say('Tik maar op de..')
                    self.s.ALAudioDevice.setOutputVolume(80)
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)

                    # self.s.ALAnimatedSpeech.say("Ik zie ik zie wat jij niet ziet, en het is een.. ^runSound(" + self.target_words[value]['SoundSetName'] + "). \\pau=500\\ Tik maar op de \\pau=500\\ ^runSound(" + self.target_words[value]['SoundSetName'] + ")")

            # If this is a correction step (after incorrect answer), we don't introduce the full task but only repeat the target word
            if self.isLastAnswerWrong:
                if self.gestures:
                    the_gesture = self.target_words[value]["Gesture"]

                    if self.gesture_variation and not self.isTestRun:
                        the_gesture = self.target_words[value]["Gestures"][int((self.round_number - 1) / 6)]
                        self.s.ALMemory.raiseEvent("log", "gesture_performed: " + the_gesture["Id"])
                        print "taking index " + str(int((self.round_number - 1) / 6)) + " for gesture in round " + str(self.round_number)

                    self.s.ALTextToSpeech.say('Tik maar op de')

                    if the_gesture["Id"] == 'VariationGestures/Turtle3' or the_gesture["Id"] == 'VariationGestures/Turtle5':
                        self.s.ALMotion.moveTo(0.0, 0.0, 1.0, [["MaxStepFrequency", 0.25]])                   

                    self.s.ALBehaviorManager.startBehavior(the_gesture["Id"])        
                    self.s.ALAudioDevice.setOutputVolume(80)
                    time.sleep(the_gesture["Pause_before"])
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)
                    time.sleep(the_gesture["Pause_after"])              

                    if the_gesture["Id"] == 'VariationGestures/Turtle3' or the_gesture["Id"] == 'VariationGestures/Turtle5':
                        self.s.ALMotion.moveTo(0.0, 0.0, -0.75, [["MaxStepFrequency", 0.25]])                           

                    # self.s.ALAnimatedSpeech.say("Tik maar op de " + self.target_words[value]['AnimatedSpeechTag'] + ".")
                else:
                    self.s.ALTextToSpeech.say('Tik maar op de..')
                    self.s.ALAudioDevice.setOutputVolume(80)
                    self.s.ALTextToSpeech.say(self.target_words[value]["English"], 'English')
                    self.s.ALAudioDevice.setOutputVolume(60)

                    # self.s.ALAnimatedSpeech.say("Tik maar op de \\pau=500\\ ^runSound(" + self.target_words[value]['SoundSetName'] + ")")
        

        if self.paused:
            return

        # Show images on the tablet for the child to answer.
        self.s.ALMemory.raiseEvent("show_images", True)      

    # Either begin or end a practice round.
    def test_run_event(self, key, value):
        # Begin a practice round.
        if value:
            self.isTestRun = True
            practice_0 = ["Je snapt het, supergoed!",
                    "Laten we het een keertje oefenen."]

            for line in practice_0:
                print line
                self.s.ALTextToSpeech.say(line)

            self.s.ALMemory.raiseEvent("describe_object", "");

        # Done with the two practice rounds -- start the actual game!
        else:
            self.isTestRun = False
            self.s.ALMemory.raiseEvent("hide_images", "")
            self.s.ALMemory.raiseEvent("round_nr", self.round_number)            
            test_done = ["Ok.", 
                "Ik denk dat je klaar bent om het echte spel te \prn=s p e2 l1 @1 n\.",
                "Druk maar op het groene gezichtje om te beginnen."]

            for line in test_done:
                print line
                self.s.ALTextToSpeech.say(line)

            # Show the green smiley face on the tablet, allowing the child to start the actual game.
            self.s.ALMemory.raiseEvent("show_start_button", "")

    # Unused event.
    def repeat_answer_event(self, key, value):
        self.logger.info("repeat_answer_event");

    # Unused event.
    def look_at_event(self, key, value):
        self.logger.info("look_at_event");

    # Unused event.
    def round_number_update_event(self, key, value):
        self.logger.info("round_number_update_event")
        print "--- round number update event " + str(value)

    # Unused event.
    def gui_buttons_event(self, key, value):
        self.logger.info("gui_buttons_event");

    # We receive feedback (from the interactionmanager) on the child's answer to a task.
    # This can be either correct or incorrect.
    # The "value" parameter contains a JSON object, which we parse into "result". It contains:
    # - 'is_correct': 'True' or 'False', whether the child answered the task correctly
    # - 'answer': the ID of the answer that was given (can be used to look up things in self.target_words)
    # - 'correct_answer': the ID of the correct answer for the current task
    def show_validation_event(self, key, value):
        self.tts_set_language("Dutch")
        
        self.logger.info("show_validation_event " + key + " " + value)

        result = json.loads(value)

        # Child answered correctly -- give positive feedback
        if result['is_correct'] == 'True':
            # Log the end time of the experiment
            if self.round_number >= self.num_rounds:
                diff = datetime.datetime.now() - self.experiment_start
                self.s.ALMemory.raiseEvent("log", "[training_time_ms]" + str(int(diff.total_seconds() * 1000)))

            self.isLastAnswerWrong = False
            # Say the positive feedback utterance (randomly selected from a set)
            self.s.ALTextToSpeech.say(self.pos_feedback_picker())
            # Mention the correct answer once more as confirmation
            self.s.ALTextToSpeech.say("Het Engelse woord voor " + self.target_words[result['answer']]['Dutch'] + " is")
            self.s.ALAudioDevice.setOutputVolume(80)
            self.s.ALTextToSpeech.say(self.target_words[result['answer']]['English'], 'English')
            self.s.ALAudioDevice.setOutputVolume(60)
            # self.s.ALAnimatedSpeech.say("Het Engelse woord voor " + self.target_words[result['answer']]['Dutch'] + " is \\pau=500\\ ^runSound(" + self.target_words[result['answer']]['SoundSetName'] + ")")

            # If we are not in a test run anymore we increment the round number after a correct answer
            if not self.isTestRun:
                self.round_number = self.round_number + 1
                if self.round_number <= self.num_rounds:
                    self.s.ALMemory.raiseEvent("round_nr", self.round_number)

            if self.isTestRun and not self.isFirstTestRun:
                # Disable "test mode"
                self.s.ALMemory.raiseEvent("test_run", False)
                return # Don't start the next assignment yet, start button first..

            # If we were in the first test run (in Dutch), we explain that we will now move on to English
            if self.isFirstTestRun:
                practice_1 = ["Maar dat was makkelijk, want ik zei het al voor!",
                    "Nog een keer!", 
                    "Nu maak ik het wel wat moeilijker.",
                    "Ik ga een Engels woord vragen!",
                    "Let op!"]

                for line in practice_1:
                    print line
                    self.s.ALTextToSpeech.say(line)

                self.isFirstTestRun = False

            # If we're not done yet, describe the next item
            if self.round_number <= self.num_rounds:
                if self.paused:
                    return
                self.s.ALMemory.raiseEvent("describe_object", "")

            # We're done, end the experiment!
            else:   
                self.s.ALMemory.raiseEvent("confetti", "")             
                self.s.ALTextToSpeech.say("Dat was het dan, ik vond het leuk! Joepie. Tot de volgende keer!")
                diff = datetime.datetime.now() - self.intro_start
                self.s.ALMemory.raiseEvent("log", "[total_experiment_time_ms]" + str(int(diff.total_seconds() * 1000)))
                self.s.ALMemory.raiseEvent("experiment_done", "")
                self.stop()
        
        # The child answered incorrectly -> mention the task once more and ask the child to perform it again (with only one distractor image)
        else:
            self.isLastAnswerWrong = True
            if self.isFirstTestRun: #self.isDutchIntro:
                self.s.ALAnimatedSpeech.say("Dat was een " + self.target_words[result['answer']]['Dutch'] + ", maar ik zag een \\pau=500\\, " + self.target_words[result['correct_answer']]['Dutch'] + " \\pau=500\\")
            else:
                # self.s.ALAnimatedSpeech.say("Dat was een " + self.target_words[result['answer']]['Dutch'] + ", maar ik zag een \\pau=500\\, ^runSound(" + self.target_words[result['correct_answer']]['SoundSetName'] + ") \\pau=500\\")
                self.s.ALTextToSpeech.say("Dat was een " + self.target_words[result['answer']]['Dutch'] + ", maar ik zag een")
                self.s.ALAudioDevice.setOutputVolume(80)
                self.s.ALTextToSpeech.say(self.target_words[result['correct_answer']]['English'], 'English')
                time.sleep(1)
                self.s.ALTextToSpeech.say(self.target_words[result['correct_answer']]['English'], 'English')
                self.s.ALAudioDevice.setOutputVolume(60)
                self.s.ALTextToSpeech.say("is het Engelse woord voor " + self.target_words[result['correct_answer']]['Dutch'])

                # self.s.ALAnimatedSpeech.say("^runSound(" + self.target_words[result['correct_answer']]['SoundSetName'] + ") is het Engelse woord voor " + self.target_words[result['correct_answer']]['Dutch'] + ".")

            if self.paused:
                return

            self.s.ALMemory.raiseEvent("explain_skill", "")

        time.sleep(1)
        
    # Pause the game (until resume button is pressed on the control panel)
    def pause_event(self, key):
        print "=== interaction paused ==="
        # Actually stopping the running speech and behavior does not seem to work, as this event doesn't come in in time.
        # Therefore we just prevent the game from going to the next round.
        self.paused = True

    # Resume the game, this will again present the round at which the game was paused
    def resume_event(self, key):
        print "=== interaction resumed ==="
        self.paused = False
        if self.isLastAnswerWrong:
            self.s.ALMemory.raiseEvent("explain_skill", "")
        else:
            self.s.ALMemory.raiseEvent("describe_object", "")


    def say_target_word_event(self, dummy, word):      
        self.s.ALAudioPlayer.playFile('/home/nao/' + word + '.wav')

    # The start button on the control panel is pressed -> start the interaction by introducing the game.
    # The name of the child (entered in the control panel) is passed as "value"
    def start_event(self, key, value):
        self.logger.info("Start introduction")
        print "start intro"
        self.tts_set_language("Dutch")

        self.s.ALMemory.raiseEvent("log", "Child name: " + value)
        self.s.ALMemory.raiseEvent("ding", "")            
        self.s.ALMemory.raiseEvent("log", "*ding*")        

        # Initialize the robot's position: standing, without animated speech (BodyLanguageMode == 0)
        self.s.ALRobotPosture.goToPosture("Stand", 0.3)
        self.s.ALAnimatedSpeech.setBodyLanguageMode(0)

        # Set breathing mode
        self.s.ALMotion.setBreathEnabled("Head", True)
        time.sleep(1)
        self.s.ALMotion.setBreathEnabled("Body", True)
        self.s.ALAudioDevice.setOutputVolume(60)

        # Temporary test code
        # self.s.ALTextToSpeech.say('Ik zie ik zie wat jij niet ziet, en het is een')
        # self.s.ALMotion.moveTo(0.0, 0.0, 1.0, [["MaxStepFrequency", 0.25]])
        # self.s.ALBehaviorManager.startBehavior("VariationGestures/Turtle5")        
        # self.s.ALAudioDevice.setOutputVolume(80)
        # time.sleep(4)
        # self.s.ALTextToSpeech.say('turtle', 'English')
        # self.s.ALAudioDevice.setOutputVolume(60)
        # time.sleep(1.5)
        # self.s.ALTextToSpeech.say('Tik maar op de')
        # self.s.ALBehaviorManager.startBehavior("VariationGestures/Turtle5")        
        # self.s.ALAudioDevice.setOutputVolume(80)
        # time.sleep(4)
        # self.s.ALTextToSpeech.say('turtle', 'English')
        # self.s.ALAudioDevice.setOutputVolume(60)
        # time.sleep(1.5)        
        # self.s.ALMotion.moveTo(0.0, 0.0, -0.75, [["MaxStepFrequency", 0.25]])

        # Introduce the game
        intro = ["Hallo "+value+"!",
                "Wat leuk je weer te zien!",
                "\\pau=100\\Ken je me nog?",
                "Ik ben Robin!",
                "Laten we een spelletje spelen!",
                "Mijn lievelingsspelletje is 'ik zie ik zie wat jij niet ziet'.",
                "Vandaag gaan we dat spelen op de \prn=t E: b l @ t \!",
                "Daar verschijnen zo plaatjes op.",
                "Als ik zeg 'ik zie ik zie wat jij niet ziet, en het is een, puntje puntje puntje', dan moet jij aanraken welk ding je denkt dat ik zie.",
                "Snap je dat?",
                "Druk maar op het groene gezichtje als je het snapt.",
                "Als je het niet snapt dan moet je drukken op het rode gezichtje."]

        self.intro_start = datetime.datetime.now()

        for line in intro:
            print line
            self.s.ALTextToSpeech.say(line)

        # Show green/red smiley on screen to trigger the next step of the game.
        self.s.ALMemory.raiseEvent("activate_faces", "true");

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        self.logger.info("ALMyService stopped by user request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        self.logger.info("ALMyService finished.")

####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(ALAnimalExperimentService)


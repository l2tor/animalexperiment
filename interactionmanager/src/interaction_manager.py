import operator
import argparse
import json
import csv
import copy
import utils
from random import randint, shuffle
from robot_gate import NaoRobotGate
from tablet_gate import TabletGate
from time import sleep
from robot import Robot
from event_module_name import EventModuleName
from child_model import ChildModel
from child_emo_model import ChildEmoModel
from child_random_model import ChildRandomModel
import logging
import os
import sys

robot_gate = None
tablet_gate = None
int_manager = None

class InteractionManager:
    # log-level
    LOG_LEVEL = 21

    def __init__(self, mode, sgroups, l1, l2, concepts, cbindings, overall_round_nr, gestures):
        """
            Constructor to initialize the interaction manager. It loads the lesson-files from the harddrive and
            initialize the child model.
        """
        self._skill_groups = sgroups
        self._L1 = l1
        self._L2 = l2

        # determine the last participant-number i and create new file with number i+1
        file_numbers = [0, ]
        for root, directories, files in os.walk("../data/vp"):
            for filename in files:
                file_numbers.append(int(filename.split("_")[1]))
        
        FORMAT = '%(asctime)s %(message)s'
        logging.basicConfig(format=FORMAT, filename='../data/vp/vp_' + str(max(file_numbers)+1), level=self.LOG_LEVEL)
        logging.log(self.LOG_LEVEL, "===" + json.dumps(mode) + "===")
        logging.log(self.LOG_LEVEL, "=== Gesture: " + json.dumps(gestures == 1) + " ===")

        # initialize the callback-handler for robot events
        global robot_gate
        robot_gate = NaoRobotGate(EventModuleName.ROBOT_GATE_CALLBACK, self)

        # initialize the callback-handler for tablet events
        global tablet_gate
        tablet_gate = TabletGate(EventModuleName.TABLET_GATE_CALLBACK, self)

        # set gesture condition
        robot_gate.setGestureCondition(gestures)

        # load lesson files
        self._load_voc(concepts, cbindings)

        skills_to_teach = []
        for skg in self._skill_groups:
            skills_to_teach.extend(self._concepts["skills"][skg].keys())

        print skills_to_teach

        # init child model
        if mode == "adaptive":
            print "adaptive"
            self._child = ChildModel(skills_to_teach, overall_round_nr)
        else:
            print "mode random"
            self._child = ChildRandomModel(skills_to_teach)

        self._emo_child = ChildEmoModel()
        self._correct_answer = None
        self._given_answer = None
        self._last_task_objects = None
        self._test_run = False

        # start main
        self.main()

    def switch_test_run_activation(self, value):
        """
            Switch the to a test-mode of the system to make sure the user understood the task.
        """
        print "Setting test run to " + str(value)
        self._test_run = value
        self._child.set_test_mode(self._test_run)
        logging.log(self.LOG_LEVEL,
                    "========================== test_mode: "
                    + json.dumps(self._test_run)
                    + " ==========================")

    def get_child(self):
        """
            Getter for the current child-model.

            :return: The current instance of the child-model.
        """
        return self._child

    def _load_voc(self, cf, cbf):
        """
            Loads the files with the skills to be teached from the hard-drive.

            :param cf Path to the csv-file of concepts.
            :param cbf Path to the csv-file of concept bindings.
        """
        self._concepts = {'objects': {}, 'skills': {}}
        self._concept_bindings = {}

        # read file with concept-bindings and store it in self._concept_bindings
        with open(cbf, 'rb') as concept_bindings_file:
            # open file
            binding_reader = csv.reader(concept_bindings_file, delimiter=';', quotechar='|')
            # first line are header information so mark them
            first_row = True
            header = None
            # read each file
            for row in binding_reader:
                # if header
                if first_row:
                    header = row
                    first_row = False
                    continue
                # insert new concept
                concept = row[0]
                self._concept_bindings.update({concept: {}})
                # with all attributes
                for i in xrange(0, len(row)):
                    self._concept_bindings[concept].update({header[i]: row[i]})

        # open file with concepts
        with open(cf, 'rb') as concept_file:
            # read file
            concept_reader = csv.reader(concept_file, delimiter=';', quotechar='|')
            # mark first row as header
            first_row = True
            header = None
            # for each row
            for row in concept_reader:
                # if header
                if first_row:
                    header = row
                    first_row = False
                    continue
                # save concept
                concept_id = row[0]
                self._concepts['objects'].update({concept_id: {'id': concept_id}})

                # and save attributes of the concept
                for i in xrange(1, len(row)):
                    self._concepts['objects'][concept_id].update({header[i]: row[i]})
                    # build groups of attributes ...
                    if header[i] in self._concepts['skills'].keys():
                        if row[i] not in self._concepts['skills'][header[i]].keys():
                            self._concepts['skills'][header[i]].update({row[i]: []})
                    else:
                        self._concepts['skills'].update({header[i]: {row[i]: []}})
                    # and sort the objects to the corresponding attribute
                    self._concepts['skills'][header[i]][row[i]].append(concept_id)

    def _configure_task(self, next_action):
        """
            This function selects items which should be used for the next action and skill.

            :param next_action: Tuple with next action for next skill
            :return: return list of items which should be used for the task.
        """
        # extract skill and action
        skill, action, _ = next_action
        # get the possible objects
        objects = self._concepts["objects"]
        # get the different skills of the current skill-group
        skills = None
        for skg in self._concepts["skills"]:
            if skg in self._skill_groups and skill in self._concepts["skills"][skg]:
                skills = self._concepts["skills"][skg]
        task_objects = []

        # get all objects which have the skill to be taught next
        objects_with_skill = skills[skill]
        # get the name of the object which will be the next right answer for the skill to be taught
        c_object_name = objects_with_skill[randint(0, len(objects_with_skill) - 1)]
        # add this object to the list of the objects for the setting
        task_objects.append(objects[str(c_object_name)])

        # if probe_skill then choose only on other object for the setting, which don't have the same skill
        if action == "probe_skill":
            while True:
                # choose other obj with not the same skill
                a_skill = skills.keys()[randint(0, len(skills.keys()) - 1)]
                if a_skill != skill:
                    skill_objects = skills[a_skill]
                    # get a random object
                    object_name = skill_objects[randint(0, len(skill_objects) - 1)]
                    # get the corresponding object to the object_name
                    task_objects.append(objects[str(object_name)])
                    break
        elif action == "task_h" or action == "task_m":
            object_count = 3 if "m" in action else 4
            # choose 3 to 4 objects
            chosen_objects = [c_object_name, ]

            available_skills = skills.keys()
            available_skills.remove(skill)
            shuffle(available_skills)
            while len(available_skills) < object_count - 1:
                # fill_up available_skills to object count
                tmp_object_list = copy.deepcopy(available_skills)
                shuffle(tmp_object_list)
                tmp_object_list.extend(available_skills)
                available_skills = tmp_object_list

            while len(chosen_objects) < object_count:
                # choose other obj with not the same skill
                a_skill = available_skills.pop()
                # if a_skill != skill:
                skill_objects = copy.deepcopy(skills[a_skill])
                for item in chosen_objects:
                    if item in skill_objects:
                        skill_objects.remove(item)

                tmp_obj = skill_objects[randint(0, len(skill_objects)-1)]
                if tmp_obj not in chosen_objects:
                    chosen_objects.append(tmp_obj)
                    task_objects.append(objects[str(tmp_obj)])

        elif action == "explanation":
            # explain the skill again; maybe skill + wrong answer?
            task_objects.append(objects[self._given_answer])

        return task_objects

    def repeat_answer(self):
        """
            Let the nao say "fesuti means red" for instance.
        """
        # get last action and skill
        last_action = self._child.get_last_action()
        next_action = copy.deepcopy(last_action)
        # use the last skill and make an explanation
        next_action[1] = "explanation"

        self._tts_task(next_action)

    def give_explanation(self):
        """
            This function initiates an explanation of the last used and wrong answered skill.
        """
        logging.log(self.LOG_LEVEL, "[mode]Explanation")
        # get last action and skill
        last_action = self._child.get_last_action()
        next_action = copy.deepcopy(last_action)
        # use the last skill and make an explanation
        next_action[1] = "explanation"
        self._child.set_last_action(next_action)

        # get right task_objects to display on screen (wrongly chosen object and the right one)
        task_objects = [x for x in self._last_task_objects if x["id"] == self._given_answer
                        or x["id"] == self._correct_answer]  # self._configure_task(next_action)

        # show them on display
        tablet_gate.set_task(json.dumps(task_objects))
        #if self._child.show_skilltext(next_action[0]):
        #    tablet_gate.show_skilltext(str(self._concept_bindings[next_action[0]]["displaytext"]))
        # tts for the explanation
        self._tts_task(next_action)

    def log(self, string):
        logging.log(self.LOG_LEVEL, string)

    def log_screen_layout(self, objects):
        logging.log(self.LOG_LEVEL, "[screen_layout]" + objects)

    def skip_explanation(self):
        """
            Skip the current task and go on with a new one. Might only work with the random model.
            Currently not used....
        """
        self._child.set_last_action(None)

    def motivate_request(self):
        """
            Determine if the user has to be motivated w.r.t.
            the next skill-action pair which would be used for teaching.
        """
        # get skill lvl for next skill and motivation
        _, action, _ = self._child.get_next_action(logger=False, sim=True)
        action_diff = self._child.get_action_difficulty(action)
        motivation = self._emo_child.get_motivation()

        print motivation
        logging.log(self.LOG_LEVEL, "[ml]" + json.dumps(motivation))

        # if motivation too low --> motivate
        if motivation == "L" or (action_diff == "H" and motivation == "M"):
            logging.log(self.LOG_LEVEL, "[m]" + json.dumps("motivated!"))
            # robot_gate.animated_tts("Ich motiviere dich jetzt.")
            self._emo_child.reset_motivation()
        robot_gate.action_finished()

    def give_task(self):
        """
            This function initiates a task with middle or high difficult or
            a task with low difficult to test the skill level of the child.
        """
        # repeat the last task?
        last_action = self._child.get_last_action()
        if not self._given_answer and last_action:
            next_action = last_action
            task_objects = self._last_task_objects
        # else: prepare for new task
        else:
            self._given_answer = None
            self._correct_answer = None
            next_action = self._child.get_next_action(sim=self._test_run)

            # get items for the new task
            # generate 10 settings and use the one which is the most difficult
            settings = []
            for _ in xrange(10):
                objs = self._configure_task(next_action)
                prob = 0.0
                for obj in objs:
                    for skg in self._skill_groups:
                        prob += utils.sum_to_percentage(self._child.get_belief(obj[skg]),
                                                        self._child.BIN_MEANING)
                settings.append((objs, prob))
            task_objects = min(settings, key=operator.itemgetter(1))[0]
            # set it as right answer
            self._correct_answer = task_objects[0]['id']
            shuffle(task_objects)
            self._last_task_objects = task_objects

        print str(next_action[1]) + " for skill " + str(next_action[0])

        # show items on screen
        print json.dumps(task_objects)
        tablet_gate.set_task(json.dumps(task_objects))

        #if self._child.show_skilltext(next_action[0]):
        #    tablet_gate.show_skilltext(str(self._concept_bindings[next_action[0]]["displaytext"]))

        # tts for task
        self._tts_task(next_action)

    def _tts_task(self, action):
        """
            This function produces for the current action a sentence and let the Nao speak it.

            :param action: The action to do for the current specific skill. Tuple(skill, action)
        """
        robot_gate.change_language(self._L1)
        if action[1] == "explanation":
            robot_gate.raise_event("introduce_word", self._concept_bindings[action[0]]['concept'])
            # robot_gate.change_language(self._L2)
            #robot_gate.animated_tts(str(self._concept_bindings[action[0]][self._L2]))
            # robot_gate.change_language(self._L1)
            #robot_gate.animated_tts(str("heisst " + self._concept_bindings[action[0]][self._L1]))
        else:            
            if self._test_run:
                robot_gate.raise_event('practice', self._concept_bindings[action[0]]['concept'])
            else:
                robot_gate.raise_event("introduce_word", self._concept_bindings[action[0]]['concept'])
            #robot_gate.animated_tts("Ich sehe was was du nicht siehst und das ist")
            # robot_gate.change_language(self._L2)
            #robot_gate.animated_tts(str(self._concept_bindings[action[0]][self._L2]))
            # robot_gate.change_language(self._L1)
        #robot_gate.action_finished()

    def validate_answer(self, answer):
        """
            This function will be called if the child gave an answer via touch on the screen and validates
            the given answer.

            :param answer: The answer given by the child.
        """
        self._given_answer = answer
        # show on the screen if answer is valid
        print self._correct_answer, answer, self._correct_answer == answer
        logging.log(self.LOG_LEVEL, "[ca;a]" + json.dumps(self._correct_answer) + ";" + json.dumps(answer))

        #tablet_gate.show_validation(str(self._correct_answer == answer))
        validation_data = {'answer': answer, 'correct_answer': self._correct_answer, 'is_correct': str(self._correct_answer == answer)}
        tablet_gate.show_validation(json.dumps(validation_data))
        if not self._test_run:
            # update belief of the skill
            self._child.update_belief("+O" if self._correct_answer == answer else "-O")
            self._emo_child.update_motivation(self._correct_answer == answer)

    def stop(self):
        global interrupted
        interrupted = True

    def log_answer_time(self, time):
        logging.log(self.LOG_LEVEL, "[time_on_task_ms]" + json.dumps(time))
        logging.log(self.LOG_LEVEL, "=====================================================================")

    def update_round_number(self, number):
        """
            This function updates the internal counter which round is currently played. This number is used
            to make sure every skill will be taught at least once.

            :param number: The new round number.
        """
        self._child.update_round_number(number)

    def main(self):
        # let Nao stand up and breath
        #robot_gate.stand_up(breath=True)
        #robot_gate.change_language(self._L1)
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.178.21", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    parser.add_argument("--mode", type=str, default="adaptive", help="Value could be: 'random' or 'adaptive'")
    parser.add_argument("--sgroups", nargs="+", help="List of Skillgroups e.g.: 'color' 'size'")
    parser.add_argument("--L1", type=str, default="German", help="German, English, Turkish")
    parser.add_argument("--L2", type=str, default="English", help="German, English, Turkish")
    parser.add_argument("--rnr", type=int, default=30, help="The count of rounds to be played.")
    parser.add_argument("--concepts", type=str, default="../data/study_1/lesson_concepts.csv",
                        help="Path to the concept csv-file.")
    parser.add_argument("--cbindings", type=str, default="../data/study_1/lesson_concept_bindings.csv",
                        help="Path to the concept-bindings csv-file.")
    parser.add_argument("--sysip", type=str, default="192.168.178.22",
                        help="The system-IP on which the IM is running on.")
    parser.add_argument("--gestures", type=int, default=1, help="Gesture condition (1 = on, 0 = off)")

    args = parser.parse_args()
    Robot.connect(args.ip, args.port, args.sysip)
    int_manager = InteractionManager(args.mode, args.sgroups, args.L1, args.L2, args.concepts, args.cbindings, args.rnr, args.gestures)

    global interrupted
    interrupted = False

    while True:
        sleep(1)

        if interrupted:
            break
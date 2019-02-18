# License #

This code was developed as part of the L2TOR project, which has received funding from the European Union’s Horizon 2020 research and innovation programme under the Grant Agreement No. 688014.

If you use this system in any way, please include a reference to the following paper:

@inproceedings{de2018effect,
  title={The Effect of a Robot's Gestures and Adaptive Tutoring on Children's Acquisition of Second Language Vocabularies},
  author={de Wit, Jan and Schodde, Thorsten and Willemsen, Bram and Bergmann, Kirsten and de Haas, Mirjam and Kopp, Stefan and Krahmer, Emiel and Vogt, Paul},
  booktitle={Proceedings of the 2018 ACM/IEEE International Conference on Human-Robot Interaction},
  pages={50--58},
  year={2018},
  organization={ACM}
}

# Instructions #
Note: The system only runs with actual NAO robots, unfortunately due to our use of qimessaging the Choregraphe simulator does not work.
There also appears to be a problem with newer versions of the NAOqi software (on the robot), where qimessaging has been removed. We're looking into this.

First, the two Choregraphe projects in the choregraphe_projects directory need to be installed on the NAO robot.

To run the system, use the following command:
start.py -i [robotip] -c [condition]

Replace [robotip] with the ip address of your NAO robot on the network, and [condition] should be one of the following:
1	-	random, no gestures
2	-	random, gestures
3	-	adaptive, no gestures
4	-	adaptive, gestures

In the random condition, all six concepts are presented five times randomly (30 rounds total), while in the adaptive condition the system uses Bayesian Knowledge Tracing (BKT) to track the knowledge state of each of the concepts, giving priority to concepts of which we are unsure whether the learner has succesfully acquired them. More information can be found in the paper linked below.

Finally, you can open controlpanel/index.html to start the experiment. If you want to run this control panel from a different machine than the companion tablet game and other modules, make sure to include robotip.js (in the root directory) so that it knows where to connect to.

# Project structure #
| animalexperimentservice | Output management (speech and gesture production) |
| interactionmanager | Interaction management (tracks progress through the experiment, decides what to do next) |
| controlpanel | Web interface used to start the experiment |
| tests | The pre and posttests used for the experiment (ran on a laptop) |

# Making changes #
In order to add your own concepts, the following steps are needed:
1. Update CSV files in interactionmanager/data/study_1/
2. Add English recordings of the concepts to choregraphe_projects/soundSet_Test/
3. If needed: add gestures of the concepts to choregraphe_projects/
4. Update the concepts at the top of the animalexperimentservice/app/scripts/myservice.py file

Note: because we did not know how to do language switches fast enough to make it sound fluent, we trigger .wav recordings in English while maintaining the Dutch language setting of the robot. We have since found a better way to do this, which you can find in the OutputManager of the large scale L2TOR study, but have not revised this project yet to implement this update.
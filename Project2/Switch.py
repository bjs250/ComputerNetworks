# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015
			    												

from Message import *
from StpSwitch import *

class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):    
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)
        
        # Use the data structure outlined by the video lecture
        self.root = self.switchID
        self.distance = 0
        self.active_links = list()
        self.switchthrough = self.switchID
        
        # Set debug flag for console output (should be set to False during grading)
        self.debugMode = False

        if self.debugMode == True:
            print("init",self.switchID, self.root, self.distance, self.active_links, self.switchthrough)


    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	    #      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)

        #
        for neighbor in self.links:
            if self.debugMode == True:
                print("send:", self.root, 0, self.switchID, neighbor,False)
            msg = Message(claimedRoot=self.root, distanceToRoot=0, originID=self.switchID, destinationID=neighbor, pathThrough=False)
            self.send_message(msg)
        return
        
    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        
        #if self.switchID == 2:
        #    print(message.origin, message.root, message.distance, self.distance)

        """
            If message has a lower root, it must be better. Update and broadcast to all neighbors
        """
        if message.root < self.root:
            self.root = message.root
            self.distance = message.distance + 1

            if self.switchthrough in self.active_links:
                self.active_links.remove(self.switchthrough)
                #print(self.switchID, self.switchthrough, "root: " + str(self.root), "dist: "  + str(self.distance))
                #msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=self.switchthrough, pathThrough=False)
                #self.send_message(msg)

            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            self.switchthrough = message.origin
            
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (root) from " + str(message.origin), "root: " + str(self.root), "dist: "  + str(self.distance), self.active_links, self.switchthrough)
            
            for neighbor in self.links:
                if neighbor == self.switchthrough:
                    paththru = True
                else:
                    paththru = False

                msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=neighbor, pathThrough=paththru)
                self.send_message(msg)
      
        """
            If you go through me (are farther away) I should add you
        """   
        if message.root == self.root and (message.distance+1) > self.distance and message.pathThrough == True:
            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (farther) from " + str(message.origin), "root: " + str(self.root), "dist: "  + str(self.distance), self.active_links, self.switchthrough)

        """
            If you have just as a good a path but lower number, tiebreaker
        """
        if message.root == self.root and (message.distance+1) == self.distance and message.origin < self.switchthrough:
            self.active_links.remove(self.switchthrough)
            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            old = self.switchthrough
            self.switchthrough = message.origin

            if self.debugMode == True:
                print("update " + str(self.switchID) + " (tiebreaker) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

            # need sender to add back
            msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=message.origin, pathThrough=True)
            self.send_message(msg)

            # need old switchthrough to remove
            msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=old, pathThrough=False)
            self.send_message(msg)

        """
            Special tiebreaker resolution
        """
        if message.root == self.root and (message.distance+1) > self.distance and (message.origin != self.switchthrough and message.pathThrough == False) and message.origin in self.active_links:
            self.active_links.remove(message.origin)
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (tiebreaker resolution) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

        """
            Weird condition
        """
        if message.root == self.root and (message.distance+1) == self.distance and (message.origin != self.switchthrough and message.pathThrough == False) and message.origin in self.active_links:
            self.active_links.remove(message.origin)
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (weird) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

            


        
    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.
        returnString = ""
        self.active_links =  sorted(self.active_links)
        if self.debugMode == True:
            print(self.switchID, self.active_links)
        for index,neighbor in enumerate(self.active_links):
            if index != (len(self.active_links)-1):
                returnString = returnString + str(self.switchID) + " - " + str(neighbor) + ", "
            else:
                returnString = returnString + str(self.switchID) + " - " + str(neighbor) 
        return returnString
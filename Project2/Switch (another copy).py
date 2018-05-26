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

    def send_initial_messages(self):
        
        # Broadcast messages to all neighbors
        for neighbor in self.links:
            msg = Message(claimedRoot=self.root, distanceToRoot=0, originID=self.switchID, destinationID=neighbor, pathThrough=False)
            self.send_message(msg)
        return
        
    def process_message(self, message):
        
        """
            If a received message has a lower root, it must be better. 
            Update root, distancce, active links, switchthru, and broadcast to all neighbors
        """
        if message.root < self.root:
            self.root = message.root
            self.distance = message.distance + 1

            # Remove the old switchthrough from activelinks
            if self.switchthrough in self.active_links:
                self.active_links.remove(self.switchthrough)
            
            # Add the new switchthrough to activelinks
            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            self.switchthrough = message.origin
            
            # Print update to console
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (root) from " + str(message.origin), "root: " + str(self.root), "dist: "  + str(self.distance), self.active_links, self.switchthrough)
            
            # Broadcast update to all neighbors
            for neighbor in self.links:
                if neighbor == self.switchthrough:
                    paththru = True
                else:
                    paththru = False

                msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=neighbor, pathThrough=paththru)
                self.send_message(msg)
      
        """
            If received message is farther away but goes through self, add as an active link
        """   
        if message.root == self.root and (message.distance+1) > self.distance and message.pathThrough == True:
            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            
            # Print update to console
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (farther) from " + str(message.origin), "root: " + str(self.root), "dist: "  + str(self.distance), self.active_links, self.switchthrough)

        """
            Tiebreaker condition: same root, same distance, but lower number, then resolve
        """
        if message.root == self.root and (message.distance+1) == self.distance and message.origin < self.switchthrough:
            # Remove old switchthrough from activelinks, update switchthrough to be message sender
            self.active_links.remove(self.switchthrough)
            if message.origin not in self.active_links:
                self.active_links.append(message.origin)
            old = self.switchthrough
            self.switchthrough = message.origin

            # Print update to console
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (tiebreaker) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

            # Reply to sender telling them to add to activelinks
            msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=message.origin, pathThrough=True)
            self.send_message(msg)

            # Send message to old switchthrough telling to remove from activelinks (see below)
            msg = Message(claimedRoot=self.root, distanceToRoot=self.distance, originID=self.switchID, destinationID=old, pathThrough=False)
            self.send_message(msg)

        """
            Tiebreaker resolution: this condition should only occur if the tiebreaker condition was tripped and switch needs to remove an activelink
        """
        if message.root == self.root and (message.distance+1) >= self.distance and (message.origin != self.switchthrough and message.pathThrough == False) and message.origin in self.active_links:
            self.active_links.remove(message.origin)
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (tiebreaker resolution) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

        """
            Corner condition: this is a rare occurence observed in Tailtopo and similar topologies where switch needs to remove an dead activelink (similar to tiebreaker resolution)
        """
        if message.root == self.root and (message.distance+1) == self.distance and (message.origin != self.switchthrough and message.pathThrough == False) and message.origin in self.active_links:
            self.active_links.remove(message.origin)
            if self.debugMode == True:
                print("update " + str(self.switchID) + " (corner) from " + str(message.origin), self.switchID, self.root, self.distance, self.active_links, self.switchthrough)

            


        
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
import unittest, sys, threading, thread
from MessageSender import MessageSender

class MessageSenderMain():
	message_sender = MessageSender()

	def send_messages(self):
		self.message_sender.sending_message(100,"NEW",1001, amount=10)
		self.message_sender.sending_message(100,"COOKING",1002)
		self.message_sender.sending_message(100,"DELIVERING.",1003)
		self.message_sender.sending_message(100,"DELIVERED",1004)
		self.message_sender.sending_end_message()


MessageSender = MessageSenderMain()
MessageSender.send_messages()
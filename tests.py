__author__ = 'romain_lavoix'
import unittest, sys, threading, thread, os
from MessageSender import MessageSender
from MessageListener import MessageListener
from MessageTracker import MessageTracker

class SummaryTest(unittest.TestCase):
	message_sender = MessageSender()
	message_listener = MessageListener()
	input = 'input'
	output = 'output'
	error = 'error'

	# simulates a summary output for testing comparaisons
	def compare_output(self, new=0, cooking=0, delivering=0, delivered=0, canceled=0, refunded=0, amount=0):
		stream_out_read = open(self.output).read()
		infos = ["New: %d" % new, "Cooking: %d" % cooking, "Delivering: %d" % delivering,\
				"Delivered: %d" % delivered, "Canceled: %d" % canceled, "Refunded: %d" % refunded,\
				"Total amount charged: %d" % amount]
		for info in infos:
			if not info in stream_out_read:
				return False
		return True

	# able to handle a reasonably large volume of orders
	def test_load_capacity(self):
		self.message_sender.sending_begin_message(self.input)
		for x in range (0, 10000):
			self.message_sender.sending_message(x,MessageTracker.new, x + 1 , amount=10)
			self.message_sender.sending_message(x,MessageTracker.cooking,x + 2)
			self.message_sender.sending_message(x,MessageTracker.delivering,x + 3)
			self.message_sender.sending_message(x,MessageTracker.delivered,x + 4)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		self.assertTrue(self.compare_output(0, 0, 0, 100, 0, 0, 100000))

	# test a bunch of possible invalid workflows
	def test_invalid_worflow(self):
		self.message_sender.sending_begin_message(self.input)
		self.message_sender.sending_message(100,MessageTracker.new,1001, amount=10)
		self.message_sender.sending_message(100,MessageTracker.delivering,1002)
		self.message_sender.sending_message(101,MessageTracker.cooking,1003, amount=10)
		self.message_sender.sending_message(102,MessageTracker.new,1004, amount=10)
		self.message_sender.sending_message(102,MessageTracker.cooking,1005, amount=10)
		self.message_sender.sending_message(102,MessageTracker.delivering,1006, amount=10)
		self.message_sender.sending_message(102,MessageTracker.refunded,1007, amount=10)
		self.message_sender.sending_message(103, MessageTracker.new, 1008, amount=20)
		self.message_sender.sending_message(103, MessageTracker.cooking, 1009, amount=20)
		self.message_sender.sending_message(103, MessageTracker.delivering, 1010, amount=20)
		self.message_sender.sending_message(103, MessageTracker.delivered, 1011, amount=20)
		self.message_sender.sending_message(103, MessageTracker.canceled, 1012, amount=30)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		error_stream = open(self.error)
		errors = error_stream.read()
		error1 = "100 can't go from NEW to DELIVERING" in errors
		error2 = "101 must start with NEW" in errors
		error3 = "can't go from DELIVERING to REFUNDED" in errors
		error4 = "can't go from DELIVERED to CANCELED" in errors
		error_stream.close()
		self.assertTrue(error1 and error2 and error3 and error4)

	# correct workflow including a manual refunding, to check the final amount charged
	def test_refunding(self):
		self.message_sender.sending_begin_message(self.input)
		self.message_sender.sending_message(100,MessageTracker.new,1001, amount=10)
		self.message_sender.sending_message(100,MessageTracker.cooking,1002)
		self.message_sender.sending_message(100,MessageTracker.delivering,1003)
		self.message_sender.sending_message(100,MessageTracker.delivered,1004)
		self.message_sender.sending_message(100,MessageTracker.refunded,1005)
		self.message_sender.sending_message(101,MessageTracker.new,1006, amount=25)
		self.message_sender.sending_message(101,MessageTracker.cooking,1007)
		self.message_sender.sending_message(101,MessageTracker.delivering,1008)
		self.message_sender.sending_message(101,MessageTracker.canceled,1010)
		self.message_sender.sending_message(102,MessageTracker.new,1006, amount=50)
		self.message_sender.sending_message(102,MessageTracker.cooking,1007)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		self.assertTrue(self.compare_output(0, 1, 0, 0, 1, 1, 50))

	# (Pete offers an aggressive ?300-day delivery or you eat free? promotion.)
	def test_automatic_refund(self):
		self.message_sender.sending_begin_message(self.input)
		self.message_sender.sending_message(100,MessageTracker.new,1001, amount=10)
		self.message_sender.sending_message(100,MessageTracker.cooking,1002)
		self.message_sender.sending_message(100,MessageTracker.delivering,1003)
		self.message_sender.sending_message(100,MessageTracker.delivered,1004, days=301)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		self.assertTrue(self.compare_output(0, 0, 0, 0, 0, 1, 0))

	# All valid orders will begin in the NEW state...
	def test_correct_worflow(self):
		self.message_sender.sending_begin_message(self.input)
		self.message_sender.sending_message(100,MessageTracker.new,1001, amount=10)
		self.message_sender.sending_message(100,MessageTracker.cooking,1002)
		self.message_sender.sending_message(100,MessageTracker.delivering,1003)
		self.message_sender.sending_message(100,MessageTracker.delivered,1004)
		self.message_sender.sending_message(101,MessageTracker.new,1005, amount=20)
		self.message_sender.sending_message(101,MessageTracker.cooking,1006)
		self.message_sender.sending_message(101,MessageTracker.delivering,1007)
		self.message_sender.sending_message(101,MessageTracker.delivered,1008)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		self.assertTrue(self.compare_output(0, 0, 0, 2, 0, 0, 30))

	# However, some customers have been complaining that Pete double- charged them for their pizza.
	def test_double_update(self):
		self.message_sender.sending_begin_message(self.input)
		self.message_sender.sending_message(100,MessageTracker.new,1001, amount=10)
		self.message_sender.sending_message(100,MessageTracker.cooking,1001)
		self.message_sender.sending_end_message()
		self.message_listener.listening(self.input, self.output, self.error)
		error_stream = open(self.error)
		self.assertTrue('double update' in error_stream.read())
		error_stream.close()

if __name__ == '__main__':
	unittest.main()
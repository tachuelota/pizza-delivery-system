__author__ = 'romain_lavoix'
import sys, json, os

class MessageSender:
	stream_in = None

	# send a single json message to the input stream
	# used primaly for unit testing
	def sending_message(self, orderId, status, updateId, *args, **kwargs):
		output_map = {
			"orderId": orderId,
			"status": status,
			"updateId": updateId
		}
		for name, value in kwargs.items():
			output_map[name] = value
		self.stream_in.write('%s\n' % json.dumps(output_map))

	# open the stream
	def sending_begin_message(self, input_name):
		self.stream_in = open(input_name, 'w')

	# close the stream in order to trigger the summary display
	def sending_end_message(self):
		self.stream_in.close()
__author__ = 'romain_lavoix'
import sys, fileinput
from MessageTracker import MessageTracker


class MessageListener:

	# if arguments are provided, we can simulate the listening of the input
	# messages in files. Otherwise stdin and stdout will be used.
	# to use in a console file you can pipe the output of a file to this script
	# or enter the messages manually and end the sequence with Ctrl+D
	def listening(self, input_name=None, output_name=None, error_name=None):
		messageTracker = MessageTracker()

		if input_name:
			stream_in = open(input_name, 'r')
		else:
			stream_in = sys.stdin
		if output_name:
			stream_out = open(output_name, 'w')
		else:
			stream_out = sys.stdout
		if error_name:
			stream_error = open(error_name, 'w')
		else:
			stream_error = sys.stderr

		for json_message in stream_in:
			messageTracker.track(json_message, stream_error)
		messageTracker.print_summary(stream_out)
		stream_out.close()
		stream_in.close()
		stream_error.close()

if __name__ == '__main__':
	message_listener = MessageListener()
	message_listener.listening()
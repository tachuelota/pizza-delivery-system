__author__ = 'romain_lavoix'

import sys, json, collections
from collections import defaultdict

# handles sequential json messages and store necessary informations
class MessageTracker:

	message = None
	order_updates = None
	invalid_messages = None
	order_infos = None

	new = "NEW"
	cooking = "COOKING"
	delivering = "DELIVERING"
	delivered = "DELIVERED"
	canceled = "CANCELED"
	refunded = "REFUNDED"
	status = "status"
	order_id = "orderId"
	update_id = "updateId"
	amount = "amount"
	days = "days"
	total_amount_charged = "Total amount charged"

	def __init__(self):
		self.order_updates = defaultdict(list)
		self.invalid_messages = 0
		self.order_infos = defaultdict(defaultdict)
		self.message = None

	# Verify if the message is correctly formated
	def check_valid_message(self, message, error_stream_name):
		try:
			self.message = json.loads(message)
		except ValueError:
			self.log_error(error_stream_name, "malformed message")
			return False
		return True

	# We don't want to have two times the same update
	def check_double_updates(self, updateId, orderId, error_stream_name):
		if updateId in self.order_updates[orderId]:
			self.log_error(error_stream_name, "double update on orderId:%d\n" % orderId)
			return False
		self.order_updates[orderId].append(updateId)
		return True

	# verify the validity of the business rules
	def check_workflow(self, message, order_id, error_stream):
		order_infos = self.order_infos[order_id]
		if not self.status in order_infos and message[self.status] == self.new:
			return True
		if not self.status in order_infos and message[self.status] != self.new:
			self.log_error(error_stream, "%d must start with NEW" % message[self.order_id])
			return False
		previous_status = order_infos[self.status]
		new_status = message[self.status]
		if (previous_status in self.new and not new_status in (self.cooking, self.canceled)) or \
			(previous_status in self.cooking and not new_status in(self.delivering, self.canceled)) or \
			(previous_status in self.delivering and not new_status in (self.delivered, self.canceled)) or \
			(previous_status in self.delivered and not new_status in self.refunded):
			self.log_error(error_stream, "%d can't go from %s to %s" % (message[self.order_id],previous_status, new_status))
			return False
		return True

	# prints a message in the error log for later verification
	def log_error(self, error_stream, error_msg):
		error_stream.write("%s\n" % error_msg)
		self.invalid_messages += 1

	# listen to a new message, and store the informations
	def track(self, json_message, error_stream):
		if not self.check_valid_message(json_message, error_stream):
			return

		order_id = self.message[self.order_id]
		update_id = self.message[self.update_id]
		status = self.message[self.status]

		if not self.check_double_updates(update_id, order_id, error_stream):
			return

		if not self.check_workflow(self.message, order_id, error_stream):
			return

		order_infos = self.order_infos[order_id]
		order_infos[self.status] = status
		if status in (self.refunded, self.canceled):
			order_infos[self.amount] = 0
		if self.amount in self.message:
			order_infos[self.amount] = self.message[self.amount]
		if self.days in self.message and self.message[self.days] > 300:
			order_infos[self.amount] = 0
			order_infos[self.status] = self.refunded

	# prints the summary of all operations after the end of a message sequence
	def print_summary(self, fd):
		summary = {
			self.new.capitalize():0,
			self.cooking.capitalize():0,
			self.delivering.capitalize():0,
			self.delivered.capitalize():0,
			self.canceled.capitalize():0,
			self.refunded.capitalize():0,
			self.total_amount_charged:0
		}
		for orderId, infos in self.order_infos.iteritems():
			if self.status in infos :
				status = infos[self.status]
				summary[status.capitalize()] += 1
			if self.amount in infos and not status in (self.new, self.refunded, self.canceled):
				summary[self.total_amount_charged] += infos[self.amount]
		for k, v in summary.iteritems():
			fd.write('%s: %d\n' % (k,v))
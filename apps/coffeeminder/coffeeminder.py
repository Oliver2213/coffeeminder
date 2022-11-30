# Coffeeminder - don't leave that coffee on too long!
# Author: Blake Oliver <oliver22213@me.com>

# Arguments:
# coffee_switch: the all important switch that controls your coffeemaker.
# coffee_minutes: how many minutes should we leave the coffee on?
	# Coffeeminder will check homeassistant for an input number called coffeeminder_minutes; if found, it's value will be used instead of the above argument.
	# this is meant for faster changes via hass's UI - stick that input whatsit on a twittly dashboard somewhere, automate it, whatever.
# notify_targets: optional comma-separated list of notify entities to send a message to when cofffeeminder turns off the coffee.

from hassapi import Hass
from datetime import timedelta

class Coffeeminder(Hass):
	def initialize(self):
		self.minder = None
		self.started_minding = None
		if self.args.get('notify_targets') is not None:
			self.notify_targets = self.split_device_list(self.args['notify_targets'])
		else:
			self.notify_targets = []
		ha_coffee_minutes = self.get_entity('input_number.coffeeminder_minutes')
		if ha_coffee_minutes:
			self.args['coffee_minutes'] = int(float(ha_coffee_minutes.state))
			self.log("Coffeeminder set to shut off after {} minutes by homeassistant.".format(self.args['coffee_minutes']))
			self.listen_state(self.coffee_minutes_changed, 'input_number.coffeeminder_minutes')
		else:
			self.log("Coffeeminder set to shut off after {} minutes by config.".format(self.args['coffee_minutes']))
		# The state listen call here has immediate set to true so that when the app is started,
		# if it's conditions are met it will properly set the timer, rather than waiting for coffeemaker toggle.
		self.listen_state(self.coffeemaker_toggled, self.args['coffee_switch'], immediate=True)
		self.delay_seconds = timedelta(minutes=self.args['coffee_minutes']).total_seconds()

	def terminate(self):
		# Unregister our minder timer.
		if self.minder and self.timer_running(self.minder):
			self.cancel_timer(self.minder)
		self.minder = None
		self.started_minding = None
		self.delay_seconds = timedelta(minutes=self.args['coffee_minutes']).total_seconds()

	def coffeemaker_toggled(self, entity, attribute, old, new, kwargs):
		if new == 'off' and old == 'on':
			self.log("Coffeemaker turned off; canceling minder.")
			self.terminate()
		elif new == 'on':
			self.log("Coffeeminder is active. Shut-off in {} minutes.".format(self.args['coffee_minutes']))
			self.started_minding = self.datetime()
			self.minder = self.run_in(self.coffeeminder, self.delay_seconds)


	def coffeeminder(self, kwargs):
		status = self.get_state(self.args['coffee_switch'])
		if status == 'on': # If it's still on.
			self.terminate() # kill timer.
			self.turn_off(self.args['coffee_switch'])
			self.log("Coffeeminder turned off your coffeemaker.")
			for t in self.notify_targets:
				self.notify("Your coffeemaker was shut off by coffeeminder.", name=t)

	def coffee_minutes_changed(self, entity, attribute, old, new, kwargs):
		# reschedule the turn-off timer, deducting or adding time based on how the value changed.
		if self.minder == None:
			return # we don't need to reschedule, we aren't minding.
		old = int(float(old))
		new = int(float(new))
		elapsed = self.datetime() - self.started_minding
		remaining = timedelta(minutes=new) - elapsed
		self.log("Started: {started}; elapsed: {elapsed}; remaining: {remaining}".format(started=self.started_minding, elapsed=elapsed.total_seconds(), remaining = remaining.total_seconds()))
		self.args['coffee_minutes'] = new
		#self.delay_seconds = timedelta(minutes=self.args['coffee_minutes']).total_seconds()
		self.delay_seconds = remaining.total_seconds()
		if remaining.total_seconds() > 0:
			self.log("Rescheduling.")
			self.cancel_timer(self.minder)
			self.minder = self.run_in(self.coffeeminder, self.delay_seconds)
			#self.started_minding = self.datetime()
		else: # Coffee minutes changed to a shorter time that has already elapsed; turn off the coffeemaker
			self.turn_off('switch.coffee_maker_on_off')
			self.log("Coffeeminder minutes change has caused coffeemaker to be turned off")
			for t in self.notify_targets:
				self.notify("Your coffeemaker was shut off by coffeeminder.", name=t)



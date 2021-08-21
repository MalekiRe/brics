""" 
Stanford Student Space Initiative
Written by: Leo Glikbarg 

This file contains the Runner class. Runner contains all the logic and methods for performing the
test procedures. The Payload class is used to interact with the hardware.
"""

from payload_controller import Payload

# default timing constants and hardware configuration
DEFAULT_SENSOR_SPEED = 1 # hz
DEFAULT_START_WAIT = 3600 # s (1 hour)
DEFAULT_END_WAIT = 3600 * 120 # s (120 hours)
DEFAULT_SHORT_GAP = 10 # s
DEFAULT_LONG_GAP = 3600 * 48 # s (48 hours)
DEFAULT_VALVE_QUANTITY = 3 # valves
DEFAULT_VALVE_PORTS = [4, 17, 27, 22, 10, 9] # GPIO hardware port numbers


class Runner:
    def __init__(self, sense_rep=DEFAULT_SENSOR_SPEED, test_start=DEFAULT_START_WAIT, test_end=DEFAULT_END_WAIT, intra=DEFAULT_SHORT_GAP, inter=DEFAULT_LONG_GAP, valve_quantity=DEFAULT_VALVE_QUANTITY, ports=DEFAULT_VALVE_PORTS):
        """configure with default or user specified timing and hardware configuration"""
        self.sense_report_time = sense_rep
        self.test_start_time = test_start
        self.test_end_time = test_end
        self.intra_valve_time = intra
        self.inter_valve_time = inter
        self.valve_num = valve_quantity
        self.payload = Payload(sense_rep, list(ports))
        self.active = False
        self.valves_configured = False
        self.current_step = "initialized"
        self.payload.status.info(("payload initialized, sensors reporting at {speed}hz").format(speed=self.sense_report_time))


    def change_timing(self, timing):
        """Chanmge the timing once the Payload has been initialized"""
        self.test_start_time = timing[0]
        self.test_end_time = timing[1]
        self.intra_valve_time = timing[2]
        self.inter_valve_time = timing[3]
        self.payload.status(("New Timing-- test_start_time:{time_0}, test_end_time:{time_1}, intra_valve_time:{time_2}, inter_valve_time:{time_3}").format(time_0=timing[0], time_1=timing[1], time_2=timing[2], time_3=timing[3]))


    def get_current_step(self):
        """outputs the current stap and status information of the paylod"""
        self.payload.status.info(("STATUS: servos_active:{running}, sensors_active:{sense}, current_step:{step}").format(running=str(self.active), sense=str(self.payload.active), step=self.current_step))


    def get_sensor_data(self):
        """reports current humidity and temperature values"""
        self.payload.get_humidity()
        self.payload.get_temperature()


    def update_step(self, state):
        """changes the current state and outputs the new state"""
        self.current_step = state
        self.payload.status.info(state)


    def cleanup(self):
        """deconfigures the gpio connections and sensor logging"""
        self.active = False
        self.payload.cleanup_gpio()
        self.valves_configured = False
        self.end_sensor_logging()
        self.update_step("")


    def end_sensor_logging(self):
        """ends the sensor logging thread"""
        self.payload.active = False
        self.payload.sense_thread.join()


    def start_testing(self, start_wait=True, end_wait=True, cleanup=True, first_valve=1, last_valve=3):
        """periodically actuate servos to open/close valves and log sensor data"""
        self.active = True
        self.current_step = "starting testing"
        self.payload.status.info(("starting testing with {valve}").format(valve=first_valve))
        try:
            # configure servos if they are not already
            if not self.valves_configured:
                self.update_step("configuring servos")
                self.payload.configure_servos(self.valve_num)
                self.valves_configured = True
                self.payload.status.info("servos configured")
            # wait to start servo movement
            if start_wait:
                self.update_step(("waiting {start_wait} minutes before beginning first valve movement").format(start_wait=float(self.test_start_time)/60.0))
                self.payload.secure_sleep(self.test_start_time)
            # open valves
            for pair_num in range(1, self.valve_num + 1):
                # open valve a
                self.payload.open_valve(("{num}a").format(num=pair_num))
                self.payload.secure_sleep(self.intra_valve_time)
                self.update_step(("just opened valve {num}a, waiting {gap_time}s before moving on").format(num=pair_num, gap_time=self.intra_valve_time))
                # open valve b
                self.payload.open_valve(("{num}b").format(num=pair_num))
                self.payload.secure_sleep(self.inter_valve_time)
                self.update_step(("just opened valve {num}b, waiting {gap_time} hours before moving on").format(num=pair_num, gap_time=float(self.inter_valve_time)/3600.0))
            # wait to finish if necessary, will end sensor logging
            if end_wait:
                self.update_step(("active testing done, data logging will continue for {end_time}hours").format(end_time=float(self.test_end_time)/3600.0))
                self.payload.secure_sleep(self.test_end_time)
            if cleanup:
                self.cleanup()
        # cleanup
        except Exception and KeyboardInterrupt as e:
            self.payload.status.info(("ERROR: stopped early -- {err}").format(err=e))

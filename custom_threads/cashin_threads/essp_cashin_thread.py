from threading import Thread, Event
import eSSP

class CashInThreadEssp(Thread):

    def __init__(self, callback_message, config):
        super().__init__()
        self.daemon = True
        self._stop_cashin = Event()
        self._callback_message = callback_message
        self._validator_port = config.VALIDATOR_PORT

    def run(self):
        """Run Worker Thread."""
        #  Create a new object ( Validator Object ) and initialize it
        validator = eSSP(com_port=self._config.VALIDATOR_PORT, ssp_address="0", nv11=False)

        while not self.stop_cashin.is_set():

            # ---- Example of interaction with events ---- #
            if validator.nv11: # If the model is an NV11, put every 100 note in the storage, and others in the stack(cashbox), but that's just for this example
                (note, currency,event) = validator.get_last_event()
                if note == 0 or currency == 0 or event == 0:
                    pass  # Operation that do not send money info, we don't do anything with it
                else:
                    if note != 4 and event == Status.SSP_POLL_CREDIT:
                        validator.nv11_stack_next_note()
                        validator.enable_validator()
                    elif note == 4 and event == Status.SSP_POLL_READ:
                        validator.set_route_storage(100)  # Route to storage
                        validator.do_actions()
                        validator.set_route_cashbox(50)  # Everything under or equal to 50 to cashbox ( NV11 )
            time.sleep(0.5)
            # TODO: somehow use the _callback_message to notify the UI

    def stop_cashin(self):
        self._stop_cashin.set()

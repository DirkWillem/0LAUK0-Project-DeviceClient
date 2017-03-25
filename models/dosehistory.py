from kivy.graphics import Color


class DoseStatus(object):
    """Contains the historical status on a dose on the current date"""

    def __init__(self, title, description, dispensed, pending, being_dispensed, dispensed_time):
        self.title = title
        self.description = description
        self.dispensed = dispensed
        self.pending = pending
        self.being_dispensed = being_dispensed
        self.dispensed_time = dispensed_time

    def get_color(self):
        if self.dispensed:
            return 0, 1, 0, 1
        elif self.pending or self.being_dispensed:
            return 0.5, 0.5, 1, 1
        else:
            return 1, 0, 0, 1

    def status_text(self):
        if self.dispensed:
            return 'Dispensed'
        elif self.being_dispensed:
            return 'Being dispensed'
        elif self.pending:
            return 'To be dispensed'
        else:
            return 'Not dispensed'

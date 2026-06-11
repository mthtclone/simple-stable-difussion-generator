class GenerationController:
    def __init__(self):
        self.cancel_requested = False
    
    def cancel(self):
        self.cancel_requested = True

    def reset(self):
        self.cancel_requested = False

    def is_cancelled(self):
        return self.cancel_requested
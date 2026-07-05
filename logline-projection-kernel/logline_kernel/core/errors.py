"""Kernel error types."""

class LogLineError(Exception):
    pass

class AdmissionError(LogLineError):
    def __init__(self, problems):
        self.problems = problems
        super().__init__(str(problems))

class RegistrationError(LogLineError):
    def __init__(self, problems):
        self.problems = problems
        super().__init__(str(problems))

class ProjectionError(LogLineError):
    pass

class SealingError(LogLineError):
    pass

class AccessDeniedError(LogLineError):
    pass

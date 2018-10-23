class Log(object):

    class BGColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def __init__(self):
        self.bgcolors = self.BGColors()
        self.color = self.bgcolors.BOLD

    def info(self, msg):
        self.color = self.bgcolors.BOLD
        self._output(msg)

    def warn(self, msg):
        self.color = self.bgcolors.WARNING
        self._output(msg)

    def debug(self, msg):
        self.color = self.bgcolors.OKBLUE
        self._output(msg)

    def _output(self, msg):
        print('{}{}{}'.format(self.color, msg, self.bgcolors.ENDC))

import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import QThread


class AcesSubprocessThread(QThread):

    # Signals
    notify_job_successful = QtCore.pyqtSignal(str, name='notifyJobSuccessful')

    def __init__(self):
        super(QThread, self).__init__()
        self.__job_id = None
        self.__cmd = None
        self.__wrk_dir = None
        self.__std_out_path = None
        self.__std_in_str = None

    def set_run_context(self, job_id, cmd, wrk_dir, std_out_path, std_in_str=None):
        self.__job_id = job_id
        self.__cmd = cmd
        self.__wrk_dir = wrk_dir
        self.__std_out_path = std_out_path
        self.__std_in_str = std_in_str

    def del_run_context(self):
        self.__job_id = None
        self.__cmd = None
        self.__wrk_dir = None
        self.__std_out_path = None
        self.__std_in_str = None

    def run(self):
        # Create process and call command
        sout = open(self.__std_out_path, 'wt')
        inp = None
        if self.__std_in_str:
            inp = bytes(self.__std_in_str, 'utf-8')
        prcs = subprocess.run(self.__cmd, input=inp, stdout=sout, stderr=sout, timeout=60 * 10, shell=True, cwd=self.__wrk_dir)
        sout.close()
        self.notify_job_successful.emit(self.__job_id)
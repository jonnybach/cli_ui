import abc
import logging
import os
import uuid


class CuiAutomatedProcess:

    def __init__(self, tool_core=None, resource_path=None):
        self._tool_core = tool_core
        self._rscr_path = resource_path

        # Initialize job folder
        self._job_id = str(uuid.uuid4())
        inp_port_key = list(tool_core.inputs.keys())[0]
        wrk_dir = os.path.split(tool_core.inputs[inp_port_key][0].working_directory)[0]
        self._jobs_path = os.path.join(wrk_dir, "jobs")
        os.mkdir(self._jobs_path)

        self._input_data = {}
        self._output_data = {}
        self.__pre_callbacks = []
        self.__post_callbacks = []

    @property
    def input_data(self):
        return self._input_data

    @property
    def output_data(self):
        return self._output_data

    def set_pre_callbacks(self, callbacks: []):
        """
        Callbacks will be executed in the order provided in the list
        :param callbacks: 
        :return: 
        """
        self.__pre_callbacks = callbacks

    def set_post_callbacks(self, callbacks: []):
        """
        Callbacks will be executed in the order provided in the list
        :param callbacks: 
        :return: 
        """
        self.__post_callbacks = callbacks

    @abc.abstractmethod
    def _parse_input_data(self):
        """
        Implement this method to process all files coming from the activity block input ports.
        Two tasks should be performed within this method:
        1. Copy any files that can be either directly used by the analysis tool or that serve as 
           templates where substitution of read only data from other input parameters will first occur
           prior to using in the analysis.  This include model files and other files required for execution.
        2. Read in a json formatted results from other upstream activity blocks or prior design revisions and store
           the parameters in the self._input_data dictionary for use in other methods.  It is strongly recommended to use
           the harmonized nomenclature (where applicable).
        :return: nothing
        """

    def _preprocess(self, *args):
        """
        Implement this method to perform any pre-processing on the input data contained in the self._input_data
        dictionary to be finally provided to the analysis tool.  This includes making any changes to the input 
        data or calculating derived quantities that the analysis needs but isn't directly provided as input.
        :return: nothing
        """
        for c in self.__pre_callbacks:
            c(args)

    @abc.abstractmethod
    def _create_execution_input(self):
        """
        Implement this method to create the final input in the format required by the analysis.
        For instance create the necessary inputs files from the set of input data by performing keyword
        substitution into the models using the parameters in the self._input_data dictionary
        :return: 
        """

    @abc.abstractmethod
    def _execute(self):
        """
        Perform the actual call to the underlying executable and handle return codes or other error
        notifications
        :return: 
        """

    @abc.abstractmethod
    def _parse_execution_output(self):
        """
        Implement this method for parsing the results file generated from the analysis tool and compiling
        the data into the self._output_data dictionary.  It is strongly recommended to use
        the harmonized nomenclature (where applicable).
        :return: 
        """

    def _postprocess(self, *args):
        """
        Implement this method to perform any additional post processing required on the in  memory
        persisted data set in order to create a final set of fully conditioned data.
        :return: 
        """
        for c in self.__pre_callbacks:
            c(args)

    @abc.abstractmethod
    def _create_output_data(self):
        """
        Implement this method to transfer the in memory and post-processed data into the required
        output datasets.
        :return: 
        """

    def run_job(self):
        logging.debug('Parsing input data ...')
        self._parse_input_data()
        logging.debug('Preprocessing data ...')
        self._preprocess()
        logging.debug('Creating execution input ...')
        self._create_execution_input()
        logging.debug('Executing ...')
        self._execute()
        logging.debug('Parsing execution output ...')
        self._parse_execution_output()
        logging.debug('Postprocessing data ...')
        self._postprocess()
        logging.debug('Creating output data ...')
        self._create_output_data()

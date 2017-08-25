import os
import copy
import uuid
import shutil
import logging


class Job:
    """
    my doc string
    """

    JOB_STATUS_NEW = 'NEW'
    JOB_STATUS_MOD = 'MODIFIED'
    JOB_STATUS_RUN = 'RUNNING'
    JOB_STATUS_CPLT = 'COMPLETE'
    JOB_STATUS_ERR = 'ERROR'
    JOB_STATUSES = {JOB_STATUS_NEW, JOB_STATUS_MOD, JOB_STATUS_RUN, JOB_STATUS_CPLT, JOB_STATUS_ERR}

    def __init__(self, job_root, new_id=None):

        if not new_id:
            self.__uuid = new_id if new_id else str(uuid.uuid4())
        else:
            self.__uuid = new_id

        self.__status = self.JOB_STATUS_NEW
        self.__path = os.path.join(job_root, self.__uuid)
        self.__data = JobData()  # Dictionary containing any required job data

    @property
    def id(self):
        return self.__uuid

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        if new_status not in self.JOB_STATUSES:
            raise ValueError('Invalid status string when attempting to set job status')
        else:
            self.__status = new_status

    @property
    def path(self):
        return self.__path

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, new_data):
        self.__data = new_data

    def copy_data(self, job):
        self.__data = copy.deepcopy(job.data)


class JobData:

    def __init__(self, inputs=None, outputs=None, custom=None):
        self.__inputs = inputs  # Key value pairs of input data
        self.__outputs = outputs  # Key value pairs of output data
        self.__custom = custom  # Key value pairs of any type of data

    @property
    def inputs(self):
        return self.__inputs

    @property
    def outputs(self):
        return self.__outputs

    @property
    def custom(self):
        return self.__custom

    def add_input(self, input_key, input_value):
        if self.__inputs:
            self.__inputs[input_key] = input_value
        else:
            self.__inputs = {input_key: input_value}

    def get_input_data(self, key):
        if key in self.__inputs:
            return self.__inputs[key]
        else:
            return None

    def add_output(self, output_key, output_value):
        if self.__inputs:
            self.__inputs[output_key] = output_value
        else:
            self.__inputs = {output_key: output_value}

    def get_output_data(self, key):
        if key in self.__outputs:
            return self.__outputs[key]
        else:
            return None

    def add_custom(self, key, value):
        if self.__custom:
            self.__custom[key] = value
        else:
            self.__custom = {key: value}

    def get_custom_data(self, key):
        if key in self.__custom:
            return self.__custom[key]
        else:
            return None

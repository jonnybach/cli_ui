import os
import copy
import uuid
import shutil
import logging


class JobManager:
    """
    my doc string
    """

    JOB_STATUS_NEW = 'NEW'
    JOB_STATUS_MOD = 'MODIFIED'
    JOB_STATUS_RUN = 'RUNNING'
    JOB_STATUS_CPLT = 'COMPLETE'
    JOB_STATUS_ERR = 'ERROR'

    def __init__(self, jobs_root):
        self.__jobs = {}  # Dictionary of analysis jobs by uuid
        self.jobs_root = jobs_root

    @property
    def jobs_root(self):
        return self.__jobs_root

    @jobs_root.setter
    def jobs_root(self, jobs_root):
        self.__jobs_root = jobs_root

    def count(self):
        return len(self.__jobs)

    def create_job(self, job_id=None, job_status=JOB_STATUS_NEW, job_data=None):
        """
        :param job_id:
        :param job_status:
        :param job_data: dictionary containing any additional properties to be stored with the job
        :return: tuple containing the job id and job path
        """
        if not job_id:
            job_id = str(uuid.uuid4())

        # Create the job path
        job_path = os.path.join(self.jobs_root, job_id)
        try:
            os.makedirs(job_path)
        except FileExistsError as e:
            logging.exception('Job path already exists when attempting to create a job.  Will remove old job and retry.')
            shutil.rmtree(job_path)
            os.makedirs(job_path)

        new_job = {
            'uuid': job_id,
            'path': job_path,
            'status': job_status,
        }
        if not job_data:
            new_job['data'] = {}
        new_job['data'] = job_data
        self.__jobs[job_id] = new_job
        return job_id, job_path

    def clone_job(self, job_id):
        """

        :param job_id:
        :return: tuple containing the newly cloned job id and job path
        """
        old_job_data = copy.deepcopy(self.get_job_data(job_id))
        new_job_id, new_job_path = self.create_job(job_data=old_job_data)
        self.update_job(new_job_id, job_status=self.get_job_status(job_id))
        return new_job_id, new_job_path

    def update_job(self, job_id, job_status, job_data=None):
        """
        :param job_id:
        :param job_status:
        :param job_data:
        :return:
        """
        if job_status != self.JOB_STATUS_NEW \
                and job_status != self.JOB_STATUS_RUN \
                and job_status != self.JOB_STATUS_MOD \
                and job_status != self.JOB_STATUS_CPLT \
                and job_status != self.JOB_STATUS_ERR:
            raise Exception('Invalid status value when trying to update job properties')
        else:
            self.__jobs[job_id]['status'] = job_status

        if job_data:
            self.__jobs[job_id]['data'] = job_data

    def delete_job(self, job_id):
        # TODO: what if job is still running?  Maybe use lck file, if exists, no delete?
        del_job = self.__jobs[job_id]
        del_path = del_job['path']
        shutil.rmtree(del_path)
        self.__jobs.pop(job_id)

    def delete_all_jobs(self):
        keys = list(self.__jobs.keys())
        for jid in keys:
            self.delete_job(jid)

    def has_job_id(self, job_id):
        return job_id in self.__jobs

    def get_job_path(self, job_id):
        return self.__jobs[job_id]['path']

    def get_job_status(self, job_id):
        return self.__jobs[job_id]['status']

    def set_job_status(self, job_id, status):
        self.__jobs[job_id]['status'] = status

    def get_job_data(self, job_id):
        return self.__jobs[job_id]['data']

    def set_job_data(self, job_id, new_data):
        self.__jobs[job_id]['data'] = new_data

    def _get_job(self, job_id):
        return self.__jobs[job_id]

    def _get_job_with_path(self, job_path):
        for k, v in self.__jobs.items():
            if job_path == v:
                return self.__jobs[k]
        return None

    def _get_job_data_for_table(self, job_id):

        kept = ''
        if job_id == self._get_kept_job_id():
            kept = self.KEEP_STR

        tbl_data = [
            self.__jobs[job_id]['uuid'],
            self.__jobs[job_id]['data']['model']['id'],
            self.__jobs[job_id]['status'],
            kept
        ]
        return tbl_data

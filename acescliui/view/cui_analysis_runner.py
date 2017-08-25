import os
import abc

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from ..model.table_model import TableModel
from ..core.job_manager import JobManager


class CuiAnalysisRunner(QtWidgets.QMainWindow):
    """
    my doc string
    """

    # Column numbers corresponding to the data types in each job table column
    CLM_ID = 0
    CLM_MDL_ID = 1
    CLM_STATUS = 2
    CLM_KEEP = 3

    KEEP_STR = 'KEEP'

    prj_path = os.path.join(os.path.split(__file__)[0])+"/.."

    def __init__(self, jobs_root=None, parent=None, window_title='Aces Model Editor'):
        super(CuiAnalysisRunner, self).__init__(parent)
        self._job_mgr = JobManager(jobs_root)
        self._text_eds = []  # List of text editors that are hosted by the tab widget
        self._active_ed_indx = -1  # Tracks the tab index of the currently active text editor
        self._active_job_id = None
        self._kept_job_id = None
        self._init_ui()

        # Set main window title
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate('CuiAnalysisRunner', window_title))  # Could call the method in retranslate UI but this will handle the case when I decide to use ui files later.

    # ---------------------------------
    # UI Setup
    # ---------------------------------

    def _init_jobs_table(self):
        hdrs = ['Analysis Id', 'Model Id', 'Status', 'Keep']
        data = []
        self._jobs_table_model = TableModel(data, hdrs)
        self.tableJobs.setModel(self._jobs_table_model)
        self.tableJobs.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table_jobs_select_model = self.tableJobs.selectionModel()
        self._table_jobs_select_model.selectionChanged.connect(self._change_selected_job)

    def _init_text_edit_tabs(self, text_editors, tab_titles):

        if len(text_editors) != len(tab_titles):
            raise Exception('Length of text_editors and tab_titles lists are not equal')

        _translate = QtCore.QCoreApplication.translate

        for i in range(len(text_editors)):
            newTabWig = QtWidgets.QWidget()
            newTabWig.setObjectName('tabTextEdit{0:d}'.format(i))
            text_editors[i].setParent(newTabWig)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(newTabWig.sizePolicy().hasHeightForWidth())
            newTabWig.setSizePolicy(sizePolicy)
            newTabLay = QtWidgets.QVBoxLayout()
            newTabLay.addWidget(text_editors[i])
            newTabWig.setLayout(newTabLay)
            self._text_eds.append(text_editors[i])
            self.tabFiles.addTab(newTabWig, _translate('CuiAnalysisRunner', tab_titles[i]))

        self.tabFiles.setCurrentIndex(0)

    def _init_menu_bar(self):

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 953, 25))
        self.menubar.setObjectName('menuBar')
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName('menuFile')
        self.setMenuBar(self.menubar)

        self.actionOpen = QtWidgets.QAction(self)
        self.actionOpen.setObjectName('actionOpen')
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionOpen.triggered.connect(self._open_file)

        # self.actionSave = QtWidgets.QAction(self)
        # self.actionSave.setObjectName("actionSave")
        # self.actionSave.setShortcut("Ctrl+S")
        # self.actionSave.triggered.connect(self._keep_analysis)

        self.actionExit = QtWidgets.QAction(self)
        self.actionExit.setObjectName('actionExit')
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.triggered.connect(self._exit)

        # Add menu bar actions
        self.menuFile.addAction(self.actionOpen)
        # self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

    def _init_toolbar(self):

        self.openAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/open.png'), 'Open Model (Ctrl+O)', self)
        self.openAction.setStatusTip('Delete and copy text to clipboard')
        #self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self._open_file)

        # self.saveAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/save.png'), 'Keep the analysis', self)
        # self.saveAction.setStatusTip("Copy text to clipboard")
        # #self.saveAction.setShortcut("Ctrl+S")
        # self.saveAction.triggered.connect(self._keep_analysis)

        self.cutAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/cut.png'), 'Cut (Ctrl+X)', self)
        self.cutAction.setStatusTip('Delete and copy text to clipboard')
        self.cutAction.setShortcut('Ctrl+X')
        self.cutAction.triggered.connect(self._cut)

        self.copyAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/copy.png'), 'Copy (Ctrl+C)', self)
        self.copyAction.setStatusTip('Copy text to clipboard')
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.triggered.connect(self._copy)

        self.pasteAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/paste.png'), 'Paste (Ctrl+V)', self)
        self.pasteAction.setStatusTip('Paste text from clipboard')
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.triggered.connect(self._paste)

        self.undoAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/undo.png'), 'Undo (Ctrl+Z)', self)
        self.undoAction.setStatusTip('Undo last action')
        self.undoAction.setShortcut('Ctrl+Z')
        self.undoAction.triggered.connect(self._undo)

        self.redoAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/redo.png'), 'Redo (Ctrl+Y)', self)
        self.redoAction.setStatusTip('Redo last undone thing')
        self.redoAction.setShortcut('Ctrl+Y')
        self.redoAction.triggered.connect(self._redo)

        self.toolbar = self.addToolBar('Options')
        self.toolbar.addAction(self.openAction)
        # self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.pasteAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

    def _init_ui(self):

        self.setObjectName("CuiAnalysisRunner")
        self.resize(953, 809)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        # Top horizontal layout
        self.horizontalLayoutTop = QtWidgets.QGridLayout()
        self.horizontalLayoutTop.setObjectName("horizontalLayoutTop")

        # Run job button
        self.btnRunJob = QtWidgets.QPushButton()
        self.btnRunJob.setMinimumSize(QtCore.QSize(200, 0))
        self.btnRunJob.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
        self.btnRunJob.setObjectName("btnRunJob")
        self.btnRunJob.clicked.connect(self._run_selected_job)
        self.horizontalLayoutTop.addWidget(self.btnRunJob, 1, 1, alignment=QtCore.Qt.AlignCenter)

        # Keep job button
        self.btnKeepJob = QtWidgets.QPushButton()
        self.btnKeepJob.setMinimumSize(QtCore.QSize(200, 0))
        self.btnKeepJob.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
        self.btnKeepJob.setObjectName("btnKeepJob")
        self.btnKeepJob.clicked.connect(self._keep_selected_job)
        self.horizontalLayoutTop.addWidget(self.btnKeepJob, 1, 3, alignment=QtCore.Qt.AlignCenter)

        # Clone job button
        self.btnCloneJob = QtWidgets.QPushButton()
        self.btnCloneJob.setMinimumSize(QtCore.QSize(200, 0))
        self.btnCloneJob.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
        self.btnCloneJob.setObjectName("btnCloneJob")
        self.btnCloneJob.clicked.connect(self._clone_selected_job)
        self.horizontalLayoutTop.addWidget(self.btnCloneJob, 2, 1, alignment=QtCore.Qt.AlignCenter)

        # Remove job button
        self.btnRmvJob = QtWidgets.QPushButton()
        self.btnRmvJob.setMinimumSize(QtCore.QSize(200, 0))
        self.btnRmvJob.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
        self.btnRmvJob.setObjectName("btnRmvJob")
        self.btnRmvJob.clicked.connect(self._remove_selected_job)
        self.horizontalLayoutTop.addWidget(self.btnRmvJob, 2, 3, alignment=QtCore.Qt.AlignCenter)

        # Vertical layout to hold jobs table and label
        self.verticalLayoutJobs = QtWidgets.QVBoxLayout()
        self.verticalLayoutJobs.setObjectName("verticalLayoutJobs")

        # Jobs table label
        self.labelReadOnly = QtWidgets.QLabel()
        self.labelReadOnly.setObjectName("labelReadOnly")
        self.labelReadOnly.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayoutJobs.addWidget(self.labelReadOnly)

        # Jobs table
        self.tableJobs = QtWidgets.QTableView()
        self.tableJobs.setMinimumSize(QtCore.QSize(50, 0))
        self.tableJobs.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tableJobs.setObjectName("tableJobs")
        self.tableJobs.horizontalHeader().setCascadingSectionResizes(False)
        self.verticalLayoutJobs.addWidget(self.tableJobs)

        # Tab container for text editors for typefile, and results text editor
        self.tabFiles = QtWidgets.QTabWidget()
        self.tabFiles.setObjectName("tabFiles")
        self.tabFiles.currentChanged.connect(self._change_active_editor)

        # Horizontal layout to hold jobs table and text view
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.addLayout(self.verticalLayoutJobs)
        self.horizontalLayout.addWidget(self.tabFiles)

        # Main widget layout
        self.verticalLayoutMain = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayoutMain.setObjectName("verticalLayoutMain")
        self.verticalLayoutMain.addLayout(self.horizontalLayoutTop)
        self.verticalLayoutMain.addLayout(self.horizontalLayout)

        self._init_jobs_table()
        self._init_menu_bar()
        self._init_toolbar()

        self._retranslate_ui()

        QtCore.QMetaObject.connectSlotsByName(self)

    def _retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CuiAnalysisRunner", "ACES Analysis Runner"))
        self.btnCloneJob.setText(_translate("CuiAnalysisRunner", "Clone Analysis"))
        self.btnRunJob.setText(_translate("CuiAnalysisRunner", "Run Analysis"))
        self.btnKeepJob.setText(_translate("CuiAnalysisRunner", "Keep Analysis"))
        self.btnRmvJob.setText(_translate("CuiAnalysisRunner", "Remove Analysis"))
        self.labelReadOnly.setText(_translate("CuiAnalysisRunner", "Engine Performance Analyses"))
        self.menuFile.setTitle(_translate("CuiModelEditor", "File"))
        self.actionOpen.setText(_translate("CuiModelEditor", "Open"))
        # self.actionSave.setText(_translate("CuiModelEditor", "Keep Analysis"))
        self.actionExit.setText(_translate("CuiModelEditor", "Exit"))

        # Set tool tips
        self.btnRunJob.setToolTip(_translate("CuiAnalysisRunner", 'Run the selected analysis in KreisPR'))
        self.btnKeepJob.setToolTip(_translate("CuiAnalysisRunner", 'Set the selected analysis to be kept upon exit'))
        self.btnCloneJob.setToolTip(_translate("CuiAnalysisRunner", 'Create an exact copy of the selected analysis'))
        self.btnRmvJob.setToolTip(_translate("CuiAnalysisRunner", 'Remove the selected analysis and associated data'))
        self.tableJobs.setToolTip('Click on a row to choose the active analysis')

    def _change_active_editor(self, tab_indx):
        self._active_ed_indx = tab_indx

    def _get_active_text_editor(self):
        return self._text_eds[self._active_ed_indx]

    def _exit(self):
        self.close()

    def closeEvent(self, event):
        if QMessageBox.question(self, ' ', 'Are you sure you want to quit?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            ok_to_close = self._prepare_to_close()
            if ok_to_close:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def _cut(self, e):
        wig = self._text_eds[self._active_ed_indx]
        if not wig.isReadOnly():
            wig.cut()

    def _copy(self, e):
        wig = self._text_eds[self._active_ed_indx]
        if not wig.isReadOnly():
            wig.copy()

    def _paste(self, e):
        wig = self._text_eds[self._active_ed_indx]
        if not wig.isReadOnly():
            wig.paste()

    def _undo(self, e):
        wig = self._text_eds[self._active_ed_indx]
        if not wig.isReadOnly():
            wig.undo()

    def _redo(self, e):
        wig = self._text_eds[self._active_ed_indx]
        if not wig.isReadOnly():
            wig.redo()

    # ---------------------------------
    # Job Table Management
    # ---------------------------------

    def _change_selected_job(self):
        indexes = self._table_jobs_select_model.selectedIndexes()
        for i in range(1, len(indexes)):
            if indexes[i].row() != indexes[0].row():
                raise Exception('More than one row selected, cannot currently handle this.')

        # Notify of the change in job selection
        if len(indexes) > 0:
            job_id = self._get_job_id_for_table_row(indexes[0].row())
        else:
            job_id = None
        self._selected_job_changed(self._active_job_id, job_id)
        self._active_job_id = job_id

    def _select_row_for_job_id(self, job_id):
        """
        Find row in table with given job id and set selected
        :param job_id:
        :return: selected row number
        """
        r = self._get_table_row_for_job_id(job_id)
        self.tableJobs.selectRow(r)
        return r

    def _get_table_row_for_job_id(self, job_id):
        """
        Find row in table with given job id and return the row number
        :param job_id:
        :return: selected row number
        """
        row = None
        for r in range(self._jobs_table_model.rowCount()):
            jid = self._get_job_id_for_table_row(r)
            if jid == job_id:
                row = r
                break
        return row

    def _get_job_id_for_table_row(self, row):
        id_index = self._jobs_table_model.createIndex(row, self.CLM_ID)
        job_id = self._jobs_table_model.data(id_index, role=QtCore.Qt.DisplayRole).value()
        return job_id

    def _get_job_data_for_table(self, job_id):

        kept = ''
        if job_id == self._get_kept_job_id():
            kept = self.KEEP_STR

        job_data = self._job_mgr.get_job_data(job_id)
        job_status = self._job_mgr.get_job_status(job_id)

        tbl_data = [
            job_id,
            job_data['model']['id'],
            job_status,
            kept
        ]
        return tbl_data

    def _refresh_table_item(self, job_id):

        row = self._get_table_row_for_job_id(job_id)
        tbl_data = self._get_job_data_for_table(job_id)

        # Job status
        indx = self._jobs_table_model.createIndex(row, self.CLM_STATUS)
        self._jobs_table_model.setData(indx, tbl_data[self.CLM_STATUS])

        # Kept status
        indx = self._jobs_table_model.createIndex(row, self.CLM_KEEP)
        self._jobs_table_model.setData(indx, tbl_data[self.CLM_KEEP])

    def _refresh_all_table_items(self):
        for r in range(self._jobs_table_model.rowCount()):
            id = self._get_job_id_for_table_row(r)
            self._refresh_table_item(id)

    def _clone_selected_job(self):
        if self.tableJobs.selectedIndexes():
            job_id = self._get_job_id_for_table_row(self.tableJobs.selectedIndexes()[0].row())
            self._clone_job(job_id)
        else:
            QtWidgets.QMessageBox.information(self, 'Cannot Clone Analysis', 'No analysis has been selected to clone.')

    def _run_selected_job(self):
        if self.tableJobs.selectedIndexes():
            job_id = self._get_job_id_for_table_row(self.tableJobs.selectedIndexes()[0].row())
            self._run_job(job_id)
        else:
            QtWidgets.QMessageBox.information(self, 'Cannot Run Analysis', 'No analysis has been selected to run.')

    def _keep_selected_job(self):
        if self.tableJobs.selectedIndexes():
            job_id = self._get_job_id_for_table_row(self.tableJobs.selectedIndexes()[0].row())
            keep_job = self._keep_job(job_id)
            if keep_job:
                self._kept_job_id = job_id
                self._refresh_all_table_items()
        else:
            QtWidgets.QMessageBox.information(self, 'Cannot Keep Analysis', 'No analysis has been selected to keep.')

    def _get_kept_job_id(self):
        return self._kept_job_id

    def _remove_selected_job(self):

        if self._job_mgr.count() <= 1:
            QtWidgets.QMessageBox.information(self, 'Cannot Remove Analysis', 'There must be at least one analysis.')
        else:
            if self.tableJobs.selectedIndexes():
                job_id = self._jobs_table_model.data(self.tableJobs.selectedIndexes()[0], role=QtCore.Qt.DisplayRole).value()
                self._active_job_id = None
                self._jobs_table_model.remove_data_item(self.tableJobs.selectedIndexes()[0].row())
                self._job_mgr.delete_job(job_id)
            else:
                QtWidgets.QMessageBox.information(self, 'Cannot Remove Analysis', 'No analysis has been selected to remove.')

    def _clear_jobs(self):
        self._active_job_id = None
        self._jobs_table_model.remove_all_data_items()
        self._job_mgr.delete_all_jobs()


    # ---------------------------------
    # Must Inherit Methods
    # ---------------------------------

    @abc.abstractmethod
    def _init_text_eds(self):
        """
        Must setup the data to be used for all the desired text editors to show, also this method must call the
        setup_text_edit_tabs method in the base class.
        :return: none
        """

    @abc.abstractmethod
    def _open_file(self):
        """

        :return: none
        """

    @abc.abstractmethod
    def _clone_job(self, job_id):
        """

        :param job_id:
        :return:
        """

    @abc.abstractmethod
    def _run_job(self, job_id):
        """
        must call update job upon completion of the subprocess to update the status of the selected job being executed
        :param job_id:
        :return:
        """

    @abc.abstractmethod
    def _keep_job(self, job_id):
        """
        :return: none
        """

    @abc.abstractmethod
    def _prepare_to_close(self):
        """
        Override to handle any tasks required prior to closing the app
        :return:
        """

    # ---------------------------------
    # Inheritable Methods
    # ---------------------------------

    def _selected_job_changed(self, from_job_id, to_job_id):
        """
        Overrideble base class method to be notified of changes in the selected job.  Base class method does nothing
        :param from_job_id:
        :param to_job_id:
        :return: nothing
        """
        pass

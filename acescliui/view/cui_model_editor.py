import os
import abc
import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from ..model.tree_model import TreeModel
from ..model.table_model import TableModel


class CuiModelEditor(QtWidgets.QMainWindow):
    """
    my doc string
    """

    # Column numbers corresponding to the data types in each job table column
    CLM_PARAM = 0
    CLM_MAP = 3

    prj_path = os.path.join(os.path.split(__file__)[0])+"/.."

    def __init__(self, parent=None, window_title='Aces Model Editor', has_read_only_inputs=True):
        super(CuiModelEditor, self).__init__(parent)
        self._ro_input_data = {}
        self.__input_map_kwds = []
        self.__changesSaved = True
        self.__text_eds = []  # List of text editors that are hosted by the tab widget
        self.__active_ed_indx = -1  # Tracks the tab index of the currently active text editor
        self.__init_ui(has_read_only_inputs)

        self.__ctx_menu = None

        # Set main window title
        self.__dflt_window_title = window_title
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate('CuiModelEditor', self.__dflt_window_title))  # Could call the method in retranslate UI but this will handle the case when I decide to use ui files later.

    # ---------------------------------
    # UI Setup
    # ---------------------------------

    def _init_ro_table_ui(self):
        self._ro_table_hdrs = ['Parameter', 'Value', 'Units', 'Mapped']
        mdl = TableModel([], self._ro_table_hdrs)
        self.tblViewReadOnlyInpts.setModel(mdl)
        self.tblViewReadOnlyInpts.setColumnWidth(1, 900)
        self.tblViewReadOnlyInpts.horizontalHeader().setStretchLastSection(False)
        self.tblViewReadOnlyInpts.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cmbReadOnly.addItem("- Select -")

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
            self.__text_eds.append(text_editors[i])
            self.tabFiles.addTab(newTabWig, _translate('CuiModelEditor', tab_titles[i]))

        self.tabFiles.setCurrentIndex(0)

    def __init_menu_bar(self):
        # Create menu bar
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 953, 25))
        self.menuBar.setObjectName("menuBar")

        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menuBar)

        self.actionMainOpen = QtWidgets.QAction(self)
        self.actionMainOpen.setObjectName("actionMainOpen")
        self.actionMainOpen.setShortcut("Ctrl+O")
        self.actionMainOpen.triggered.connect(self._open_model)

        self.actionMainSave = QtWidgets.QAction(self)
        self.actionMainSave.setObjectName("actionSave")
        self.actionMainSave.setShortcut("Ctrl+S")
        self.actionMainSave.triggered.connect(self._save)

        self.actionExit = QtWidgets.QAction(self)
        self.actionExit.setObjectName("action_Close")
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(self._exit)

        # Add menu bar actions
        # self.menuFile.addAction(self.actionViewTemplate)
        self.menuFile.addAction(self.actionMainOpen)
        self.menuFile.addAction(self.actionMainSave)
        self.menuFile.addAction(self.actionExit)
        self.menuBar.addAction(self.menuFile.menuAction())

    def __init_toolbar(self):

        self.openAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/open.png'), 'Open Model (Ctrl+O)', self)
        self.openAction.setStatusTip('Delete and copy text to clipboard')
        #self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self._open_model)

        self.saveAction = QtWidgets.QAction(QtGui.QIcon(self.prj_path + '/icons/save.png'), 'Save Model (Ctrl+S)', self)
        self.saveAction.setStatusTip('Copy text to clipboard')
        #self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self._save)

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
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.pasteAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

        # Makes the next toolbar appear underneath this one
        self.addToolBarBreak()

    def __init_status_bar(self):
        # Create status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName('statusbar')
        self.setStatusBar(self.statusbar)

    def __init_ui(self, has_read_only_inputs):
        
        self.setObjectName('CuiModelEditor')
        self.resize(953, 809)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName('centralwidget')
        self.setCentralWidget(self.centralwidget)
        
        # Top horizontal layout
        self.gridLayoutTop = QtWidgets.QGridLayout()
        self.gridLayoutTop.setObjectName('giridLayoutTop')

        # ------------------------------------------
        # Tab text editor UI controls
        # ------------------------------------------

        # Tab container for text editors for typefile, and results text editor
        self.tabFiles = QtWidgets.QTabWidget()
        self.tabFiles.setObjectName("tabFiles")
        self.tabFiles.currentChanged.connect(self._change_active_editor)

        # ------------------------------------------
        # Read only inputs UI controls
        # ------------------------------------------
        if has_read_only_inputs:
            # Read only inputs label
            self.labelReadOnly = QtWidgets.QLabel()
            self.labelReadOnly.setObjectName("labelReadOnly")
            self.labelReadOnly.setMinimumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
            self.labelReadOnly.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))

            # Read only inputs combo box
            self.cmbReadOnly = QtWidgets.QComboBox()
            self.cmbReadOnly.setObjectName("cmbReadOnly")
            self.cmbReadOnly.setMinimumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
            self.cmbReadOnly.setMaximumSize(QtCore.QSize(200, QtWidgets.QWIDGETSIZE_MAX))
            self.cmbReadOnly.currentIndexChanged.connect(self._combo_box_index_changed)

            # Horizontal layout to hold read only label and combo
            self.horizLayoutReadOnlyLable = QtWidgets.QHBoxLayout()
            self.horizLayoutReadOnlyLable.setObjectName("horizLayoutReadOnlyLable")
            self.horizLayoutReadOnlyLable.addWidget(self.labelReadOnly)
            self.horizLayoutReadOnlyLable.addWidget(self.cmbReadOnly)
            self.horizLayoutReadOnlyLable.addSpacing(800)

            # Read only inputs table view
            self.tblViewReadOnlyInpts = QtWidgets.QTableView()
            self.tblViewReadOnlyInpts.setShowGrid(True)
            self.tblViewReadOnlyInpts.setObjectName("tblViewReadOnlyInpts")

            # Vertical layout to hold read only controls
            self.verticalLayoutReadOnly = QtWidgets.QVBoxLayout()
            self.verticalLayoutReadOnly.setObjectName("verticalLayoutReadOnly")
            self.verticalLayoutReadOnly.addLayout(self.horizLayoutReadOnlyLable)
            self.verticalLayoutReadOnly.addWidget(self.tblViewReadOnlyInpts)

        # ------------------------------------------
        # Add everything to main layouts
        # ------------------------------------------

        # Horizontal layout to hold everything under grid layout
        self.lowerLayout = QtWidgets.QVBoxLayout()
        self.lowerLayout.setObjectName("lowerLayout")
        self.lowerLayout.addWidget(self.tabFiles)
        if has_read_only_inputs:
            self.lowerLayout.addLayout(self.verticalLayoutReadOnly)

        # Main widget layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addLayout(self.gridLayoutTop)
        self.verticalLayout.addLayout(self.lowerLayout)

        self.__init_menu_bar()
        self.__init_toolbar()
        self.__init_status_bar()
        if has_read_only_inputs:
            self._init_ro_table_ui()

        self._retranslate_ui(has_read_only_inputs)

        QtCore.QMetaObject.connectSlotsByName(self)

    def _retranslate_ui(self, has_read_only_inputs):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CuiModelEditor", "ACES Model Editor"))
        self.menuFile.setTitle(_translate("CuiModelEditor", "File"))
        self.actionMainOpen.setText(_translate("CuiModelEditor", "Open"))
        self.actionMainSave.setText(_translate("CuiModelEditor", "Save"))
        self.actionExit.setText(_translate("CuiModelEditor", "Exit"))
        if has_read_only_inputs:
            self.labelReadOnly.setText(_translate("CuiModelEditor", "Mapped Read Only Inputs"))
            self.cmbReadOnly.setToolTip(_translate("CuiAnalysisRunner", 'Select which input data set to view in the table below'))

    def _add_widget_to_grid_layout(self, wig, row, column, alignment=QtCore.Qt.AlignCenter):
        """

        :param wig:
        :param row:
        :param column:
        :return:
        """
        self.gridLayoutTop.addWidget(wig, row, column, alignment)

    def _add_layout_to_grid_layout(self, lay, row, column, alignment=QtCore.Qt.AlignCenter):
        """

        :param wig:
        :param row:
        :param column:
        :return:
        """
        self.gridLayoutTop.addLayout(lay, row, column, alignment)

    def _change_active_editor(self, tab_indx):
        self.__active_ed_indx = tab_indx

    def _get_active_text_editor(self):
        return self.__text_eds[self.__active_ed_indx]

    def _save(self):
        self._save_model()
        self.__changesSaved = True
        self._update_window_title()

    def _exit(self):
        self.close()

    def closeEvent(self, event):
        if self.__changesSaved:
            if QMessageBox.question(self, ' ', 'Are you sure you want to quit?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                self._prepare_to_close()
                event.accept()
            else:
                event.ignore()
        else:
            rspns = QMessageBox.question(self, ' ', 'Save changes before quiting?', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if rspns == QMessageBox.Yes:
                self._save_model()
                self._prepare_to_close()
                event.accept()
            elif rspns == QMessageBox.No:
                self._prepare_to_close()
                event.accept()
            else:
                event.ignore()

    def _cut(self, e):
        wig = self.__text_eds[self.__active_ed_indx]
        if not wig.isReadOnly():
            wig.cut()

    def _copy(self, e):
        wig = self.__text_eds[self.__active_ed_indx]
        if not wig.isReadOnly():
            wig.copy()

    def _paste(self, e):
        wig = self.__text_eds[self.__active_ed_indx]
        if not wig.isReadOnly():
            wig.paste()

    def _undo(self, e):
        wig = self.__text_eds[self.__active_ed_indx]
        if not wig.isReadOnly():
            wig.undo()

    def _redo(self, e):
        wig = self.__text_eds[self.__active_ed_indx]
        if not wig.isReadOnly():
            wig.redo()

    def _cursor_position(self):
        if self.__text_eds:
            cursor = self.__text_eds[self.__active_ed_indx].textCursor()

            # Mortals like 1-indexed things
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber()

            self.statusbar.showMessage('Line: {} | Column: {}'.format(line,col))

    def _text_changed(self):
        self.__changesSaved = False
        self._update_window_title()

    def _update_window_title(self):
        _translate = QtCore.QCoreApplication.translate
        if self.__changesSaved:
            title = self.__dflt_window_title
            self.setWindowTitle(_translate('CuiModelEditor', title))
        else:
            title = self.__dflt_window_title + ' (UNSAVED)'
            self.setWindowTitle(_translate('CuiModelEditor', title))

    def _combo_box_index_changed(self, index):
        ro_key = self.cmbReadOnly.itemData(index)
        self._set_readonly_table_model(ro_key)

    def _add_readonly_inputs(self, input_data, ro_item_key, ro_combo_text):
        self._ro_input_data[ro_item_key] = input_data
        self.cmbReadOnly.addItem(ro_combo_text, userData=ro_item_key)

    def _clear_readonly_inputs(self):
        self._ro_input_data.clear()
        for i in range(1, self.cmbReadOnly.count()):
            self.cmbReadOnly.removeItem(self.cmbReadOnly.count()-1)

    def _set_readonly_input_mapped_state(self):
        try:
            for kk, ii in self._ro_input_data.items():
                for k, i in ii.items():
                    mapped = 'YES' if k in self.__input_map_kwds else 'NO'
                    i['mapped'] = mapped
            ro_key = self.cmbReadOnly.currentData()

            # Find the data in the read only model and change the mapping
            mdl = self.tblViewReadOnlyInpts.model()
            strt_idx = mdl.createIndex(0, self.CLM_PARAM)
            if ro_key in self._ro_input_data:
                for k, i in self._ro_input_data[ro_key].items():
                    indxs = mdl.match(strt_idx, QtCore.Qt.DisplayRole, k, 1)
                    if len(indxs) == 1:
                        data_idx = mdl.createIndex(indxs[0].row(), self.CLM_MAP)
                        self.tblViewReadOnlyInpts.model().setData(data_idx, i['mapped'], QtCore.Qt.EditRole)
        except AttributeError:
            logging.exception(' Non fatal attribute error raised')

    def _set_readonly_table_model(self, ro_key):
        try:
            if not ro_key in self._ro_input_data:
                mdl = TableModel([], self._ro_table_hdrs)
                self.tblViewReadOnlyInpts.setModel(mdl)
            else:
                data_dict = self._ro_input_data[ro_key]
                ro_model = []
                for k, i in data_dict.items():
                    itm = [k, i['value'], i['units'], i['mapped']]
                    ro_model.append(itm)
                mdl = TableModel(ro_model, self._ro_table_hdrs)
                self.tblViewReadOnlyInpts.setModel(mdl)
        except AttributeError:
            logging.exception(' Non fatal attribute error raised')

    def _update_template_keywords(self, kwds):
        self.__input_map_kwds = kwds

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        self._show_read_only_input_context_menu(event)

    def _show_read_only_input_context_menu(self):
        """
        Re-implement in the child class to handle context menu events for the
        read only inputs table view.  Does nothing in the base class
        :return: 
        """
        pass

    @abc.abstractmethod
    def _init_read_only_inputs(self):
        """
        Must call _add_readonly_inputs and add any readonly data required
        :return: nothing
        """

    @abc.abstractmethod
    def _init_text_eds(self):
        """
        Must setup the data to be used for all the desired text editors to show, also this method must call the
        setup_text_edit_tabs method in the base class.
        :return: none
        """

    @abc.abstractmethod
    def _open_model(self):
        """

        :return: none
        """

    @abc.abstractmethod
    def _save_model(self):
        """

        :return: none
        """

    @abc.abstractmethod
    def _prepare_to_close(self):
        """
        Override to handle any tasks required prior to closing the app
        :return: none
        """

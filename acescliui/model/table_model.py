from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex


class TableModel(QAbstractTableModel):

    def __init__(self, initial_data, data_headers, parent=None, *args):
        super(TableModel, self).__init__(parent)

        # List of lists
        self._data = initial_data
        # List of strings
        self._headers = data_headers

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def add_data_item(self, new_data_item):
        if self._data:
            new_row = len(self._data)
        else:
            new_row = 1
        self.beginInsertRows(QModelIndex(), new_row, new_row)
        self._data.append(new_data_item)
        self.endInsertRows()
        return new_row

    def remove_data_item(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self._data.pop(row)
        self.endRemoveRows()

    def remove_all_data_items(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()-1)
        self._data.clear()
        self.endRemoveRows()

    def rowCount(self, parent=None):
        row_len = 0
        if self._data:
            row_len = len(self._data)
        return row_len

    def columnCount(self, parent=None):
        clm_len = len(self._headers)
        if self._data:
            clm_len = len(self._data[0])
        return clm_len

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            if self._data:
                value = self._data[index.row()][index.column()]
                return QVariant(value)
            else:
                return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        else:
            return False

    def headerData(self, sect, orient, role=None):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[sect])
        return QVariant()

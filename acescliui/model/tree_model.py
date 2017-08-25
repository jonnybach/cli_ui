from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant


class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0


class TreeModel(QAbstractItemModel):
    def __init__(self, read_only_data, read_only_headers, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(read_only_headers)
        self.setup_model_data(read_only_data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.rootItem.data(section))
        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setup_model_data(self, data, root_item):
        """

        :param data: multi-level dictionary containing the key value pairs of all read only values and units
        :param root_item: root parent item in the tree model
        :return: nothing
        """

        # Recurse through read only dictionary and build tree model
        self.__recurse_model_data(data, root_item)

    def __recurse_model_data(self, data_dict, parent):

        for k, v in data_dict.items():

            if isinstance(v, dict):
                # Parent to another leaf item
                clm_data = [k, ""]
                new_item = TreeItem(clm_data, parent)
                parent.appendChild(new_item)
                self.__recurse_model_data(v, new_item)

            else:
                # this parent is a parameter leaf item with data values to be added as a child
                clm_data = [k,v]
                new_item = TreeItem(clm_data, parent)
                parent.appendChild(new_item)
                return

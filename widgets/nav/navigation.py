# System Imports
import os
import sys

# Third Party Imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import qtawesome

# Local Imports
from sharedtoolbox import style, configs, event_handler
from sharedtoolbox.dialogs import infoDialog
from sharedtoolbox.widgets.base import *

# ______________________________________________________________________________________________________________________

class NavigationWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(NavigationWidget, self).__init__(objectName='nav', *args, **kwargs)
        self.setMinimumWidth(100)
        self.resize(*configs.Prefs.nav_widget_size)

        # Properties
        self._item_cache = {}

        # Widgets
        self.nav_tree = QTreeView()
        self.nav_tree.header().hide()
        self.proxy_model = FilterProxyModel()
        self.btn_new_script = QPushButton(objectName='icon', enabled=False, toolTip='Create a new script in selected location',
                                          icon=qtawesome.icon('fa5b.python', color=style.STYLE.get('primary')))
        self.btn_new_dir = QPushButton(objectName='icon', enabled=False, toolTip='Create a new folder in selected location',
                                          icon=qtawesome.icon('fa5s.folder-plus', color=style.STYLE.get('primary')))
        self.btn_open_dir = QPushButton(objectName='icon', enabled=False, toolTip='Open selected location',
                                          icon=qtawesome.icon('ei.folder-open', color=style.STYLE.get('primary')))
        self.search_bar = QLineEdit(placeholderText='Search..', objectName='searchbar', fixedHeight=24)

        # Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(8, 8, 8, 0)
        self.header_layout.setSpacing(4)
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout = VScrollLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(8)
        self.layout().addLayout(self.header_layout)
        self.layout().addWidget(HLine())
        self.layout().addLayout(self.body_layout)
        self.body_layout.addWidget(self.search_bar)
        self.body_layout.addWidget(self.scroll_layout.scroll_area)
        self.scroll_layout.addWidget(self.nav_tree)

        self.init_header_layout()

        # Connections
        self.search_bar.textChanged.connect(self._on_search_bar_textChanged)
        self.btn_new_script.clicked.connect(self._on_btn_new_script_clicked)
        self.btn_new_dir.clicked.connect(self._on_btn_new_dir_clicked)
        self.btn_open_dir.clicked.connect(self._on_btn_open_dir_clicked)
        event_handler.file_opened.connect(self._on_editor_file_opened)

        # Init
        self._set_new_model()
        self._load_scripts()

    @property
    def selected_item(self):
        """Returns the selected item"""
        index = self.nav_tree.selectionModel().currentIndex()
        if index.isValid():
            item = self.proxy_model.itemData(self.nav_tree.selectedIndexes()[0])
            return item
        else:
            return None
        
    @property
    def selected_item_path(self):
        """Returns the selected item's path"""
        item = self.selected_item
        if item:
            return item.get(256)
        else:
            return None

    def reload(self):
        """Reload tool"""
        self._item_cache = {}
        self._set_new_model()
        self._load_scripts()

    def init_header_layout(self):
        """Init the header layout"""
        self.header_layout.addWidget(QLabel(text='Explorer', enabled=False))
        self.header_layout.addItem(HSpacer())
        self.header_layout.addWidget(self.btn_new_script)
        self.header_layout.addWidget(self.btn_new_dir)
        self.header_layout.addWidget(VLine())
        self.header_layout.addWidget(self.btn_open_dir)

    def _set_new_model(self):
        """Sets a new model on the treeview"""
        self.model = QStandardItemModel()
        self.proxy_model.setSourceModel(self.model)
        self.nav_tree.setModel(self.proxy_model)
        self.nav_tree.selectionModel().selectionChanged.connect(self._on_treeview_itemSelected)

    def _on_treeview_itemSelected(self, *args, **kwargs):
        """Triggered when a ContainerItem/ScriptItem has been selected"""
        item = self.selected_item
        item_path = item.get(256)

        # Toggle new script button state
        if item_path is None or item_path.endswith('.py'):
            self.btn_new_script.setEnabled(False)
            self.btn_new_dir.setEnabled(False)
            self.btn_open_dir.setEnabled(False)
        else:
            self.btn_new_script.setEnabled(True)
            self.btn_new_dir.setEnabled(True)
            self.btn_open_dir.setEnabled(True)

        # Emit selection signal
        if item_path and item_path.endswith('.py'):
            event_handler.file_clicked.emit(item_path)

    def _load_scripts(self):
        """Loads all scripts found"""
        _item_cache = {}

        # Local scripts
        local_script_path = configs.Prefs.get_local_script_path()
        local_item = ContainerItem(local_script_path, 'Local')
        self.model.appendRow(local_item)
        _item_cache[local_script_path] = local_item

        if os.path.exists(local_script_path):
            for root, dirs, files in os.walk(local_script_path):
                for dir in dirs:
                    itemN = ContainerItem(os.path.join(root, dir), dir)
                    _item_cache.get(root).appendRow(itemN)
                    _item_cache[os.path.join(root, dir)] = itemN
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.py'):
                        itemN = ScriptItem(file_path, file[0:-3])
                        _item_cache.get(root).appendRow(itemN)
                    
        # Shared scripts
        shared_script_path = configs.Prefs.get_shared_script_path()
        shared_item = ContainerItem(shared_script_path, 'Shared')
        self.model.appendRow(shared_item)
        _item_cache[shared_script_path] = shared_item

        if os.path.exists(shared_script_path):
            for root, dirs, files in os.walk(shared_script_path):
                for dir in dirs:
                    itemN = ContainerItem(os.path.join(root, dir), dir)
                    _item_cache.get(root).appendRow(itemN)
                    _item_cache[os.path.join(root, dir)] = itemN
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.py'):
                        itemN = ScriptItem(file_path, file[0:-3])
                        _item_cache.get(root).appendRow(itemN)

        # Project Scripts
        project_root_path = configs.Prefs.get_project_root_path()
        project_script_location = configs.Prefs.get_project_script_location()
        project_item = ContainerItem(None, 'Projects')
        self.model.appendRow(project_item)
        _item_cache[project_root_path] = shared_item

        if project_root_path and os.path.exists(project_root_path):
            for dir in os.listdir(project_root_path):
                dir_path = os.path.join(project_root_path, dir)
                if not os.path.isdir(dir_path):
                    continue
                project_script_path = os.path.join(dir_path, project_script_location)
                current_project_item = ContainerItem(project_script_path, dir)
                _item_cache[project_script_path] = current_project_item
                project_item.appendRow(current_project_item)
                for root, dirs, files in os.walk(project_script_path):
                    for dir_ in dirs:
                        itemN = ContainerItem(os.path.join(root, dir_), dir_)
                        _item_cache.get(root).appendRow(itemN)
                        _item_cache[os.path.join(root, dir_)] = itemN
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file.endswith('.py'):
                            itemN = ScriptItem(file_path, file[0:-3])
                            _item_cache.get(root).appendRow(itemN)

        self._item_cache = _item_cache

    def _on_search_bar_textChanged(self, search_text):
        """Search the script list"""
        self.proxy_model.setSearchTerm(search_text)
        if search_text:
            self.nav_tree.expandAll()

    def _on_btn_new_dir_clicked(self):
        """Creates a new directory at the selected location"""
        text, confirmed = QInputDialog.getText(self, 'New Folder', "Enter the new folder's name")
        if not confirmed:
            return
        path = os.path.join(self.selected_item_path, text)
        if os.path.exists(path):
            infoDialog.InfoDialog(text='Folder already exists').exec()
            return
        try:
            os.makedirs(path, exist_ok=True)
        except:
            print('Failed creating new script at "{}"'.format(path))
            return
        itemN = ContainerItem(path, os.path.basename(path))
        self._item_cache.get(self.selected_item_path).appendRow(itemN)

    def _on_btn_open_dir_clicked(self):
        """Open the selected item in the file browser"""
        current_item_path = self.selected_item.get(256)
        if not os.path.isdir(current_item_path):
            dlg = infoDialog.InfoDialog(text='Directory not found', desc=current_item_path, info_level=3)
            dlg.exec_()
            return
        if current_item_path:
            os.startfile(current_item_path)

    def _on_btn_new_script_clicked(self):
        """Creates a new script in the selected path"""
        text, confirmed = QInputDialog.getText(self, 'New Script', "Enter the new script's name")
        if not confirmed:
            return
        if not text.endswith('.py'):
            text += '.py'
        path = os.path.join(self.selected_item_path, text)
        if os.path.exists(path):
            infoDialog.InfoDialog(text='File already exists').exec()
            return
        try:
            os.makedirs(self.selected_item_path, exist_ok=True)
            open(path, 'a').close()
        except:
            print('Failed creating new script at "{}"'.format(path))
            return
        itemN = ScriptItem(path, os.path.basename(path)[0:-3])
        self._item_cache.get(os.path.dirname(path)).appendRow(itemN)

        # Selection not working
        # index = self.nav_tree.model().index(itemN.row(), itemN.column())
        # self.nav_tree.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectionFlag.Select)

    def iter_tree_items(self):
        """WIP: Related on _on_editor_file_opened"""
        root = self.model.invisibleRootItem()
        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child.hasChildren():
                        yield from recurse(child)
        if root is not None:
            yield from recurse(root)

    def _on_editor_file_opened(self, file):
        """Triggered by the editor when a new file has been opened
        Make sure the given file is selected in the navigation widget
        
        Args:
            file (str): File path
        """
        if self.selected_item_path and os.path.normpath(self.selected_item_path) != os.path.normpath(file):
            # Select the file if found
            # TODO: Loop over model items, if item matches get its index from the model and self.nav_tree.expand(index)
            pass

    def _exit_handler(self):
        """Triggered on app quit"""
        configs.Prefs.set_pref_data('nav_widget_size', (self.width(), self.height()))


class ContainerItem(QStandardItem):

    def __init__(self, path, *args, **kwargs):
        icon = qtawesome.icon('fa.folder', color=style.STYLE.get('secondary'))
        super(ContainerItem, self).__init__(icon, *args, **kwargs)
        self.path = path
        self.setEditable(False)
        self.setCheckable(False)
        self.setData(path, role=Qt.UserRole)


class ScriptItem(QStandardItem):

    def __init__(self, script, *args, **kwargs):
        icon = qtawesome.icon('fa5b.python', color=style.STYLE.get('primary'))
        super(ScriptItem, self).__init__(icon, *args, **kwargs)
        self.script = os.path.normpath(script)
        self.setEditable(False)
        self.setCheckable(False)
        self.setData(script, role=Qt.UserRole)

        
class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super(FilterProxyModel, self).__init__(*args, **kwargs)
        self.search_term = ''

    def setSearchTerm(self, term):
        self.search_term = term.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.search_term:
            return True

        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        # Check the current item
        if self.search_term in model.data(index).lower():
            return True

        # Check the children of the current item
        for row in range(model.rowCount(index)):
            if self.filterAcceptsRow(row, index):
                return True

        return False
# ______________________________________________________________________________________________________________________

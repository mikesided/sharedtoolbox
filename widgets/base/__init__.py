# System Imports

# Third Party Imports
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

# Local Imports

# ______________________________________________________________________________________________________________________

__all__ = [
    'Spacer',
    'VSpacer',
    'HSpacer',
    'VLine',
    'HLine',
    'QComboBoxNoWheel',
    'HScrollLayout', 
    'VScrollLayout', 
    'FlowLayout',
]

class Spacer(QSpacerItem):
    """Spacer Item"""
    def __init__(self, w=1, h=1, h_expand=False, v_expand=False):
        """Constructor
        
        Args:
            w (int): width, defaults to 1
            h (int): height, defaults to 1
            h_expand (bool): Horizontal Expanding, defaults to false
            v_expand (bool): Vertical Expanding, defaults to false

        Returns:
            QSpacerItem
        """
        h_policy = QSizePolicy.Expanding if h_expand else QSizePolicy.Fixed
        v_policy = QSizePolicy.Expanding if v_expand else QSizePolicy.Fixed
        super(Spacer, self).__init__(w, h, h_policy, v_policy)

class VSpacer(Spacer):
    def __init__(self, w=1, *args, **kwargs):
        super(VSpacer, self).__init__(w=w, v_expand=True, *args, **kwargs)

class HSpacer(Spacer):
    def __init__(self, h=1, *args, **kwargs):
        super(HSpacer, self).__init__(h=h, h_expand=True, *args, **kwargs)

class VScrollLayout(QVBoxLayout):
    def __init__(self, layout=None, *args, **kwargs):
        """Constructor
        
        Args:
            parent: Parent widget
            layout: Layout to add this scroll layout to
            
        Returns:
            QVBoxLayout
        """
        super(VScrollLayout, self).__init__(*args, **kwargs)
        self.scroll_area = QScrollArea(*args, **kwargs)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_widget = QWidget(*args, **kwargs)
        self.scroll_area.setWidget(self._scroll_widget)
        if layout:
            layout.addWidget(self.scroll_area)
        self._scroll_widget.setLayout(self)

class HScrollLayout(QHBoxLayout):
    def __init__(self, layout=None, *args, **kwargs):
        """Constructor
        
        Args:
            parent: Parent widget
            layout: Layout to add this scroll layout to
            
        Returns:
            QVBoxLayout
        """
        super(HScrollLayout, self).__init__(*args, **kwargs)
        self.scroll_area = QScrollArea(*args, **kwargs)
        self.scroll_area.setMinimumHeight(2)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_widget = QWidget(*args, **kwargs)
        self.scroll_area.setWidget(self._scroll_widget)
        if layout:
            layout.addWidget(self.scroll_area)
        self._scroll_widget.setLayout(self)
        self.scroll_area.wheelEvent = self._wheelEvent

    def _wheelEvent(*args):
        pass

class VLine(QFrame):
    def __init__(self, parent=None, w=1, *args, **kwargs):
        super(VLine, self).__init__(parent, *args, **kwargs)
        self.setObjectName('line')
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setFixedWidth(w)

class HLine(QFrame):
    def __init__(self, parent=None, h=1, *args, **kwargs):
        super(HLine, self).__init__(parent, *args, **kwargs)
        self.setObjectName('line')
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setFixedHeight(h)

class QComboBoxNoWheel(QComboBox):

    def __init__(self, *args, **kwargs):
        super(QComboBoxNoWheel, self).__init__(*args, **kwargs)
        self.setView(QListView())

    def wheelEvent(self, event):
        event.ignore()

class FlowLayout(QLayout):
    """Custom layout that mimics the behaviour of a flow layout"""
 
    def __init__(self, margins=(0, 0, 0, 0), spacing=-1, *args, **kwargs):
        """Create a new FlowLayout instance.
        This layout will reorder the items automatically."""
        super(FlowLayout, self).__init__(*args, **kwargs)
        self.setContentsMargins(*margins)
        self.setSpacing(spacing)
 
        self.itemList = []
 
    def __del__(self):
        """Delete all the items in this layout"""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
 
    def addItem(self, item):
        """Add an item at the end of the layout.
        This is automatically called when you do addWidget()
        item (QWidgetItem)"""
        self.itemList.append(item)
 
    def count(self):
        """Get the number of items in the this layout
        @return (int)"""
        return len(self.itemList)
 
    def itemAt(self, index):
        """Get the item at the given index
        @param index (int)
        @return (QWidgetItem)"""
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None
 
    def takeAt(self, index):
        """Remove an item at the given index
        @param index (int)
        @return (None)"""
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None
 
    def insertWidget(self, index, widget):
        """Insert a widget at a given index
        @param index (int)
        @param widget (QWidget)"""
        item = QWidgetItem(widget)
        self.itemList.insert(index, item)
 
    def expandingDirections(self):
        """This layout grows only in the horizontal dimension"""
        return Qt.Orientations(Qt.Horizontal)
 
    def hasHeightForWidth(self):
        """If this layout's preferred height depends on its width
        @return (boolean) Always True"""
        return True
 
    def heightForWidth(self, width):
        """Get the preferred height a layout item with the given width
        @param width (int)"""
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
 
    def setGeometry(self, rect):
        """Set the geometry of this layout
        @param rect (QRect)"""
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
 
    def sizeHint(self):
        """Get the preferred size of this layout
        @return (QSize) The minimum size"""
        return self.minimumSize()
 
    def minimumSize(self):
        """Get the minimum size of this layout
        @return (QSize)"""
        # Calculate the size
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        # Add the margins
        if self.itemList:
            l, t, r, b = self.getContentsMargins()
            size += QSize(l+r, t+b)
        return size
 
    def doLayout(self, rect, testOnly):
        """Layout all the items
        @param rect (QRect) Rect where in the items have to be laid out
        @param testOnly (boolean) Do the actual layout"""
        l, t, r, b = self.getContentsMargins()
        x = rect.x() + l
        y = rect.y() + t
        lineHeight = 0
 
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > (rect.right() - r) and lineHeight > 0:
                x = rect.x() + l
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
 
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
 
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        if self.itemList:
            return y + lineHeight - rect.y() + b
        else:
            return 
    
# ______________________________________________________________________________________________________________________

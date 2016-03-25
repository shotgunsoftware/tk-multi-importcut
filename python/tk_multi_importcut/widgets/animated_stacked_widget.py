# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from tank.platform.qt import QtCore, QtGui

class AnimatedStackedWidget(QtGui.QStackedWidget):
    """
    A thin layer on top of QStackedWidget animating transitions
    """
    # Signal emitted when the first page is reached
    # when moving backward
    first_page_reached = QtCore.Signal()
    # Signal emitted when the last page is reached
    # when moving forward
    last_page_reached = QtCore.Signal()

    def __init__(self, parent=None, animation_duration=600):
        QtGui.QStackedWidget.__init__(self, parent)
        # Will be used to keep animations around
        # For garbage collection purpose
        self.__anims = [None, None]
        self.__anim_grp = None
        self._animation_duration = animation_duration

    @QtCore.Slot()
    def prev_page(self):
        """
        Move back to the previous page
        """
        self.goto_page(self.currentIndex()-1)

    @QtCore.Slot()
    def next_page(self):
        """
        Move to the next page if any
        """
        self.goto_page(self.currentIndex()+1)

    def set_current_index(self, index):
        """
        Thin wrapper around setCurrentIndex
        Ensuring first_page_reached and last_page_reached
        are emitted when needed
        """
        self.setCurrentIndex(index)
        # Emit signals if needed
        if index == 0:
            self.first_page_reached.emit()

        if index == self.count()-1:
            self.last_page_reached.emit()

    @QtCore.Slot(int)
    def goto_page(self, to_index):
        """
        Animate transition from the current page to the one with the given index
        """
        from_index = self.currentIndex()
        if from_index == to_index: # Already on the wanted page
            return

        this_page = self.widget(from_index)
        next_page = self.widget(to_index)

        if not this_page or not next_page: # Indexes out of range ?
            return

        if not hasattr(QtCore, "QAbstractAnimation"):
            # this version of Qt (probably PyQt4) doesn't contain
            # Q*Animation classes so just change the page:
            self.set_current_index(to_index)
            return
        geometry =  self.geometry()
        if from_index > to_index: # Backward
            rest_pos = -geometry.width()
        else: # Forward
            rest_pos = geometry.width()

        if self.__anim_grp and self.__anim_grp.state() == QtCore.QAbstractAnimation.Running:
            # The previous animation hasn't finished yet so jump to the end!
            self.__anim_grp.setCurrentTime(self.__anim_grp.duration())

        # Rest position
        next_page.move(next_page.x()+rest_pos, next_page.y())
        self.set_current_index(to_index)
        # Show and raise both pages so the animation will be visible
        this_page.show()
        this_page.raise_()       
        next_page.show()
        next_page.raise_()

        # Animations
        if self._animation_duration < 1 or not hasattr(QtCore, "QAbstractAnimation"):
            # this version of Qt (probably PyQt4) doesn't contain
            # Q*Animation classes so just change the page:
            this_page.hide()
            return
        
        # Keep them around for garbage collection purpose
        # That might not be needed, but who knows ...
        self.__anims[0] = QtCore.QPropertyAnimation(this_page, "pos")
        self.__anims[0].setDuration(self._animation_duration)
        self.__anims[0].setStartValue(QtCore.QPoint(this_page.x(), this_page.y()))
        self.__anims[0].setEndValue(QtCore.QPoint(this_page.x()-rest_pos, this_page.y()))
        self.__anims[0].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.__anims[1] = QtCore.QPropertyAnimation(next_page, "pos")
        self.__anims[1].setDuration(self._animation_duration)
        self.__anims[1].setStartValue(QtCore.QPoint(next_page.x()+rest_pos, next_page.y()))
        self.__anims[1].setEndValue(QtCore.QPoint(next_page.x(), next_page.y()))
        self.__anims[1].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.__anim_grp = QtCore.QParallelAnimationGroup()
        self.__anim_grp.addAnimation(self.__anims[0])
        self.__anim_grp.addAnimation(self.__anims[1])

        # Hide the old page when the animation is finished
        # otherwise it might become visible when the window is
        # made very large
        self.__anim_grp.finished.connect( lambda : this_page.hide())

        self.__anim_grp.start()



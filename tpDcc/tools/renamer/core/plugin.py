#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base classes to create/register renaming plugins
"""

from __future__ import print_function, division, absolute_import

import re

from Qt.QtCore import Qt, Signal, QRect, QAbstractAnimation, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve
from Qt.QtWidgets import QSizePolicy, QWidget, QLabel, QGraphicsScene, QGraphicsView

from tpDcc.managers import resources
from tpDcc.libs.python import decorators
from tpDcc.libs.plugin.core import factory
from tpDcc.libs.qt.core import base, qtutils
from tpDcc.libs.qt.widgets import layouts, checkbox, buttons


@decorators.add_metaclass(decorators.Singleton)
class PluginsManager(factory.PluginFactory):

    REGEX_FOLDER_VALIDATOR = re.compile('^((?!__pycache__).)*$')

    def __init__(self):
        super(PluginsManager, self).__init__(interface=RenamerPlugin)


class RenamerPlugin(base.BaseWidget):

    ID = None
    VERSION = None

    PLUGIN_HEIGHT = 135

    closeWidget = Signal(object)
    deleteWidget = Signal(object)

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller
        self._animation = None

        super(RenamerPlugin, self).__init__(parent=parent)

        self.refresh()

    @classmethod
    def create(cls, parent):
        raise NotImplementedError()

    @classmethod
    def get_title(cls):
        return ''

    @classmethod
    def get_icon(cls):
        return resources.icon('puzzle')

    def get_main_layout(self):
        return layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))

    def ui(self):
        super(RenamerPlugin, self).ui()

        self.setFixedHeight(qtutils.dpi_scale(self.PLUGIN_HEIGHT))

        self._main_frame = base.BaseFrame(parent=self)
        self._main_frame.setFixedHeight(qtutils.dpi_scale(self.PLUGIN_HEIGHT - 30))
        self._main_frame.setStyleSheet('border-radius: 10px;')
        self.main_layout.addWidget(self._main_frame)

        self._main_widget = QWidget()
        self._main_widget.setStyleSheet('border-radius: 10px; background: transparent;')
        self._main_widget.setLayout(layouts.VerticalLayout(spacing=5, margins=(5, 5, 5, 5)))
        self._main_widget.setFixedHeight(qtutils.dpi_scale(self.PLUGIN_HEIGHT - 30))
        self._main_widget.setFixedWidth(qtutils.dpi_scale(400))
        graphics_scene = QGraphicsScene()
        graphics_view = QGraphicsView()
        graphics_view.setScene(graphics_scene)
        graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.setFocusPolicy(Qt.NoFocus)
        graphics_view.setStyleSheet('QGraphicsView {border-style: none;}')
        graphics_view.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._main_frame.main_layout.addWidget(graphics_view)
        self._main_widget_proxy = graphics_scene.addWidget(self._main_widget)
        self._main_widget.setParent(graphics_view)

        self._custom_widget = self.get_custom_widget() or QWidget()
        self._custom_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        custom_widget_layout = layouts.VerticalLayout()
        options_layout = layouts.VerticalLayout()
        options_layout.setAlignment(Qt.AlignRight)
        title_layout = layouts.HorizontalLayout()
        icon_layout = layouts.VerticalLayout()
        close_layout = layouts.HorizontalLayout()
        separator_layout = layouts.VerticalLayout()
        separator_layout.setAlignment(Qt.AlignRight)
        self._title_icon = QLabel(parent=self)
        self._title_icon.setPixmap(self.get_icon().pixmap(40))
        icon_layout.addWidget(self._title_icon)
        icon_layout.addStretch()
        self._close_btn = buttons.CloseButton('X', parent=self)
        close_layout.addStretch()
        close_layout.addWidget(self._close_btn)
        self._separator_cbx = checkbox.BaseCheckBox('Add separator?', parent=self)
        self._separator_cbx.setChecked(True)
        separator_layout.addStretch()
        separator_layout.addWidget(self._separator_cbx)

        custom_widget_layout.addLayout(icon_layout)
        options_layout.addLayout(close_layout)
        options_layout.addLayout(separator_layout)

        title_layout.addLayout(custom_widget_layout)
        title_layout.addStretch()
        title_layout.addLayout(options_layout)

        self._main_widget.layout().addLayout(title_layout)
        self._main_widget.layout().addWidget(self._custom_widget)
        self._main_widget.layout().addStretch()

    def setup_signals(self):
        self._close_btn.clicked.connect(self._on_close_widget)

    def refresh(self):
        pass

    def get_custom_widget(self):
        return QWidget()

    def update_width(self, width):
        self._main_frame.setFixedWidth(width - 8)
        self._main_widget.setFixedWidth(width - 8)

    def close_button_visible(self, flag):
        self._close_btn.setVisible(flag)

    def animate_expand(self, value):

        size_animation = QPropertyAnimation(self, b'geometry')
        geometry = self.geometry()
        width = geometry.width()
        x, y, _, _ = geometry.getCoords()
        size_start = QRect(x, y, width, int(not value) * self.PLUGIN_HEIGHT)
        size_end = QRect(x, y, width, value * self.PLUGIN_HEIGHT - 10)
        size_animation.setStartValue(size_start)
        size_animation.setEndValue(size_end)
        size_animation.setDuration(200)
        size_anim_curve = QEasingCurve()
        size_anim_curve.setType(QEasingCurve.InQuad) if value else size_anim_curve.setType(QEasingCurve.OutQuad)
        size_animation.setEasingCurve(size_anim_curve)

        opacity_animation = QPropertyAnimation(self._main_widget_proxy, b'opacity')
        opacity_animation.setStartValue(not(value))
        opacity_animation.setEndValue(value)
        opacity_animation.setDuration(100)
        opacity_anim_curve = QEasingCurve()
        opacity_anim_curve.setType(QEasingCurve.InQuad) if value else opacity_anim_curve.setType(QEasingCurve.OutQuad)
        opacity_animation.setEasingCurve(opacity_anim_curve)

        # We must store the animation objects as a member variables. Otherwise the animation object could be deleted
        # once the function is completed. In that case, the animation will not work.
        self._animation = QSequentialAnimationGroup()
        if value:
            self._main_widget_proxy.setOpacity(0)
            self._animation.addAnimation(size_animation)
            self._animation.addAnimation(opacity_animation)
        else:
            self._main_widget_proxy.setOpacity(1)
            self._animation.addAnimation(opacity_animation)
            self._animation.addAnimation(size_animation)

        # When animating geometry property, the parent layout is not updated automatically.
        # We force the resize of the layout by calling a signal each time the size animation value changes.
        size_animation.valueChanged.connect(self._on_force_resize)
        self._animation.finished.connect(self._animation.clear)

        if not value:
            self._animation.finished.connect(self._on_delete_widget)

        self._animation.start(QAbstractAnimation.DeleteWhenStopped)

    def clear_animation(self):
        self._animation = None

    def _on_force_resize(self, new_height):
        """
        Internal function that forces the resize of the parent layout of the widget
        We use the setFixedWidth function ot he widget to force its parent to reevaluate
        """

        self.setFixedHeight(new_height.height())

    def _on_close_widget(self):
        self.closeWidget.emit(self)

    def _on_delete_widget(self):
        self.deleteWidget.emit(self)

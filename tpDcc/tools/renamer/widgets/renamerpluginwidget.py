#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains plugin based renamed widget
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from Qt.QtCore import Qt
from Qt.QtWidgets import QSizePolicy, QFrame, QScrollArea, QMenu

from tpDcc.managers import resources
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, buttons, dividers

from tpDcc.tools.renamer.core import plugin


class RenamerPluginWidget(base.BaseWidget):
    def __init__(self, model, controller, parent=None):
        self._model = model
        self._controller = controller

        super(RenamerPluginWidget, self).__init__(parent=parent)

        self.refresh()

    def resizeEvent(self, event):
        super(RenamerPluginWidget, self).resizeEvent(event)
        for plugin_widget in self._model.plugin_widgets:
            plugin_widget.update_width(self.width())

    def ui(self):
        super(RenamerPluginWidget, self).ui()

        central_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        central_widget = QFrame(parent=self)
        frame_bg_color = self.palette().color(self.backgroundRole()).lighter(25)
        central_widget.setStyleSheet(
            'border-radius: 5px; background-color: rgb({}, {}, {}, 100);'.format(
                frame_bg_color.redF() * 255, frame_bg_color.greenF() * 255, frame_bg_color.blueF() * 255))
        central_widget.setLayout(central_layout)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll = QScrollArea(parent=self)
        scroll.setStyleSheet('border: 0px;')
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)
        scroll.setWidget(central_widget)

        buttons_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        self._add_plugin_button = buttons.BaseButton(parent=self)
        self._add_plugin_button.setIcon(resources.icon('plus'))
        self._add_plugin_button.setStyleSheet('QPushButton::menu-indicator{width:0px;}')
        self._plugins_menu = QMenu(parent=self)
        self._add_plugin_button.setMenu(self._plugins_menu)
        self._refresh_btn = buttons.BaseButton(parent=self)
        self._refresh_btn.setIcon(resources.icon('refresh'))
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._add_plugin_button)
        buttons_layout.addWidget(self._refresh_btn)

        self._plugins_layout = layouts.VerticalLayout(spacing=2, margins=(2, 2, 2, 2))
        self._plugins_layout.setAlignment(Qt.AlignTop)
        central_layout.addLayout(self._plugins_layout)

        self._rename_btn = buttons.BaseButton('Rename')
        self._rename_btn.setIcon(resources.icon('rename'))

        self.main_layout.addLayout(buttons_layout)
        self.main_layout.addWidget(dividers.Divider(parent=self))
        self.main_layout.addWidget(scroll)
        self.main_layout.addWidget(dividers.Divider(parent=self))
        self.main_layout.addWidget(self._rename_btn)

    def setup_signals(self):
        self._plugins_menu.aboutToShow.connect(self._on_update_menu)

        self._model.addPluginWidget.connect(self._on_add_plugin_widget)
        self._model.removePluginWidget.connect(self._on_remove_plugin_widget)

    def refresh(self):
        pass

    def _on_update_menu(self):
        self._plugins_menu.clear()
        renamer_plugins = plugin.PluginsManager().plugins()
        if not renamer_plugins:
            return

        for plugin_class in renamer_plugins:
            plugin_title = plugin_class.get_title()
            plugin_action = self._plugins_menu.addAction(plugin_title)
            plugin_action.setIcon(plugin_class.get_icon())
            plugin_action.triggered.connect(partial(self._on_add_action, plugin_class))

    def _on_add_action(self, plugin_class):
        self._controller.add_plugin_widget(plugin_class, parent=self)

    def clear(self):
        widgets = self._model.plugin_widgets
        if not widgets:
            return
        for plugin_widget in widgets:
            self._controller.remove_plugin_widget(plugin_widget)

    def _on_add_plugin_widget(self, plugin_widget):
        self._plugins_layout.addWidget(plugin_widget)
        plugin_widget.closeWidget.connect(self._controller.remove_plugin_widget)
        plugin_widget.setFixedHeight(0)
        plugin_widget.animate_expand(True)
        plugin_widget.update_width(self.width())

    def _on_remove_plugin_widget(self, plugin_widget):
        plugin_widget.deleteWidget.connect(self._on_delete)
        plugin_widget.animate_expand(False)

    def _on_delete(self, plugin_widget):
        self._plugins_layout.removeWidget(plugin_widget)
        plugin_widget.clear_animation()
        # plugin_widget.deleteLater()


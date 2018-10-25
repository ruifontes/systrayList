# -*- coding: utf-8 -*-
# List of SysTray elements - Global Plugin for NVDA
# Authors:
# Rui Fontes <rui.fontes@tiflotecnia.com>
# Rui Batista <ruiandrebatista@gmail.com>
# Masamitsu Misono <misono@nvsupport.org>
# Joseph Lee <joseph.lee22590@gmail.com>
# Shortcut: NVDA+f11
# Copyright 2013-2017, released under GPL.

import os.path
import wx
import globalPluginHandler
import globalVars
import scriptHandler
import NVDAObjects
import winUser
import gui
import addonHandler
_addonDir = os.path.join(os.path.dirname(__file__), "..", "..").decode("mbcs")
_curAddon = addonHandler.Addon(_addonDir)
_addonSummary = _curAddon.manifest['summary']
addonHandler.initTranslation()
CENTER_ON_SCREEN = wx.CENTER_ON_SCREEN if hasattr(wx,"CENTER_ON_SCREEN") else 2

def mouseEvents(location, *events):
	x,y = int (location[0]+location[2]/2), int (location[1]+location[3]/2)
	#move the cursor
	winUser.setCursorPos (x,y)
	#simulation of pressing mouse button
	for event in events:
		winUser.mouse_event(event, 0, 0, None, None)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = unicode(_addonSummary)

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		# The dialog instance is initially None.
		# We only create it the first time the script is called.
		self._systrayListDialog = None

	def terminate(self):
		# Destroy the window on plugin deletion just to make sure it goes away
		# (to prevent strange things when reloading plugin)
		try:
			if not self._systrayListDialog:
				self._systrayListDialog.Destroy()
		except (AttributeError, RuntimeError):
			pass

	def _findAccessibleLeafsFromWindowClassPath(self, windowClassPath):
		# Create a list of (obj.name, obj.location)
		h, FindWindowEx =0, winUser.user32.FindWindowExW
		for element in windowClassPath:
			h = FindWindowEx(h,0,element,0)
		l = []
		o = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,1)
		# When o.next is None it means that there is no more objects on the systray.
		while o is not None:
			l.append((o.name, o.location))
			o = o.next
		return l

	def script_createList(self, gesture):
		if scriptHandler.getLastScriptRepeatCount() == 0:
			self._createSystrayList()
		else:
			self._createTaskList()
	# Translators: Input help mode message for system tray list command.
	script_createList.__doc__ = _(u"Shows the list of buttons on the System Tray. If pressed twice quickly, shows the items on the taskbar.")

	def _createSystrayList(self):
		path = (u"shell_TrayWnd", u"TrayNotifyWnd", u"SysPager", u"ToolbarWindow32")
		objects = self._findAccessibleLeafsFromWindowClassPath(path)
		self._createObjectsWindow(objects, _("System Tray List"), _("Icons on the System Tray:"))

	def _createTaskList(self):
		objects = self._findAccessibleLeafsFromWindowClassPath((u"Shell_TrayWnd", u"RebarWindow32", u"MSTaskSwWClass", u"MSTaskListWClass") ,)
		if not objects:
			# Probably on XP; try this instead:
			objects = self._findAccessibleLeafsFromWindowClassPath((u"Shell_TrayWnd", u"RebarWindow32", u"MSTaskSwWClass", u"ToolbarWindow32"),)
		self._createObjectsWindow(objects, _("Taskbar List"), _("Icons of running applications on the taskbar:"))

	def _createObjectsWindow(self, objects, title, label):
		if globalVars.appArgs.secure:
			return
		# If this is the first call create the Window
		if not self._systrayListDialog:
			self._systrayListDialog = SystrayListDialog(gui.mainFrame, objects)
		# Update the list in the dialog
		self._systrayListDialog.updateSystray(objects, title, label)
		# Show the window if it is hidden
		if not self._systrayListDialog.IsShown():
			gui.mainFrame.prePopup()
			self._systrayListDialog.Show()
			gui.mainFrame.postPopup()

	__gestures={
		"kb:NVDA+f11": "createList",
	}


class SystrayListDialog(wx.Dialog):
	def __init__(self, parent, systray, title=""):
		self.systray = systray
		super(SystrayListDialog, self).__init__(parent, title=title)
		# Create interface
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		tasksSizer = wx.BoxSizer(wx.VERTICAL)
		# Create a label and a list view for systray entries
		# Label is above the list view.
		self.tasksLabel = wx.StaticText(self, -1)
		tasksSizer.Add(self.tasksLabel)
		self.listBox = wx.ListBox(self, wx.NewIdRef() if wx.version().startswith("4") else wx.NewId(), style=wx.LB_SINGLE, size=(550, 250))
		tasksSizer.Add(self.listBox, proportion=8)
		mainSizer.Add(tasksSizer)
		# Create buttons.
		# Buttons are in a horizontal row
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		leftClickButtonID = wx.NewIdRef() if wx.version().startswith("4") else wx.NewId()
		# Translators: A button on the system tray list dialog to perform left mouse click.
		leftClickButton = wx.Button(self, leftClickButtonID, _("&Left Click"))
		buttonsSizer.Add(leftClickButton)
		leftDoubleClickButtonID = wx.NewIdRef() if wx.version().startswith("4") else wx.NewId()
		# Translators: A button in the system tray list dialog to perform left double mouse click.
		leftDoubleClickButton = wx.Button(self, leftDoubleClickButtonID, _("Left &Double Click"))
		buttonsSizer.Add(leftDoubleClickButton)
		rightClickButtonID = wx.NewIdRef() if wx.version().startswith("4") else wx.NewId()
		# Translators: A button in the system tray list dialog to perform right mouse click.
		rightClickButton = wx.Button(self, rightClickButtonID, _("&Right Click"))
		buttonsSizer.Add(rightClickButton)
		cancelButton = wx.Button(self, wx.ID_CANCEL)
		buttonsSizer.Add(cancelButton)
		# Bind the buttons to perform mouse clicks
		# The `makeBindingClicFunction just returns a function
		# that performs the passed events. Functional programming at its best.
		# Except for Cancel button that should destory this dialog.
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP), id=leftClickButtonID)
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP, winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP), id=leftDoubleClickButtonID)
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_RIGHTDOWN, winUser.MOUSEEVENTF_RIGHTUP), id=rightClickButtonID)
		self.Bind(wx.EVT_BUTTON,self.onClose,id=wx.ID_CANCEL)
		mainSizer.Add(buttonsSizer)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		rightClickButton.SetDefault()
		self.Center(wx.BOTH | CENTER_ON_SCREEN)

	def onClose(self, evt):
		self.Destroy()

	def makeBindingClickFunction(self, *events):
		def func(event):
			self.Destroy
			index = self.listBox.GetSelections()
			if index is not None:
				location = self.systray[index[0]][1]
				mouseEvents(location, *events)
			self.Hide()
		return func

	def updateSystray(self, systray, title, label):
		# Clear the label, otherwise a jumble of labels will be shown on screen and via screen review.
		self.tasksLabel.SetLabel("")
		self.SetTitle(title)
		self.tasksLabel.SetLabel(label)
		self.systray = systray
		self.listBox.SetItems([obj[0] for obj in self.systray])
		self.listBox.Select(0)
		self.listBox.SetFocus()

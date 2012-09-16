# -*- coding: utf-8 -*-
# List of SysTray elements - Global Plugin for NVDA
# Authors:
# Rui Fontes <rui.fontes@tiflotecnia.com>
# Rui Batista <ruiandrebatista@gmail.com>
# Shortcut: NVDA+f11

import ctypes
import gettext
import languageHandler
import os.path
import wx
import globalPluginHandler,IAccessibleHandler
import globalVars
import scriptHandler
import NVDAObjects
from api import getFocusObject
import winUser
import gui
import addonHandler
addonHandler.initTranslation()

def mouseEvents(location, *events):
	x,y = int (location[0]+location[2]/2), int (location[1]+location[3]/2)
	#move the cursor
	winUser.setCursorPos (x,y)
	#simulation of pressing mouse button
	for event in events:
		winUser.mouse_event(event, 0, 0, None, None)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()
			# The dialog instance is initialy None.
			# We only create it on the first time the script is called.
		self._systrayListDialog = None

	def __del__(self):
		# Destroy the window on plugin deletion just for making sure it goes away
		# (to prevent strange things on plugin realoading)
		if self._systrayListDialog is not None:
			self._systrayListDialog.Destroy()

	def _findAccessibleLeafsFromWindowClassPath(self, windowClassPath):
		# Create a list of (obj.name, obj.location)
		h,FindWindowExA =0,ctypes.windll.user32.FindWindowExA
		for element in windowClassPath:
			h = FindWindowExA(h,0,element,0)
		l = []
		o = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,1)
		# When o.next is None it means that there is no more objects on the systray.
		while o is not None:
			l.append((o.name, o.location))
			o = o.next
		return l


	def script_createSystrayList(self, gesture):
		path = ("shell_TrayWnd","TrayNotifyWnd","SysPager","ToolbarWindow32")
		objects = self._findAccessibleLeafsFromWindowClassPath(path)
		self._createObjectsWindow(objects, _("System Notification Area"), _("Icons of systrem tray items in the windows notification area:"))

	def script_createTaskList(self, gesture):
		objects = self._findAccessibleLeafsFromWindowClassPath(("Shell_TrayWnd","RebarWindow32","MSTaskSwWClass","MSTaskListWClass") ,)
		if not objects:
			# Probably on XP; try this instea:
			objects = self._findAccessibleLeafsFromWindowClassPath(("Shell_TrayWnd","RebarWindow32","MSTaskSwWClass","ToolbarWindow32"),)
		self._createObjectsWindow(objects, _("Running Applications List"), _("Icons of running applications in the task bar"))

	def _createObjectsWindow(self, objects, title, label):
		if globalVars.appArgs.secure:
			return
		# If this is the first call create the Window
		if not self._systrayListDialog:
			self._systrayListDialog = SystrayListDialog(gui.mainFrame, objects)
		# Update the list on the dialog
		self._systrayListDialog.updateSystray(objects, title, label)
		# Show the window if it is Hiden
		if not self._systrayListDialog.IsShown():
			gui.mainFrame.prePopup()
			self._systrayListDialog.Show()
			self._systrayListDialog.Centre()
			gui.mainFrame.postPopup()

	# Documentation
	script_createSystrayList.__doc__ = _(u"Shows the list of buttons on the System Tray")
	script_createTaskList.__doc___ = _("Shows the list of icons in the task bar")

	__gestures={
	"kb:NVDA+shift+f11": "createTaskList",
		"kb:NVDA+f11": "createSystrayList",
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
		self.tasksLabel = wx.StaticText(self, -1, label="")
		tasksSizer.Add(self.tasksLabel)
		self.listBox = wx.ListBox(self, wx.NewId(), style=wx.LB_SINGLE, size=(550, 250))
		tasksSizer.Add(self.listBox, proportion=8)
		mainSizer.Add(tasksSizer)
		# Create buttons.
		# Buttons are in a horizontal row
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		leftClickButtonID = wx.NewId()
		leftClickButton = wx.Button(self, leftClickButtonID, _("&Left Click"))
		buttonsSizer.Add(leftClickButton)
		leftDoubleClickButtonID = wx.NewId()
		leftDoubleClickButton = wx.Button(self, leftDoubleClickButtonID, _("Left &Double Click"))
		buttonsSizer.Add(leftDoubleClickButton)
		rightClickButtonID = wx.NewId()
		rightClickButton = wx.Button(self, leftClickButtonID, _("&Right Click"))
		buttonsSizer.Add(rightClickButton)
		cancelButton = wx.Button(self, wx.ID_CANCEL)
		buttonsSizer.Add(cancelButton)
		# Bind the buttons to perform mouse clicks
		# The `makeBindingClicFunction just returns a function
		# that performs the passed events. Functional programming at its best.
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP), id=leftClickButtonID)
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP, winUser.MOUSEEVENTF_LEFTDOWN, winUser.MOUSEEVENTF_LEFTUP), id=leftDoubleClickButtonID)
		self.Bind( wx.EVT_BUTTON, self.makeBindingClickFunction(winUser.MOUSEEVENTF_RIGHTDOWN, winUser.MOUSEEVENTF_RIGHTUP), id=leftClickButtonID)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		rightClickButton.SetDefault()

	def makeBindingClickFunction(self, *events):
		def func(event):
			index = self.listBox.GetSelections()
			if index is not None:
				location = self.systray[index[0]][1]
				mouseEvents(location, *events)
			self.Hide()
		return func

	def updateSystray(self, systray, title, label):
		self.SetTitle(title)
		self.tasksLabel.SetLabel(label)
		self.systray = systray
		self.listBox.SetItems([obj[0] for obj in self.systray])
		self.listBox.Select(0)
		self.listBox.SetFocus()

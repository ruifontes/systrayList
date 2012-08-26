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

	def script_createSystrayList(self, gesture):
		if globalVars.appArgs.secure:
			return
		# Create a list of (obj.name, obj.location)
		# from the systray.
		# This runs through the window hierarchy finding 
		# the first object on the path represented by l
		# l is a list of windowClassNames.
		l=("shell_TrayWnd","TrayNotifyWnd","SysPager","ToolbarWindow32")
		
		h,FindWindowExA =0,ctypes.windll.user32.FindWindowExA
		for element in l:
			h = FindWindowExA(h,0,element,0)

		systray = []
		o = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,1)
		# When o.next is None it means that there is no more objects on the systray.
		while o is not None:
			systray.append((o.name, o.location))
			o = o.next

		# If this is the first call create the Window
		if not self._systrayListDialog:
			self._systrayListDialog = SystrayListDialog(gui.mainFrame, systray)
		# Update the list on the dialog
		self._systrayListDialog.updateSystray(systray)
		# Show the window if it is Hiden
		if not self._systrayListDialog.IsShown():
			gui.mainFrame.prePopup()
			self._systrayListDialog.Show()
			self._systrayListDialog.Centre()
			gui.mainFrame.postPopup()

	# Documentation
	script_createSystrayList.__doc__ = _(u"Shows the list of buttons on the System Tray")

	__gestures={
		"kb:NVDA+f11": "createSystrayList",
	}


class SystrayListDialog(wx.Dialog):
	def __init__(self, parent, systray, title=_("System Tray List")):
		self.systray = systray
		super(SystrayListDialog, self).__init__(parent, title=title)
		# Create interface
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		tasksSizer = wx.BoxSizer(wx.VERTICAL)
		# Create a label and a list view for systray entries
		# Label is above the list view.
		tasksLabel = wx.StaticText(self, -1, label=_("Icons on the System Tray:"))
		tasksSizer.Add(tasksLabel)
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

	def updateSystray(self, systray):
		self.systray = systray
		self.listBox.SetItems([obj[0] for obj in self.systray])
		self.listBox.Select(0)
		self.listBox.SetFocus()

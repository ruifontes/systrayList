import webbrowser
import wx
import addonHandler
addonHandler.initTranslation()
import gui
import languageHandler

DONATIONS_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=STUTSNJNVT752&lc={lang}&item_name=NVDA%20systrayList%20donations&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted".format(lang=languageHandler.getLanguage().split("_")[0].upper())
def onInstall():
	manifest = addonHandler.getCodeAddon().manifest
	message = _(""" {name} is a free add-on for NVDA.
You can make a donation to its author to suport further developments of this add-on and other free software products.
Do you want to donate now? (you will be redirected to the Paypal website).""").format(**manifest)
	if gui.messageBox(message, caption=_("Request for Contributions to {name}").format(name=manifest['name']),
		style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
		webbrowser.open(DONATIONS_URL)
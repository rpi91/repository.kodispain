################################################################################
#      Copyright (C) 2015 Surfacingx                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import uservar
from datetime import date, datetime, timedelta
from resources.libs import extract, downloader, notify, loginit, debridit, traktit, skinSwitch, uploadLog, wizard as wiz

ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = wiz.addonId(ADDON_ID)
VERSION        = wiz.addonInfo(ADDON_ID,'version')
ADDONPATH      = wiz.addonInfo(ADDON_ID,'path')
ADDONID        = wiz.addonInfo(ADDON_ID,'id')
DIALOG         = xbmcgui.Dialog()
DP             = xbmcgui.DialogProgress()
HOME           = xbmc.translatePath('special://home/')
PROFILE        = xbmc.translatePath('special://profile/')
KODIHOME       = xbmc.translatePath('special://xbmc/')
ADDONS         = os.path.join(HOME,     'addons')
KODIADDONS     = os.path.join(KODIHOME, 'addons')
USERDATA       = os.path.join(HOME,     'userdata')
PLUGIN         = os.path.join(ADDONS,   ADDON_ID)
PACKAGES       = os.path.join(ADDONS,   'packages')
ADDONDATA      = os.path.join(USERDATA, 'addon_data', ADDON_ID)
TEXTCACHE      = os.path.join(ADDONDATA, 'Cache')
FANART         = os.path.join(ADDONPATH,'fanart.jpg')
ICON           = os.path.join(ADDONPATH,'icon.png')
ART            = os.path.join(ADDONPATH,'resources', 'art')
ADVANCED       = os.path.join(USERDATA, 'advancedsettings.xml')
SKIN           = xbmc.getSkinDir()
BUILDNAME      = wiz.getS('buildname')
DEFAULTSKIN    = wiz.getS('defaultskin')
DEFAULTNAME    = wiz.getS('defaultskinname')
DEFAULTIGNORE  = wiz.getS('defaultskinignore')
BUILDVERSION   = wiz.getS('buildversion')
BUILDLATEST    = wiz.getS('latestversion')
BUILDCHECK     = wiz.getS('lastbuildcheck')
DISABLEUPDATE  = wiz.getS('disableupdate')
AUTOCLEANUP    = wiz.getS('autoclean')
AUTOCACHE      = wiz.getS('clearcache')
AUTOPACKAGES   = wiz.getS('clearpackages')
AUTOTHUMBS     = wiz.getS('clearthumbs')
AUTOFEQ        = wiz.getS('autocleanfeq')
AUTONEXTRUN    = wiz.getS('nextautocleanup')
TRAKTSAVE      = wiz.getS('traktlastsave')
REALSAVE       = wiz.getS('debridlastsave')
LOGINSAVE      = wiz.getS('loginlastsave')
KEEPTRAKT      = wiz.getS('keeptrakt')
KEEPREAL       = wiz.getS('keepdebrid')
KEEPLOGIN      = wiz.getS('keeplogin')
INSTALLED      = wiz.getS('installed')
EXTRACT        = wiz.getS('extract')
EXTERROR       = wiz.getS('errors')
NOTIFY         = wiz.getS('notify')
NOTEDISMISS    = wiz.getS('notedismiss')
NOTEID         = wiz.getS('noteid')
BACKUPLOCATION = ADDON.getSetting('path') if not ADDON.getSetting('path') == '' else HOME
MYBUILDS       = os.path.join(BACKUPLOCATION, 'My_Builds', '')
NOTEID         = 0 if NOTEID == "" else int(NOTEID)
AUTOFEQ        = int(AUTOFEQ) if AUTOFEQ.isdigit() else 0
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
TWODAYS        = TODAY + timedelta(days=2)
THREEDAYS      = TODAY + timedelta(days=3)
ONEWEEK        = TODAY + timedelta(days=7)
SKINCHECK      = ['skin.aftermath.zephyr', 'skin.aftermath.silvo', 'skin.aftermath.simple', 'skin.ccm.aftermath']
RAM            = int(xbmc.getInfoLabel("System.Memory(total)")[:-2])
KODIV          = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
EXCLUDES       = uservar.EXCLUDES
BUILDFILE      = uservar.BUILDFILE
UPDATECHECK    = uservar.UPDATECHECK if str(uservar.UPDATECHECK).isdigit() else 1
NEXTCHECK      = TODAY + timedelta(days=UPDATECHECK)
NOTIFICATION   = uservar.NOTIFICATION
ENABLE         = uservar.ENABLE
HEADERMESSAGE  = uservar.HEADERMESSAGE
AUTOUPDATE     = uservar.AUTOUPDATE
WIZARDFILE     = uservar.WIZARDFILE
AUTOINSTALL    = uservar.AUTOINSTALL
REPOID         = uservar.REPOID
REPOADDONXML   = uservar.REPOADDONXML
REPOZIPURL     = uservar.REPOZIPURL
COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
WORKING        = True if wiz.workingURL(BUILDFILE) == True else False
FAILED         = False

###########################
#### Check Updates   ######
###########################
def checkUpdate():
	BUILDNAME      = wiz.getS('buildname')
	BUILDVERSION   = wiz.getS('buildversion')
	bf             = wiz.textCache(BUILDFILE)
	if bf == False: return
	link           = bf.replace('\n','').replace('\r','').replace('\t','')
	match          = re.compile('name="%s".+?ersion="(.+?)".+?con="(.+?)".+?anart="(.+?)"' % BUILDNAME).findall(link)
	if len(match) > 0:
		version = match[0][0]
		icon    = match[0][1]
		fanart  = match[0][2]
		wiz.setS('latestversion', version)
		if version > BUILDVERSION:
			if DISABLEUPDATE == 'false':
				wiz.log("[Comprobacion de Actualizaciones] [Version Instalada: %s] [Version Actual: %s] Abriendo Ventana de Actualizacion" % (BUILDVERSION, version), xbmc.LOGNOTICE)
				notify.updateWindow(BUILDNAME, BUILDVERSION, version, icon, fanart)
			else: wiz.log("[Comprobacion de Actualizaciones] [Version Instalada: %s] [Version Actual: %s] Ventana de Actualizacion Desactivada" % (BUILDVERSION, version), xbmc.LOGNOTICE)
		else: wiz.log("[Comprobacion de Actualizaciones] [Version Instalada: %s] [Version Actual: %s]" % (BUILDVERSION, version), xbmc.LOGNOTICE)
	else: wiz.log("[Comprobacion de Actualizaciones] ERROR: No se pudo encontrar la version de compilacion en build.txt", xbmc.LOGERROR)

def checkInstalled():
	current = ''
	for skin in SKINCHECK:
		skinpath = os.path.join(ADDONS,skin)
		if os.path.exists(skinpath):
			current = skin
	if current == SKINCHECK[0]:
		yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR dodgerblue]Aftermath[/COLOR] Zephyr is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
		if yes_pressed:	xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
		else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR dodgerblue]Aftermath[/COLOR] Wizard.')
	elif current == SKINCHECK[1]:
		yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR dodgerblue]Aftermath[/COLOR] Silvo is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
		if yes_pressed:	xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
		else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR dodgerblue]Aftermath[/COLOR] Wizard.')
	elif current == SKINCHECK[2]:
		if KODIV >= 16:
			gui   = os.path.join(ADDOND, SKINCHECK[2], 'settings.xml')
			f     = open(gui,mode='r'); g = f.read(); f.close()
			match = re.compile('<setting id=\"SubSettings.3.Label\" type=\"string\">(.+?)<\/setting>').findall(g)
			if len(match):
				name, build, ver = match[0].replace('[COLOR dodgerblue]','').replace('[/COLOR]','').split(' ')
			else:
				build = "Simple"
				ver = "v0.1"
		else:
			gui   = os.path.join(USERDATA,'guisettings.xml')
			f     = open(gui,mode='r'); g = f.read(); f.close()
			match = re.compile('<setting type=\"string\" name=\"skin.aftermath.simple.SubSettings.3.Label\">(.+?)<\/setting>').findall(g)
			name, build, ver = match[0].replace('[COLOR dodgerblue]','').replace('[/COLOR]','').split(' ')
		wiz.setS('buildname', 'Aftermath %s' % build)
		wiz.setS('buildversion', ver[1:])
		wiz.setS('lastbuildcheck', str(NEXTCHECK))
		checkUpdate()
	elif current == SKINCHECK[3]:
		yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR dodgerblue]Aftermath[/COLOR] CCM is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
		if yes_pressed:	xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
		else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR dodgerblue]Aftermath[/COLOR] Wizard.')
	else:
		notify.firstRunSettings()
		notify.firstRun()

def writeAdvanced():
	if RAM > 1536: buffer = '209715200'
	else: buffer = '104857600'
	with open(ADVANCED, 'w+') as f:
		f.write('<advancedsettings>\n')
		f.write('	<network>\n')
		f.write('		<buffermode>2</buffermode>\n')
		f.write('		<cachemembuffersize>%s</cachemembuffersize>\n' % buffer)
		f.write('		<readbufferfactor>5</readbufferfactor>\n')
		f.write('		<curlclienttimeout>10</curlclienttimeout>\n')
		f.write('		<curllowspeedtime>10</curllowspeedtime>\n')
		f.write('	</network>\n')
		f.write('</advancedsettings>\n')
	f.close()

def checkSkin():
	wiz.log("[Build Check] Invalid Skin Check Start")
	DEFAULTSKIN   = wiz.getS('defaultskin')
	DEFAULTNAME   = wiz.getS('defaultskinname')
	DEFAULTIGNORE = wiz.getS('defaultskinignore')
	gotoskin = False
	if not DEFAULTSKIN == '':
		if os.path.exists(os.path.join(ADDONS, DEFAULTSKIN)):
			if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Would you like to set the skin back to:[/COLOR]", '[COLOR %s]%s[/COLOR]' % (COLOR1, DEFAULTNAME)):
				gotoskin = DEFAULTSKIN
				gotoname = DEFAULTNAME
			else: wiz.log("Skin was not reset", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
		else: wiz.setS('defaultskin', ''); wiz.setS('defaultskinname', ''); DEFAULTSKIN = ''; DEFAULTNAME = ''
	if DEFAULTSKIN == '':
		skinname = []
		skinlist = []
		for folder in glob.glob(os.path.join(ADDONS, 'skin.*/')):
			xml = "%s/addon.xml" % folder
			if os.path.exists(xml):
				f  = open(xml,mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
				match  = wiz.parseDOM(g, 'addon', ret='id')
				match2 = wiz.parseDOM(g, 'addon', ret='name')
				wiz.log("%s: %s" % (folder, str(match[0])), xbmc.LOGNOTICE)
				if len(match) > 0: skinlist.append(str(match[0])); skinname.append(str(match2[0]))
				else: wiz.log("ID not found for %s" % folder, xbmc.LOGNOTICE)
			else: wiz.log("ID not found for %s" % folder, xbmc.LOGNOTICE)
		if len(skinlist) > 0:
			if len(skinlist) > 1:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Would you like to view a list of avaliable skins?[/COLOR]"):
					choice = DIALOG.select("Select skin to switch to", skinname)
					if choice == -1: wiz.log("Skin was not reset", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
					else:
						gotoskin = skinlist[choice]
						gotoname = skinname[choice]
				else: wiz.log("Skin was not reset", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
			else:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Would you like to set the skin back to:[/COLOR]", '[COLOR %s]%s[/COLOR]' % (COLOR1, skinname[0])):
					gotoskin = skinlist[0]
					gotoname = skinname[0]
				else: wiz.log("Skin was not reset", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
		else: wiz.log("No skins found in addons folder.", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
	if gotoskin:
		if wiz.swapSkins(gotoskin):
			wiz.lookandFeelData('restore')
	wiz.log("[Build Check] Invalid Skin Check End", xbmc.LOGNOTICE)

while xbmc.Player().isPlayingVideo():
	xbmc.sleep(1000)

if KODIV >= 17:
	NOW = datetime.now()
	temp = wiz.getS('kodi17iscrap')
	if not temp == '':
		if temp > str(NOW - timedelta(minutes=2)):
			wiz.log("Killing Start Up Script")
			sys.exit()
	wiz.log("%s" % (NOW))
	wiz.setS('kodi17iscrap', str(NOW))
	xbmc.sleep(1000)
	if not wiz.getS('kodi17iscrap') == str(NOW):
		wiz.log("Killing Start Up Script")
		sys.exit()
	else:
		wiz.log("Continuing Start Up Script")

wiz.log("[Path Check] Started", xbmc.LOGNOTICE)
path = os.path.split(ADDONPATH)
if not ADDONID == path[1]: DIALOG.ok(ADDONTITLE, '[COLOR %s]Please make sure that the plugin folder is the same as the ADDON_ID.[/COLOR]' % COLOR2, '[COLOR %s]Plugin ID:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, ADDONID), '[COLOR %s]Plugin Folder:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, path)); wiz.log("[Path Check] ADDON_ID and plugin folder doesnt match. %s / %s " % (ADDONID, path))
else: wiz.log("[Path Check] Good", xbmc.LOGNOTICE)

if KODIADDONS in ADDONPATH:
	wiz.log("Copiando ruta a directorio de addons", xbmc.LOGNOTICE)
	if not os.path.exists(ADDONS): os.makedirs(ADDONS)
	newpath = xbmc.translatePath(os.path.join('special://home/addons/', ADDONID))
	if os.path.exists(newpath):
		wiz.log("Ya existe la carpeta, limpiando directorio", xbmc.LOGNOTICE)
		wiz.cleanHouse(newpath)
		wiz.removeFolder(newpath)
	try:
		wiz.copytree(ADDONPATH, newpath)
	except Exception, e:
		pass
	wiz.forceUpdate(True)

try:
	mybuilds = xbmc.translatePath(MYBUILDS)
	if not os.path.exists(mybuilds): xbmcvfs.mkdirs(mybuilds)
except:
	pass

wiz.log("Flushing Aged Cached Text Files")
wiz.flushOldCache()

wiz.log("[Auto Install Repo] Iniciado", xbmc.LOGNOTICE)
if AUTOINSTALL == 'Si' and not os.path.exists(os.path.join(ADDONS, REPOID)):
	workingxml = wiz.workingURL(REPOADDONXML)
	if workingxml == True:
		ver = wiz.parseDOM(wiz.openURL(REPOADDONXML), 'addon', ret='version', attrs = {'id': REPOID})
		if len(ver) > 0:
			installzip = '%s-%s.zip' % (REPOID, ver[0])
			workingrepo = wiz.workingURL(REPOZIPURL+installzip)
			if workingrepo == True:
				DP.create(ADDONTITLE,'Descargando Repo...','', 'Por favor, espera')
				if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
				lib=os.path.join(PACKAGES, installzip)
				try: os.remove(lib)
				except: pass
				downloader.download(REPOZIPURL+installzip,lib, DP)
				extract.all(lib, ADDONS, DP)
				try:
					f = open(os.path.join(ADDONS, REPOID, 'addon.xml'), mode='r'); g = f.read(); f.close()
					name = wiz.parseDOM(g, 'addon', ret='name', attrs = {'id': REPOID})
					wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name[0]), "[COLOR %s]Addon Actualizado[/COLOR]" % COLOR2, icon=os.path.join(ADDONS, REPOID, 'icon.png'))
				except:
					pass
				if KODIV >= 17: wiz.addonDatabase(REPOID, 1)
				DP.close()
				xbmc.sleep(500)
				wiz.forceUpdate(True)
				wiz.log("[Auto Install Repo] Instalado Correctamente", xbmc.LOGNOTICE)
			else:
				wiz.LogNotify("[COLOR %s]Error al Instalar Repo[/COLOR]" % COLOR1, "[COLOR %s]URL invalida para zip[/COLOR]" % COLOR2)
				wiz.log("[Auto Install Repo] No se pudo crear una URL adecuada para el repositorio %s" % workingrepo, xbmc.LOGERROR)
		else:
			wiz.log("URL incorrecta para Repo Zip", xbmc.LOGERROR)
	else:
		wiz.LogNotify("[COLOR %s]Error de Instalacion de Repo[/COLOR]" % COLOR1, "[COLOR %s]Archivo addon.xml no valido[/COLOR]" % COLOR2)
		wiz.log("[Auto Install Repo] No se puede leer el archivo addon.xml.", xbmc.LOGERROR)
elif not AUTOINSTALL == 'Yes': wiz.log("[Auto Install Repo] No disponible", xbmc.LOGNOTICE)
elif os.path.exists(os.path.join(ADDONS, REPOID)): wiz.log("[Auto Install Repo] Repositorio ya instalado")

wiz.log("[Auto Update Wizard] Iniciado", xbmc.LOGNOTICE)
if AUTOUPDATE == 'Yes':
	wiz.wizardUpdate('startup')
else: wiz.log("[Auto Update Wizard] Inhabilitado", xbmc.LOGNOTICE)

wiz.log("[Notifications] Iniciado", xbmc.LOGNOTICE)
if ENABLE == 'Yes':
	if not NOTIFY == 'true':
		url = wiz.workingURL(NOTIFICATION)
		if url == True:
			id, msg = wiz.splitNotify(NOTIFICATION)
			if not id == False:
				try:
					id = int(id); NOTEID = int(NOTEID)
					if id == NOTEID:
						if NOTEDISMISS == 'false':
							notify.notification(msg)
						else: wiz.log("[Notifications] id[%s] Rechazado" % int(id), xbmc.LOGNOTICE)
					elif id > NOTEID:
						wiz.log("[Notifications] id: %s" % str(id), xbmc.LOGNOTICE)
						wiz.setS('noteid', str(id))
						wiz.setS('notedismiss', 'false')
						notify.notification(msg=msg)
						wiz.log("[Notifications] Completo", xbmc.LOGNOTICE)
				except Exception, e:
					wiz.log("Error on Notifications Window: %s" % str(e), xbmc.LOGERROR)
			else: wiz.log("[Notifications] Archivo de texto no formateado correctamente")
		else: wiz.log("[Notifications] URL(%s): %s" % (NOTIFICATION, url), xbmc.LOGNOTICE)
	else: wiz.log("[Notifications] Apagado", xbmc.LOGNOTICE)
else: wiz.log("[Notifications] No disponible", xbmc.LOGNOTICE)

wiz.log("[Installed Check] Iniciado", xbmc.LOGNOTICE)
if INSTALLED == 'true':
	if KODIV >= 17:
		wiz.kodi17Fix()
		if SKIN in ['skin.confluence', 'skin.estuary']:
			checkSkin()
		FAILED = True
	elif not EXTRACT == '100' and not BUILDNAME == "":
		wiz.log("[Installed Check] La Build fue extraida %s/100 con [ERRORS: %s]" % (EXTRACT, EXTERROR), xbmc.LOGNOTICE)
		yes=DIALOG.yesno(ADDONTITLE, '[COLOR %s]%s[/COLOR] [COLOR %s]no fue instalado correctamente' % (COLOR1, COLOR2, BUILDNAME), 'Instalado: [COLOR %s]%s[/COLOR] / Error Count: [COLOR %s]%s[/COLOR]' % (COLOR1, EXTRACT, COLOR1, EXTERROR), 'Le gustaria volver a intentarlo?[/COLOR]', nolabel='[B]No, gracias[/B]', yeslabel='[B]Reinstalar[/B]')
		wiz.clearS('build')
		FAILED = True
		if yes:
			wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=fresh)" % (ADDON_ID, urllib.quote_plus(BUILDNAME)))
			wiz.log("[Installed Check] Nueva instalacion reactivada", xbmc.LOGNOTICE)
		else: wiz.log("[Installed Check] Reinstalar ignorado")
	elif SKIN in ['skin.confluence', 'skin.estuary']:
		wiz.log("[Installed Check] Skin incorrecto: %s" % SKIN, xbmc.LOGNOTICE)
		defaults = wiz.getS('defaultskin')
		if not defaults == '':
			if os.path.exists(os.path.join(ADDONS, defaults)):
				if wiz.swapSkins(defaults):
					wiz.lookandFeelData('restore')
		if not wiz.currSkin() == defaults and not BUILDNAME == "":
			gui = wiz.checkBuild(BUILDNAME, 'gui')
			FAILED = True
			if gui == 'http://':
				wiz.log("[Installed Check] Guifix fue puesto en http://", xbmc.LOGNOTICE)
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Parece que la configuracion del skin no se aplico correctamente." % COLOR2, "Lamentablemente la build no dispone de un gui fix", "Debe volver a instalar la build y asegurarse de hacer un cierre forzado[/COLOR]")
			elif wiz.workingURL(gui):
				yes=DIALOG.yesno(ADDONTITLE, '%s was not installed correctly' % BUILDNAME, 'It looks like the skin settings was not applied to the build.', 'Would you like to apply the GuiFix?', nolabel='[B]No, cancelar[/B]', yeslabel='[B]Aplicar Fix[/B]')
				if yes: wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=gui)" % (ADDON_ID, urllib.quote_plus(BUILDNAME))); wiz.log("[Installed Check] Guifix intentando instalar")
				else: wiz.log('[Installed Check] Guifix url funcionando pero cancelada: %s' % gui, xbmc.LOGNOTICE)
			else:
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Parece que la configuracion del skin no se aplico correctamente." % COLOR2, "Lamentablemente la build no dispone de un gui fix", "Debe volver a instalar la build y asegurarse de hacer un cierre forzado[/COLOR]")
				wiz.log('[Installed Check] Guifix url no funciona: %s' % gui, xbmc.LOGNOTICE)
	else:
		wiz.log('[Installed Check] La instalacion parece haberse completado correctamente', xbmc.LOGNOTICE)
	if not wiz.getS('pvrclient') == "":
		wiz.toggleAddon(wiz.getS('pvrclient'), 1)
		wiz.ebi('StartPVRManager')
	wiz.addonUpdates('reset')
	if KEEPTRAKT == 'true': traktit.traktIt('restore', 'all'); wiz.log('[Installed Check] Restaurando Datos de Trakt', xbmc.LOGNOTICE)
	if KEEPREAL  == 'true': debridit.debridIt('restore', 'all'); wiz.log('[Installed Check] Restaurando Datos de Real Debrid', xbmc.LOGNOTICE)
	if KEEPLOGIN == 'true': loginit.loginIt('restore', 'all'); wiz.log('[Installed Check] Restaurando Datos de Login', xbmc.LOGNOTICE)
	wiz.clearS('install')
else: wiz.log("[Installed Check] No disponible", xbmc.LOGNOTICE)

if FAILED == False:
	wiz.log("[Build Check] Iniciada", xbmc.LOGNOTICE)
	if not WORKING:
		wiz.log("[Build Check] No es una URL valida para el archivo de compilacion: %s" % BUILDFILE, xbmc.LOGNOTICE)
	elif BUILDCHECK == '' and BUILDNAME == '':
		wiz.log("[Build Check] Primer intento", xbmc.LOGNOTICE)
		checkInstalled()
		wiz.setS('lastbuildcheck', str(NEXTCHECK))
	elif not BUILDNAME == '':
		wiz.log("[Build Check] Build Instalada", xbmc.LOGNOTICE)
		if SKIN in ['skin.confluence', 'skin.estuary'] and not DEFAULTIGNORE == 'true':
			checkSkin()
			wiz.log("[Build Check] Build Instalada: Comprobando actualizaciones", xbmc.LOGNOTICE)
			wiz.setS('lastbuildcheck', str(NEXTCHECK))
			checkUpdate()
		elif BUILDCHECK <= str(TODAY):
			wiz.log("[Build Check] Build Instalada: Comprobando actualizaciones", xbmc.LOGNOTICE)
			wiz.setS('lastbuildcheck', str(NEXTCHECK))
			checkUpdate()
		else:
			wiz.log("[Build Check] Build Instalada: La siguiente verificacion no es hasta: %s / HOY es: %s" % (BUILDCHECK, str(TODAY)), xbmc.LOGNOTICE)

wiz.log("[Trakt Data] Iniciado", xbmc.LOGNOTICE)
if KEEPTRAKT == 'true':
	if TRAKTSAVE <= str(TODAY):
		wiz.log("[Trakt Data] Guardando todos los datos", xbmc.LOGNOTICE)
		traktit.autoUpdate('all')
		wiz.setS('traktlastsave', str(THREEDAYS))
	else:
		wiz.log("[Trakt Data] Siguiente Autoguardado no es hasta: %s / HOY es: %s" % (TRAKTSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Trakt Data] No disponible", xbmc.LOGNOTICE)

wiz.log("[Debrid Data] Iniciado", xbmc.LOGNOTICE)
if KEEPREAL == 'true':
	if REALSAVE <= str(TODAY):
		wiz.log("[Debrid Data] Guardando todos los datos", xbmc.LOGNOTICE)
		debridit.autoUpdate('all')
		wiz.setS('debridlastsave', str(THREEDAYS))
	else:
		wiz.log("[Debrid Data] Siguiente Autoguardado no es hasta: %s / HOY es: %s" % (REALSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Real Debrid Data] No disponible", xbmc.LOGNOTICE)

wiz.log("[Login Info] Iniciado", xbmc.LOGNOTICE)
if KEEPLOGIN == 'true':
	if LOGINSAVE <= str(TODAY):
		wiz.log("[Login Info] Guardando todos los datos", xbmc.LOGNOTICE)
		loginit.autoUpdate('all')
		wiz.setS('loginlastsave', str(THREEDAYS))
	else:
		wiz.log("[Login Info] Siguiente Autoguardado no es hasta: %s / HOY es: %s" % (LOGINSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Login Info] No disponible", xbmc.LOGNOTICE)

wiz.log("[Limpieza automatica] Iniciada", xbmc.LOGNOTICE)
if AUTOCLEANUP == 'true':
	service = False
	days = [TODAY, TOMORROW, THREEDAYS, ONEWEEK]
	feq = int(float(AUTOFEQ))
	if AUTONEXTRUN <= str(TODAY) or feq == 0:
		service = True
		next_run = days[feq]
		wiz.setS('nextautocleanup', str(next_run))
	else: wiz.log("[Limpieza automatica] Siguiente limpieza %s" % AUTONEXTRUN, xbmc.LOGNOTICE)
	if service == True:
		AUTOCACHE      = wiz.getS('clearcache')
		AUTOPACKAGES   = wiz.getS('clearpackages')
		AUTOTHUMBS     = wiz.getS('clearthumbs')
		if AUTOCACHE == 'true': wiz.log('[Limpieza automatica] de Cache: Activada', xbmc.LOGNOTICE); wiz.clearCache(True)
		else: wiz.log('[Limpieza automatica] de Cache: Desactivada', xbmc.LOGNOTICE)
		if AUTOTHUMBS == 'true': wiz.log('[Limpieza automatica] de Miniaturas Antiguas: Activada', xbmc.LOGNOTICE); wiz.oldThumbs()
		else: wiz.log('[Limpieza automatica] de Miniaturas antiguas: Desactivada', xbmc.LOGNOTICE)
		if AUTOPACKAGES == 'true': wiz.log('[Limpieza automatica] de Paquetes: Activada', xbmc.LOGNOTICE); wiz.clearPackagesStartup()
		else: wiz.log('[Limpieza automatica] de Paquetes: Desactivada', xbmc.LOGNOTICE)
else: wiz.log('[Limpieza automatica] Desactivada', xbmc.LOGNOTICE)

wiz.setS('kodi17iscrap', '')

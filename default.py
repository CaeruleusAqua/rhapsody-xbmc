import xbmcgui
import xbmc
import xbmcaddon
import pickle
import os
import gc
import time
from lib import rhapapi
from lib import image
from lib import member
from lib import play
from lib import view
from lib import lists
from lib import utils
from lib import caching


#Set global addon information first
__addon_id__ = 'script.audio.rhapsody'
__addon_cfg__ = xbmcaddon.Addon(__addon_id__)
__addon_path__ = __addon_cfg__.getAddonInfo('path')
__addon_version__ = __addon_cfg__.getAddonInfo('version')


class Application():
	__vars = None

	def __init__(self):
		self.__vars = {}  #dict for app vars
		self.view_keeper = {'browseview': 'browse_newreleases', 'frame': 'Browse'}


	def set_var(self, name, value):
		self.__vars[name] = value


	def has_var(self, name):
		return name in self.__vars


	def get_var(self, name):
		return self.__vars[name]


	def remove_var(self, name):
		del self.__vars[name]



class LoginWin(xbmcgui.WindowXML):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		pass


	def onInit(self):
		print "Starting onInit Loop"
		while not app.get_var('logged_in'):
			if app.get_var('bad_creds'):
				self.getControl(10).setLabel('Login failed! Try again...')
				print "Set fail label message"
			self.inputwin = InputDialog("input.xml", __addon_path__, 'Default', '720p')
			self.inputwin.doModal()
			data = mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
			app.set_var('logged_in', data['logged_in'])
			app.set_var('bad_creds', data['bad_creds'])
			del self.inputwin
			print "Logged_in value: " + str(app.get_var('logged_in'))
			print "Bad Creds value: " + str(app.get_var('bad_creds'))

		print "Exited the while loop! Calling the del function"
		self.close()


class InputDialog(xbmcgui.WindowXMLDialog):

	def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes):
		self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'rhapsody_font16', '0xDD171717', focusTexture="none.png")
		self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='rhapsody_font16', textColor='0xDD171717', focusTexture="none.png", isPassword=1)
		self.butn = None
		self.name_txt = ""
		self.pswd_txt = ""

	def onInit(self):
		self.name_select = self.getControl(10)
		#self.name_select.setVisible(False)
		self.pswd_select = self.getControl(11)
		self.pswd_select.setVisible(False)
		self.addControl(self.name)
		self.addControl(self.pswd)
		self.butn = self.getControl(22)
		self.name.setPosition(600, 320)
		self.name.setWidth(400)
		self.name.controlDown(self.pswd)
		self.pswd.setPosition(600, 410)
		self.pswd.setWidth(400)
		self.pswd.controlUp(self.name)
		self.pswd.controlDown(self.butn)
		self.butn.controlUp(self.pswd)
		self.setFocus(self.name)


	def onAction(self, action):
		#print str(action.getId())
		#print type(action)
		if action.getId() == 7:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			elif self.getFocusId() == 22:
				self.close()
				self.name_txt = self.name.getText()
				self.pswd_txt = self.pswd.getText()
			else: pass
		elif action.getId() == 18:
			if self.getFocus() == self.name:
				self.setFocus(self.pswd)
			elif self.getFocus() == self.pswd:
				self.setFocus(self.butn)
			elif self.getFocus() == self.butn:
				self.setFocus(self.name)
			else: pass
		else:
			pass

	def onFocus(self, control):
		if control == 3001:
			self.name_select.setVisible(True)
			self.pswd_select.setVisible(False)
		elif control == 3002:
			self.name_select.setVisible(False)
			self.pswd_select.setVisible(True)
		elif control == 22:
			self.name_select.setVisible(False)
			self.pswd_select.setVisible(False)
		else: pass


class MainWin(xbmcgui.WindowXML):

	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		self.setup = False
		print "running _init_ for mainwin"
		#self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		#self.win.setProperty("browseview", 'browse_newreleases')
		#self.win.setProperty("frame", 'Browse')

		#self.pos = None
		#self.playing_pos = None
		#self.current_playlist_albumId = None
		#self.browse_menu = ["browse_newreleases","browse_topalbums","browse_topartists","browse_toptracks"]
		#self.library_menu = ["library_albums", "library_artists", "library_tracks", "library_stations", "library_favorites"]
		#print "Script path: " + __addon_path__


	def onInit(self):
		print "running onInit for mainwin"
		self.handle = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		self.handle.setProperty("browseview", app.view_keeper['browseview'])
		self.handle.setProperty("frame", app.view_keeper['frame'])
		#self.alb_dialog = None
		self.main()

	def main(self):
		self.handle.setProperty("full_name", mem.first_name+" "+mem.last_name)
		self.handle.setProperty("country", mem.catalog)
		self.handle.setProperty("logged_in", "true")
		self.clist = self.getControl(201)
		self.frame_label = self.getControl(121)
		view.draw_mainwin(self, app)


	def onAction(self, action):
		if action.getId() == 7:
			self.manage_action()
		if action.getId() == 10:
			utils.goodbye(self, app, player)
		elif action.getId() == 92:
			utils.goodbye(self, app, player)
		else:
			pass


	def manage_action(self):
		if self.getFocusId() == 201:
			view.draw_mainwin(self, app)
			app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

		elif self.getFocusId() == 101:
			view.draw_mainwin(self, app)
			app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

		elif self.getFocusId() == 1001:
			app.set_var('logged_in', False)
			try:
				os.remove(mem.filename)
			except OSError, e:  ## if failed, report it back to the user ##
				print ("Error: %s - %s." % (e.filename,e.strerror))
			player.stop()
			playlist.clear()
			self.close()

	def onClick(self, control):
		pos = self.getCurrentListPosition()
		id = app.get_var(list)[pos]#["album_id"]
		print "mainwin onClick: id: "+str(id)
		if control == 50:
			self.alb_dialog = AlbumDialog("album.xml", __addon_path__, 'Default', '720p', current_list=app.get_var(list),
			                         pos=pos, cache=cache.album, alb_id=id)
			self.alb_dialog.setProperty("review", "has_review")
			self.alb_dialog.doModal()
			self.alb_dialog.id = None
			if self.empty_list():
				view.draw_mainwin(self, app)
			self.setCurrentListPosition(self.alb_dialog.pos)
			cache.save_album_data()

		elif control == 51:
			self.start_playback(control)


	def start_playback(self, id):

		player.now_playing = {'pos': 0, 'type':'playlist', 'item':toptracks.data, 'id':'toptracks'}  #['data']}
		player.build()
		if id == 51:
			player.now_playing['pos'] = self.getCurrentListPosition()
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song...)")
		track = player.add_playable_track(0)
		if not track:
			xbmc.executebuiltin("XBMC.Notification(Rhapsody, Problem with this song. Aborting...)")
			print "Unplayable track. Can't play this track"
			#player.stop()
			return False
		player.playselected(player.now_playing['pos'])
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started)")
		if id == 21:
			self.setCurrentListPosition(playlist.getposition())
			self.setFocusId(51)


	def onFocus(self, control):
		#print("onfocus(): control %i" % control)
		pass


	def make_visible(self, *args):
		for item in args:
			self.getControl(item).setVisible(True)

	def empty_list(self):
		if self.getListSize() < 2:
			return True


	def sync_playlist_pos(self):
		try:
			if player.now_playing['id'] == 'toptracks':
				print "syncing playlist pos because player.now_playing id is 'toptracks'"
				self.setCurrentListPosition(playlist.getposition())
				toptracks.pos = playlist.getposition()
			elif player.now_playing['id'] == self.alb_dialog.id:
				print "syncing playlist pos because player.now_player id is current album id"
				self.alb_dialog.setCurrentListPosition(playlist.getposition())
		except:
			pass


class DialogBase(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlName, thescriptPath, defaultname, forceFallback):
		#print "I'm the base dialog class"
		pass


class AlbumDialog(DialogBase):

	def __init__(self, *args, **kwargs):
		DialogBase.__init__(self, *args)
		self.current_list = kwargs.get('current_list')
		self.cache = kwargs.get('cache')
		self.id = kwargs.get('alb_id')
		self.pos = kwargs.get('pos')
		self.img_dir = __addon_path__+'/resources/skins/Default/media/'


	def onInit(self):
		self.show_info(self.id, self.cache)


	def show_info(self, alb_id, cache):
		print "AlbumDialog: album id = "+self.id
		album = cache[alb_id]
		self.reset_fields()
		self.clearList()
		self.getControl(11).setText(album["album"])
		self.getControl(13).setLabel(album["artist"])
		self.getControl(8).setLabel(album["album_date"])
		self.manage_artwork(cache, album)
		self.getControl(7).setImage(album["bigthumb"])
		self.manage_review(cache, album)
		self.getControl(14).setText(album["review"])
		self.manage_details(cache, album)
		self.getControl(10).setLabel(album["label"])
		self.getControl(6).setLabel(album["style"])
		self.manage_windowtracklist(cache, album)

	def show_next_album(self, offset):
		self.pos = (self.pos+offset) % len(self.current_list)
		self.id = self.current_list[self.pos]#['album_id']
		self.show_info(self.id, self.cache)
		print str(self.pos)
		print len(self.current_list)

	def manage_windowtracklist(self, cache, album):
		print "AlbumDialog: Manage tracklist for gui list"
		liz = windowtracklist.get_litems(cache, album["album_id"])
		for item in liz:
			self.addItem(item)
		win.sync_playlist_pos()

	def onAction(self, action):
		if action.getId() == 7:                     # --- Enter / Select ---
			if self.getFocusId() == 21:             # --- Play Button ---
				self.start_playback(self.getFocusId(), self.cache[self.id])
			elif self.getFocusId() == 27:           # --- Next Button ---
				self.show_next_album(1)
			elif self.getFocusId() == 26:           # --- Prev Button ---
				self.show_next_album(-1)
			elif self.getFocusId() == 51:           # --- Tracklist ---
				self.start_playback(self.getFocusId(), self.cache[self.id])
			else: pass
		elif action.getId() == 10:                  # --- Back ---
			self.close()
		elif action.getId() == 92:                  # --- Esc ---
			self.close()
		elif action.getId() == 18:                  # --- Tab ---
			self.close()
		else:
			pass


	def start_playback(self, id, album):
		print "Album dialog: start playback"
		#utils.prettyprint(album['tracks'])
		if not self.now_playing_matches_album_dialog():
			print "hit the first if. building playlist"
			player.now_playing = {'pos': 0, 'type':'album', 'item':album['tracks'], 'id':album['album_id']}
			player.build()
		if player.now_playing['type'] != 'album':
			print "hit the second if. building playlist"
			player.now_playing = {'pos': 0, 'type':'album', 'item':album['tracks'], 'id':album['album_id']}
			player.build()
		#print "Now playing item list follows!"
		#utils.prettyprint(player.now_playing['item'])
		if id == 51:
			player.now_playing['pos'] = self.getCurrentListPosition()
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song...)")
		track = player.add_playable_track(0)
		if not track:
			xbmc.executebuiltin("XBMC.Notification(Rhapsody, Problem with this song. Aborting...)")
			print "Unplayable track. Can't play this track"
			#player.stop()
			return False
		player.playselected(player.now_playing['pos'])
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started)")
		if id == 21:
			self.setCurrentListPosition(playlist.getposition())
			self.setFocusId(51)


	def now_playing_matches_album_dialog(self):
		try:
			if player.now_playing['id'] == self.id:
				return True
			else:
				return False
		except:
			return True


	def reset_fields(self):
		self.getControl(6).setLabel("")
		self.getControl(7).setImage("")
		self.getControl(8).setLabel("")
		self.getControl(10).setLabel("")
		self.getControl(11).setText("")
		self.getControl(13).setLabel("")
		self.getControl(14).setText("")


	def manage_review(self, cache, album):
		alb_id = album["album_id"]
		if album["review"] == "":
			print "Getting review from Rhapsody"
			review = api.get_album_review(alb_id)
			if not review:
				if album['artist_id'] == "Art.0":
					print "No review for Various Artists"
					return
				else:
					review = api.get_bio(album['artist_id'])
					print "No review. Trying artist bio for album review space"
				#print review
			if review:
				#print review
				album["review"] = review
			else:
				print "No bio available for this artist either. :-("
				album["review"] = ""
		else:
			print "Already have the review in memory for this album"

	def manage_details(self, cache, album):
		alb_id = album["album_id"]
		if album["label"] == "":
			# try to get info from cached album data
			if cache.has_key(alb_id) and (cache[alb_id]['label'] != ""):
				print "Using genre, track, and label from cached album data"
			else:
				print "Getting genre, tracks and label from Rhapsody"
				results = api.get_album_details(alb_id)
				if results:
					album["label"] = results["label"]
					album["tracks"] = results["trackMetadatas"]
					album["style"] = results["primaryStyle"]
				else:
					print "Album Detail api not returning response"
		else:
			print "Using genre, track, and label from cached album data"

	def manage_artwork(self, cache, album):
		alb_id = album["album_id"]
		if os.path.isfile(cache[alb_id]['bigthumb']):
			return
		else:
			if not album['thumb_url']:
				file = img.handler(album['thumb_url'], 'large', 'album')
			else:
				file = img.base_path+self.big_image(album["album_id"])
			album["bigthumb"] = file
			#cache[alb_id]['bigthumb'] = file

	def big_image(self, album_id):
		url = img.identify_largest_image(album_id, "album")
		bigthumb = img.handler(url, 'large', 'album')
		return bigthumb


class ContentList():
	#handle new releases, top albums, artist discography, library album list, etc.
	def __init__(self, *args):

		self.data = []
		self.liz = []
		self.built = False
		self.pos = 0
		self.timestamp = time.time()
		self.type = args[0]
		self.name = args[1]
		self.filename = args[2]
		self.raw = None
		print 'running init code for '+self.name

	def fresh(self):
		return True

	def make_active(self):
		if (app.get_var('last_rendered_list') == self.name) and win.getListSize()>2:
			print "Window already has that list in memory. Skipping list building"
			return
		print "ContentList: make active " +self.name
		#print "current frame: "+app.get_var('current_frame')
		#print "current view: "+app.get_var('current_view')
		print "current frame: "+win.getProperty('frame')
		print "current view: "+win.getProperty('browseview')
		print "Built: "+str(self.built)
		print "Fresh: "+str(self.fresh())
		if self.built and self.fresh():
			print "doing simple list building for mainwin"
			self.build_winlist()
		else:
			print "Doing full data fetch and list building for mainwin"
			self.build()
		app.set_var('last_rendered_list', self.name)
		#if self.name == 'toptracks':
		#	win.sync_playlist_pos()
		#print app.get_var('last_rendered_list')


	def build(self):
		print "ContentList: build (full)"
		results = self.download_list()
		if results:
			self.ingest_list(results)
		else:
			print "Couldn't get info from rhapsody about "+self.name

	def save_raw_data(self, data):
		jar = open(self.filename, 'wb')
		pickle.dump(data, jar)
		jar.close()
		print self.name+" info saved in cachefile!"

	def download_list(self):
		print "Download_list. self.filename: "+self.filename
		try:
			pkl_file = open(self.filename, 'rb')
			self.raw = pickle.load(pkl_file)
			pkl_file.close()
			print "Loaded cache file"
			r = self.raw
		except:
			print "No list cache file to load. Let's download it"
			d = {'newreleases':   api.get_new_releases,
			     'topalbums':     api.get_top_albums,
			     'topartists':    api.get_top_artists,
			     'toptracks':     api.get_top_tracks,
			     'lib_albums':    api.get_library_albums,
			     'lib_artists':   api.get_library_artists,
			     #'lib_tracks':    api.get_library_artist_tracks,
			     #'lib_stations':  api.get_library_stations,
			     #'lib_favorites': api.get_library_favorites
			     }
			r = d[self.name]()
			#self.save_raw_data(r)
		#utils.prettyprint(r)
		return r

	def ingest_list(self, results):

		print "Ingest list. Type: "+self.type
		win.clearList()
		__ = {}

		d = {'album': cache.album,
			 'artist': cache.artist,
		     'track':  __,
		     'station': __}

		store = d[self.type]

		for i, item in enumerate(results):
			id = item['id']
			if self.type == 'album':
				infos = self.process_album(i, item)
				self.data.append(infos[self.type]['album_id'])
			elif self.type == 'artist':
				infos = self.process_artist(i, item)
				self.data.append(infos[self.type]['artist_id'])
			elif self.type == 'track':
				infos = self.process_track(i, item)
				self.data.append(infos[self.type])
			self.liz.append(infos['listitem'])
			self.add_lizitem_to_winlist(infos['listitem'])
			if not id in store:
				store[id] = infos[self.type]

		self.built = True
		#utils.prettyprint(self.data)
		cache.save_album_data()
		cache.save_artist_data()


	def process_album(self, count, item):
		data = {}
		thumb = img.handler(item["images"][0]["url"], 'small', 'album')
		data['album'] = {'album_id': item["id"],
		         'album': item["name"],
		         'thumb': thumb,
		         'thumb_url': item["images"][0]["url"],
		         'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
		         'orig_date': "",
		         'label': "",
		         'review': "",
		         'bigthumb': "",
		         'tracks': "",
		         'style': '',
		         'artist': item["artist"]["name"],
		         'list_id': count,
		         'artist_id': item["artist"]["id"]}
		data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', thumb)
		return data

	def process_artist(self, count, item):
		id = item['id']
		print "processing "+id
		data = {}

		if not id in cache.artist:
			if id == 'Art.0':
				print "detected artist 0 case!"
				url = None
				genre = ""
			else:
				url = img.identify_largest_image(item["id"], "artist")
				g_id = api.get_artist_genre(item["id"])
				genre = cache.genre_dict__[g_id]
		else:
			#print 'using cached thumb url for artist image'
			url = cache.artist[id]['thumb_url']
			#print 'using cached genre for artist'
			genre = cache.artist[id]['style']

		bigthumb = img.handler(url, 'large', 'artist')

		data['artist'] = {'artist_id': item["id"],
		         'name': item["name"],
		         'thumb': bigthumb,
		         'thumb_url': url,
		         'bio': "",
		         'bigthumb': bigthumb,
		         'toptracks': "",
		         'style': genre,
		         'list_id': count}
		data['listitem'] = xbmcgui.ListItem(item["name"], data["artist"]["style"], '', bigthumb)
		return data

	def process_track(self, count, item):
		data = {}
		#thumb = img.handler(item["images"][0]["url"], 'small', 'album')
		thumb = 'none.png'
		data['track'] = {'trackId': item["id"],
		         'name': item["name"],
		         'thumb': thumb,
		         #'thumb_url': item["images"][0]["url"],
		         'album': item['album']['name'],
		         'displayAlbumName': item['album']['name'],
		         'albumId': item['album']['id'],
		         'genre_id': item['genre']['id'],
		         'duration': item['duration'],
		         'playbackSeconds': item['duration'],
		         'style': '',
		         'artist': item["artist"]["name"],
		         'displayArtistName': item["artist"]["name"],
		         'artistId': item["artist"]["id"],
		         'previewURL': item['sample'],
		         'list_id': count,
		         'trackIndex': count+1}
		data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"])
		info = {
	            "title": item["name"],
	            "album": item['album']['name'],
	            "artist": item["artist"]["name"],
	            "duration": item['duration'],
	            "tracknumber": count+1,
				}
		data['listitem'].setInfo("music", info)
		return data

	def add_lizitem_to_winlist(self, li):
		win.addItem(li)

	def build_winlist(self):
		print "ContentList: build_winlist"
		win.clearList()
		for i, item in enumerate(self.liz):
			win.addItem(self.liz[i])
			#xbmc.sleep(2)
		print "list position: "+ str(self.pos)

class WindowTrackList():
	def __init__(self):
		pass
	#handle albums, playlists, radio, queue, listening history

	def get_litems(self, cache, id):
		print "Tracklist: adding dummy tracks for gui list"
		src = cache[id]
		list = []
		for i, item in enumerate(src["tracks"]):
			newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
			newlistitem.setInfo('music', { 'tracknumber':   int(src["tracks"][i]["trackIndex"]),
			                               'title':         src["tracks"][i]["name"],
			                               'duration':      int(src["tracks"][i]["playbackSeconds"])
			                               })
			list.append(newlistitem)
		print "Showing "+str(i+1)+" tracks"
		return list









#gc.disable()

app = Application()
mem = member.Member()
mem.set_addon_path(__addon_path__)
win = MainWin("main.xml", __addon_path__, 'Default', '720p')
cache = caching.Cache(__addon_path__)
api = rhapapi.Api()
img = image.Image(__addon_path__)

player = play.Player(win=win, cache=cache, img=img, api=api)
playlist = player.playlist


newreleases =   ContentList('album',   'newreleases',   __addon_path__+'/resources/.newreleases.obj')
topalbums =     ContentList('album',   'topalbums',     __addon_path__+'/resources/.topalbums.obj')
topartists =    ContentList('artist',  'topartists',    __addon_path__+'/resources/.topartists.obj')
toptracks =     ContentList('track',   'toptracks',     __addon_path__+'/resources/.toptracks.obj')
lib_albums =    ContentList('album',   'lib_albums',    __addon_path__+'/resources/.lib_albums.obj')
lib_artists =   ContentList('artist',  'lib_artists',   __addon_path__+'/resources/.lib_artists.obj')
#lib_tracks =    ContentList('track',   'lib_tracks',    __addon_path__+'/resources/.lib_tracks.obj')
#lib_stations =  ContentList('station', 'lib_stations',  __addon_path__+'/resources/.lib_stations.obj')
#lib_favorites = ContentList('tracks',  'lib_favorites', __addon_path__+'/resources/.lib_favorites.obj')
windowtracklist = WindowTrackList()

app.set_var('view_matrix' , {"browse_newreleases": newreleases,
			                "browse_topalbums":   topalbums,
			                "browse_topartists":  topartists,
			                "browse_toptracks":   toptracks,
			                "library_albums":     lib_albums,
			                "library_artists":    lib_artists,
			                #"library_tracks":     lib_tracks,
			                #"library_stations":   lib_stations,
			                #"library_favorites":  lib_favorites
			                })

app.set_var('running', True)
app.set_var('logged_in', False)
app.set_var('bad_creds', False)
app.set_var('last_rendered_list', None)

loadwin = xbmcgui.WindowXML("loading.xml", __addon_path__, 'Default', '720p')
loadwin.show()
loadwin.getControl(10).setLabel('Getting things ready...')
cache.load_cached_data()
time.sleep(1)


while app.get_var('running'):
	if not app.get_var('logged_in'):
		if not mem.has_saved_creds():
			logwin = LoginWin("login.xml", __addon_path__, 'Default', '720p')
			logwin.doModal()
			loadwin.getControl(10).setLabel('Logging you in...')
			del logwin
			time.sleep(1)
		else:
			loadwin.getControl(10).setLabel('Logging you in...')
			app.set_var('logged_in', True)
			time.sleep(1)
		api.token = mem.access_token
	#win = MainWin("main.xml", __addon_path__, 'Default', '720p')
	win.doModal()
	if app.get_var('logged_in') == False:
		loadwin.getControl(10).setLabel('Logging you out...')
	else:
		loadwin.getControl(10).setLabel('Finishing up...')
	del win
	t1 = time.time()
	cache.save_album_data()
	cache.save_artist_data()
	t2 = time.time()
	print "Album data save operation took "+str(t2-t1)
	time.sleep(1)
	#print "Saved album data to cachefile"
del loadwin
gc.collect()
print "Rhapsody addon has exited"



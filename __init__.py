# THANKYOU
# author of the original irc_pager. beautifully simple IRC solution!
# - Pepijn de Vos (https://badge.sha2017.org/projects/irc_pager)
import badge, ugfx, appglue, wifi, time, woezel
import usocket as socket

name = badge.nvs_get_str('owner', 'name', 'n00b')
log_messages = []
fonts = [
  'Roboto_Regular18',
  'PermanentMarker36',
  'pixelade13'
]
logo_width = 77
logo_path = '/lib/hackeriet/hackeriet-77.png'
is_updating = False

# Add 20 width to hide list scrollbars
log_ui_list = ugfx.List(logo_width, 0, ugfx.width() - logo_width + 30, ugfx.height() - 13)
log_ui_list.enabled(False)

def log(text):
  global log_messages
  log_messages.insert(0, text)

  # Keep log short
  if len(log_messages) > 10:
  	log_messages.pop()

  # Write all log lines, then flush buffer
  while (log_ui_list.count() > 0):
    log_ui_list.remove_item(0)
  for i, line in enumerate(log_messages):
    log_ui_list.add_item(line)
  ugfx.flush()

def clear_ghosting():
	ugfx.clear(ugfx.BLACK)
	ugfx.flush()
	badge.eink_busy_wait()
	ugfx.clear(ugfx.WHITE)
	ugfx.flush()
	badge.eink_busy_wait()

def start_self_update():
  global is_updating
  is_updating = True
  log('+ Starting self update')
  attempts = 0
  attempts_max = 5
  log('+ Waiting for network...')
  while not wifi.sta_if.isconnected():
    if attempts > attempts_max:
      log('+ Giving up wifi... Skipping update!')
      is_updating = False
      return
    time.sleep(1)
    pass
  # Attempt to install new version and restart the app if it succeeds
  try:
    woezel.install('hackeriet')
    appglue.start_app('hackeriet')
  except:
    log('+ woezel.install failed. May already be up to date.')
  is_updating = False

def exit_app():
  log('+ Exiting app...')
  appglue.home()

# ##################################
# LIGHTS
# ##################################

off = bytes([0, 0, 0, 0])
red = bytes([7, 7, 0, 0])
green = bytes([7, 0, 0, 0])

def blink_led(color, duration=.2):
  badge.leds_send_data(color, 4)
  time.sleep(duration)
  badge.leds_send_data(off, 4)

def program_main():
  ugfx.init()
  ugfx.clear(ugfx.WHITE)
  
  badge.leds_init()
  
  try:
    badge.eink_png(0, 0, logo_path)
  except:
    log('+ Failed to load graphics')
  
  # Name tag
  ugfx.string(ugfx.width() - ugfx.get_string_width(name, fonts[1]), ugfx.height() - 36, name, fonts[1], ugfx.BLACK)
  
  # Button info
  ugfx.string(0, ugfx.height() - 13, '[FLASH to update] [B to exit]', fonts[2], ugfx.BLACK)
  ugfx.flush()
  
  ugfx.input_init()
  ugfx.input_attach(ugfx.BTN_B, lambda pressed: exit_app())
  ugfx.input_attach(ugfx.BTN_FLASH, lambda pressed: start_self_update())

  HOST = "chat.freenode.net"
  PORT = 6667
  NICK = name+"[luv]"
  REALNAME = name+' @ SHA2017'
  
  log('+ waiting for network...')
  wifi.init()
  while not wifi.sta_if.isconnected():
    time.sleep(0.1)

  s = socket.socket()
  s.connect((HOST, PORT))

  s.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
  s.send(bytes("USER %s 0 * :%s\r\n" % (NICK, REALNAME), "UTF-8"))
  s.send(bytes("JOIN #sha2017\r\n", "UTF-8"));

  # IRC Client
  while True:
    line = s.readline().rstrip()
    parts = line.split()

    if parts:
      if (parts[0] == b"PING"):
        s.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
        blink_led(green)
      if (parts[1] == b"PRIVMSG"):
        blink_led(red)
        msg = b' '.join(parts[3:])
        rnick = line.split(b'!')[0]
        log(b'%s: %s' % (rnick, msg))

program_main()

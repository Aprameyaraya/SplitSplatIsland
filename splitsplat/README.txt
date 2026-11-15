SPLITSPLAT ISLAND - a pixel-art game based on William Spaniel's Game Theory 101
Unofficial, free fan project. Not affiliated with or endorsed by William Spaniel.
Watch the real lectures: https://gametheory101.com/courses/game-theory-101/

FILES (keep them together in one folder)
  main.py          entry point
  sp_engine.py     drawing + all reusable scenes
  sp_levels_1.py   units 1-3
  sp_levels_2.py   units 4-9 + final boss
  sp_links.py      which lectures each level links to

PLAY ON DESKTOP
  pip install pygame
  python main.py

PLAY IN A BROWSER (easiest): the web folder
  Double-click web/index.html. That is the whole game: no Python, no install, works on phones.
  To put it online, upload the web folder (or splitsplat-web.zip) to itch.io (new project > HTML, tick 'played in the browser'),
  GitHub Pages, Netlify Drop, or any web host. Players are saved in the visitor's own browser.
  The web version's lessons are generated from the Python game. After editing any level in Python, run:  python export_web.py
  Save codes work between the Python and browser versions.

ALTERNATIVE BROWSER BUILD (pygbag, optional and untested)
  pip install pygbag
  (from the folder that CONTAINS the splitsplat folder)
  pygbag splitsplat            -> builds, then serves at http://localhost:8000
  pygbag --build splitsplat    -> only builds; upload the zip in splitsplat/build/web to itch.io as an HTML5 game
  NOTE: the browser build was prepared but not built or tested by the author of these files.
  In the browser the game uses the browser's default font (text spacing may differ slightly) and saves players
  in the browser's localStorage. Tapping works through the browser's touch-to-mouse conversion; numbers and names
  are entered with on-screen keypads.

CONTROLS
  Mouse or touch. SPACE / tap advances dialogue. ESC or the on-screen "< Back" button goes back.
  Island screen: "Unlock all levels" button (handy if you already know the early units).

PLAYERS AND SAVING
  Pick or create a player on the start screen. Progress saves automatically on this device.
  "Save code" (island screen) shows a short code that restores progress on another device.
  Real cloud accounts would need a server, which this project does not have.

IF SOMETHING BREAKS
  The game writes errors to crash_log.txt next to main.py and returns to the map instead of closing.

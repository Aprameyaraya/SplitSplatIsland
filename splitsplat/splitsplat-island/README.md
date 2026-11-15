# Splitsplat Island

A free, **unofficial fan project**: a pixel-art story game that teaches the 9 units of William Spaniel's *Game Theory 101*.
Not affiliated with or endorsed by William Spaniel. The lecture ideas are his; every level links to the matching lecture at
[gametheory101.com](https://gametheory101.com/courses/game-theory-101/). Please watch the real lectures.

**Play in the browser:** `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/` (replace with your own link after enabling GitHub Pages)

## Run the Python version
```
pip install pygame
python main.py
```

## Browser version
The `docs/` folder is the whole browser game (`docs/index.html` plus three .js files). The lessons in `docs/content.js` are generated
from the Python files. After editing a level, run `python export_web.py` to refresh it.

## Notes
- 41 levels, optional quizzes, a boss-fight final exam, touch keypad, local player profiles with save codes.
- Players are saved in the player's own browser (web) or `splitsplat_save.json` (Python). Neither is uploaded anywhere.
- No license is included yet. Until you add one, all rights are reserved by default. Decide on a license before inviting others to reuse the code.

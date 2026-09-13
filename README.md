# Tuqa Lynch — portfolio

Static site. No build step for viewing.

## Local preview
    python3 -m http.server 8777
then open http://localhost:8777

## Regenerate case-study pages
Edit data in `build/gen.py` then:
    python3 build/gen.py
This re-writes `work/*.html` and re-downloads any missing images into `assets/img/<slug>/`.

## Swap the showreel
Replace `assets/video/showreel.mp4` with your real reel (same filename).

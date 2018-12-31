#! /bin/bash
pyinstaller entry.py -F -w --add-data soundfont.sf2:. --add-data libfluidsynth.dylib:.
cp -r ./dist/entry.app ./entry.app
rm -r ./dist
rm -r ./build
rm entry.spec

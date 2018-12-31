pyinstaller entry_win.py -F -w --add-data soundfont.sf2;.
copy dist\entry_win.exe entry.exe
rmdir /S /Q dist
rmdir /S /Q build
del /Q entry_win.spec
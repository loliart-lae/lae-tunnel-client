rd/s/q build
rd/s/q dist

pyinstaller lae-tunnel.py -F

copy "config.yml" dist
md .\dist\language
xcopy language .\dist\language
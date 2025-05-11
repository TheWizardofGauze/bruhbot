@echo off
pushd %~dp0
python -m pip install -U Red-DiscordBot
start "" cmd /c cscript redbot.vbs
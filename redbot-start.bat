@echo off
pushd %~dp0
echo python -m pip install -U Red-DiscordBot
echo python -m pip install -U discord
start "" cmd /c cscript redbot.vbs
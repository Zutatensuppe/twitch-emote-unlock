Remove-Item .\dist -Recurse
poetry run pyinstaller --onefile run.py
mkdir .\dist\twitch-emote-unlock
mv .\dist\run.exe .\dist\twitch-emote-unlock\run.exe
cp .\config.example.toml .\dist\twitch-emote-unlock\config.toml
Compress-Archive -Path .\dist\twitch-emote-unlock -DestinationPath .\dist\twitch-emote-unlock-windows.zip

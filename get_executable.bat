python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --icon=icon.ico --name Valorant_Caster_Helper  --onefile --noconsole --add-data "assets;assets" main.py
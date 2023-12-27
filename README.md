# together-api-gui
 
### Create a virtual environment
1. Open the command palette with `ctrl + shift + p` in vscode
2. Type `python create env` and select the option
3. Select `Venv`
4. Select `Python 3.XX` python 3.8 or greater
5. Check `requirements.txt` and press OK
6. `pip install git+https://github.com/openai/openai-python.git@b2b4239bc95a2c81d9db49416ec4095f8a72d5e2` to install speech streaming compatible version

### API Keys
1. Create a empty file called `.env`
2. Enter your openai api key in env file. example: `OPENAI_API_KEY=...`
3. Enter your together ai api key in env file. example: `TOGETHER_API_KEY=...`

### Install mpv
1. Follow the [tutorial](https://mpv.io/) here
<div align="center">
  <h1>Sounder</h1>
  <h3>Quickly play local music/sound.</h3>
  <img src="https://img.shields.io/badge/Python-purple?style=for-the-badge&logo=python&logoColor=white"/> 
  <a href="https://github.com/FJRG2007"> <img alt="GitHub" src="https://img.shields.io/badge/GitHub-purple?style=for-the-badge&logo=github&logoColor=white"/></a>
  <a href="https://ko-fi.com/fjrg2007"> <img alt="Kofi" src="https://img.shields.io/badge/Ko--fi-purple?style=for-the-badge&logo=ko-fi&logoColor=white"></a>
  <br />
  <hr />
</div>

### Use (Still in development)

First clone the repository:
```bash
$ git clone https://github.com/FJRG2007/sounder.git
$ cd sounder
```

Now install the requirements:
```bash
$ pip install -r requirements.txt
```

Then, replace the `.env.example` file to `.env` and fill in the tokens you need.

> [!NOTE]\
> Remember to create your playlists as folders and download your sounds in mp3!

```txt
📦sounds
 ┗ 📂Playlist Name
 ┃ ┗ 📜Sound Name.mp3
```

```bash
$ python main.py
```

### Features

- Algorithm for sound recommendation and sound selection.
- Sound search system in the current playlist.
- Direct integration with Discord and Macros for device control.
- Customized playback order for the user.

#### License
The founder of the project, [FJRG2007](https://github.com/FJRG2007/), reserves the right to modify the license at any time.
This project is licensed under the terms of the [GNU Affero General Public License](./LICENSE).

<p align="right"><a href="#top">Back to top 🔼</a></p>
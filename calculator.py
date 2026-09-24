# calculator.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests

logger = logging.getLogger('MusicPlayer')

if sys.platform == 'win32':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

mcp = FastMCP("AdvancedMusicPlayer")

@mcp.tool()
def play_music(song_name: str) -> dict:
    """
    当用户想要听歌、播放音乐、点播特定歌曲或歌手的曲目时，必须调用此工具。
    参数 song_name: 用户想要播放的歌曲名称或歌手名，例如 '晴天'、'青花瓷'。
    """
    logger.info(f"正在检索歌曲: {song_name}")
    
    search_url = f"http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={song_name}&type=1&offset=0&total=true&limit=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://music.163.com"
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=5)
        result = res.json()
        songs = result.get("result", {}).get("songs", [])
        if not songs:
            return {"success": False, "message": f"未找到歌曲《{song_name}》"}
            
        first_song = songs[0]
        song_id = first_song.get("id")
        title = first_song.get("name")
        artists = "/".join([a.get("name", "") for a in first_song.get("artists", [])])
        
        # 预先跟随重定向，获取真实的 HTTPS CDN 播放地址，避免板端 302 失败
        redirect_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
        r_head = requests.head(redirect_url, headers=headers, allow_redirects=True, timeout=5)
        real_audio_url = r_head.url
        
        logger.info(f"解析到真实音频直链: {real_audio_url}")
        
        # 返回符合小智音箱多媒体播放标准结构的数据
        return {
            "type": "music",
            "action": "play",
            "title": title,
            "artist": artists,
            "url": real_audio_url,
            "audio_url": real_audio_url,
            "message": f"正在为你播放《{title}》"
        }
        
    except Exception as e:
        logger.error(f"解析出错: {e}")
        return {"success": False, "message": f"点歌失败: {e}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")

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

mcp = FastMCP("MusicPlayer")

@mcp.tool()
def play_music(song_name: str) -> dict:
    """
    【音乐播放工具】
    当用户要求听歌、点歌、播放音乐或指定某首歌曲时调用此工具。
    工具将返回音乐直链。系统接收后必须向硬件播放器下发音频流播放指令。
    参数:
      song_name: 歌曲名或歌手加歌名
    """
    logger.info(f"正在检索歌曲: {song_name}")
    
    search_url = f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={song_name}&type=1&offset=0&total=true&limit=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://music.163.com"
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=5)
        result = res.json()
        songs = result.get("result", {}).get("songs", [])
        
        if not songs:
            return {"status": "error", "message": f"未找到歌曲《{song_name}》"}
            
        first_song = songs[0]
        song_id = first_song.get("id")
        title = first_song.get("name")
        artists = "/".join([a.get("name", "") for a in first_song.get("artists", [])])
        
        # 使用官方标准 HTTPS 外链（短链结构，ESP32 缓冲区不会溢出）
        audio_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
        
        logger.info(f"匹配成功: 《{title}》 - {artists} -> {audio_url}")
        
        # 返回专属于智能音箱多媒体服务的复合指令
        return {
            "status": "success",
            "device_action": "PLAY_AUDIO",
            "play_mode": "audio_stream",
            "url": audio_url,
            "audio_url": audio_url,
            "title": title,
            "artist": artists,
            "tts_reply": f"好的，正在为你播放{artists}的《{title}》"
        }
        
    except Exception as e:
        logger.error(f"音乐解析错误: {e}")
        return {"status": "error", "message": f"音乐点播失败: {e}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")

# calculator.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests

logger = logging.getLogger('MusicPlayer')

# 修复 Windows 控制台中文编码
if sys.platform == 'win32':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 初始化 MCP 服务
mcp = FastMCP("AdvancedMusicPlayer")

@mcp.tool()
def play_music(song_name: str) -> dict:
    """
    当用户想要听歌、播放音乐、点播特定歌曲或歌手的曲目时，必须调用此工具。
    参数 song_name: 用户想要播放的歌曲名称或歌手名，例如 '晴天'、'周杰伦 稻香'。
    """
    logger.info(f"正在搜索并解析歌曲: {song_name}")
    
    # 免费聚合音乐解析 API（支持跨源搜索与直链获取）
    search_url = f"https://api.vkeys.cn/v2/music/netease?word={song_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=8)
        data = response.json()
        
        if data.get("code") == 200 and data.get("data"):
            music_info = data["data"]
            title = music_info.get("song", song_name)
            singer = music_info.get("singer", "未知歌手")
            play_url = music_info.get("url")
            
            if play_url:
                logger.info(f"解析成功: 《{title}》 - {singer} -> {play_url}")
                return {
                    "success": True,
                    "song": title,
                    "singer": singer,
                    "audio_url": play_url,
                    "message": f"已为你找到《{title}》- {singer}，音频链接：{play_url}"
                }
        
        # 备用方案（当主接口未匹配时返回提示）
        return {
            "success": False,
            "message": f"抱歉，暂时没有在曲库中找到歌曲《{song_name}》的无损播放源。"
        }
        
    except Exception as e:
        logger.error(f"音乐检索失败: {e}")
        return {
            "success": False,
            "message": f"搜索歌曲《{song_name}》时发生网络超时或错误，请稍后再试。"
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")

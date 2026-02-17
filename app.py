from flask import Flask, render_template_string, request
import ctypes
import time

app = Flask(__name__)

# 直接加载系统核心 DLL
user32 = ctypes.windll.user32

# Windows 硬件指令常量
WM_APPCOMMAND = 0x0319
APPCOMMAND_VOLUME_UP = 0x0A
APPCOMMAND_VOLUME_DOWN = 0x09
APPCOMMAND_VOLUME_MUTE = 0x08

# 全局变量，记录最后一次设置的值
# 既然无法稳定读取系统值，我们就以网页最后一次操作为准
last_vol = 50 

def set_volume_win32(target_level):
    """
    通过 SendMessage 直接发送硬件按键指令
    这是目前在你的环境下唯一 100% 生效的方法
    """
    # 1. 强制归零 (发送 50 次减量，每次减2)
    # 为了减少“抽搐感”，我们快速发送，不加延时
    for _ in range(50):
        user32.SendMessageW(user32.GetForegroundWindow(), WM_APPCOMMAND, 0, APPCOMMAND_VOLUME_DOWN << 16)
    
    # 2. 增加到目标值
    # 每次增加信号对应系统音量 2 级
    press_times = int(target_level / 2)
    for _ in range(press_times):
        user32.SendMessageW(user32.GetForegroundWindow(), WM_APPCOMMAND, 0, APPCOMMAND_VOLUME_UP << 16)

# --- 极简前端界面 (去掉了不稳定的读取，只管控制) ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>音量直控</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; background: #000; color: #fff; padding: 40px 20px; }
        .val { font-size: 8rem; font-weight: 900; color: #00ff88; margin: 20px 0; }
        .slider { width: 100%; max-width: 400px; height: 15px; border-radius: 10px; background: #333; -webkit-appearance: none; }
        .slider::-webkit-slider-thumb { -webkit-appearance: none; width: 45px; height: 45px; background: #fff; border-radius: 50%; border: 5px solid #00ff88; cursor: pointer; }
        .btn-group { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
        .btn { background: #222; border: 1px solid #444; color: white; width: 80px; height: 80px; border-radius: 20px; font-size: 2.5rem; cursor: pointer; }
        .btn:active { background: #00ff88; color: #000; }
    </style>
</head>
<body>
    <div class="val" id="v">50</div>
    
    <div class="btn-group">
        <button class="btn" onclick="step(-2)">－</button>
        <button class="btn" onclick="step(2)">＋</button>
    </div>

    <input type="range" min="0" max="100" value="50" class="slider" id="s">
    
    <p style="color: #444; margin-top: 30px;">Win32 API Direct Mode (No-Read)</p>

    <script>
        const s = document.getElementById('s');
        const v = document.getElementById('v');
        let timer = null;

        function update(val) {
            val = Math.max(0, Math.min(100, val));
            s.value = val;
            v.innerText = val;
            
            // 增加防抖，避免拖动过快导致消息队列堵塞引发的严重抽搐
            clearTimeout(timer);
            timer = setTimeout(() => {
                fetch(`/set?l=${val}`);
            }, 150);
        }

        s.oninput = () => update(s.value);
        function step(d) {
            update(parseInt(s.value) + d);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/set')
def set_vol():
    l = request.args.get('l', type=int)
    if l is not None:
        try:
            set_volume_win32(l)
            return "OK"
        except Exception as e:
            return str(e), 500
    return "Error", 400

if __name__ == '__main__':
    # 端口 5000，使用单线程模式处理消息请求更稳定
    print("DLL 直接控制模式已启动...")
    app.run(host='0.0.0.0', port=5000, threaded=False)

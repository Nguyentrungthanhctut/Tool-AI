import ctypes
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps, ImageGrab
import io, math, json, threading, queue, os, base64, mimetypes, re
import urllib.request, urllib.error, urllib.parse

# Khai báo DPI Awareness trên Windows để tọa độ kéo chụp màn hình không bị lệch khi bật Scaling
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

BASE = 'https://generativelanguage.googleapis.com/'
CONFIG_DIR = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'SolverProV8')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
COPYRIGHT_TEXT = '© 2026 ThanhDevHub • All Rights Reserved'

SYSTEM_PROMPT = (
    "Hỗ trợ đối chiếu bài tập luyện tập. Trả đáp án ngắn gọn theo số câu kèm một bước kiểm chứng ngắn. "
    "Trình bày công thức toán học bằng ký tự Unicode dễ đọc (ví dụ: x², √x, ∫, π, ≤, ≥, ≠, →), "
    "không dùng cú pháp LaTeX thô như $ hoặc \\frac. Nếu thiếu dữ kiện, hãy nói rõ."
)


def load_saved_key():
    if os.getenv('GEMINI_API_KEY'):
        return os.getenv('GEMINI_API_KEY').strip()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('api_key', '').strip()
    except Exception:
        return ''


def save_key(api_key):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'api_key': api_key.strip()}, f)
    except Exception:
        pass


def request(key, version, path, payload=None, timeout=10):
    req = urllib.request.Request(
        BASE + version + '/' + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={'x-goog-api-key': key, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def describe(e, key):
    if isinstance(e, urllib.error.HTTPError):
        try:
            detail = json.loads(e.read()).get('error', {}).get('message', '')
        except Exception:
            detail = ''
        msg = f'HTTP {e.code}: {detail}'
    else:
        msg = str(e)
    return msg.replace(key, '[KEY]') if key else msg


def discover(key):
    for version in ('v1beta', 'v1'):
        models = []
        page = ''
        try:
            while True:
                params = {'pageSize': 100}
                if page:
                    params['pageToken'] = page
                data = request(key, version, 'models?' + urllib.parse.urlencode(params))
                for m in data.get('models', []):
                    name = m.get('name', '')
                    if (
                        name.startswith('models/gemini-')
                        and 'generateContent' in m.get('supportedGenerationMethods', [])
                        and not any(x in name for x in ('embedding', 'tts', 'audio', 'live', 'image', 'robotics', 'computer-use', 'research'))
                    ):
                        models.append(name)
                page = data.get('nextPageToken', '')
                if not page:
                    break
        except urllib.error.HTTPError as e:
            if e.code == 404 and version == 'v1beta':
                continue
            raise
        if models:
            def rank(n):
                match = re.search(r'gemini-(\d+)(?:\.(\d+))?', n)
                return (
                    not any(x in n for x in ('preview', 'experimental', '-exp')),
                    'flash' in n,
                    'lite' in n,
                    tuple(int(x or 0) for x in match.groups()) if match else (0, 0)
                )
            return version, sorted(set(models), key=rank, reverse=True)
    raise RuntimeError('Không tìm thấy model Gemini phù hợp.')


def generate(key, version, model, parts, check=False):
    payload = {'contents': [{'parts': parts}]}
    if check:
        payload['generationConfig'] = {'maxOutputTokens': 256}
    data = request(key, version, model + ':generateContent', payload, timeout=12 if check else 60)
    answer = '\n'.join(
        p['text']
        for c in data.get('candidates', [])
        for p in c.get('content', {}).get('parts', [])
        if 'text' in p and not p.get('thought')
    )
    if not answer.strip():
        raise RuntimeError('Model không trả về văn bản. ' + str(data.get('promptFeedback', '')))
    return answer


def image_to_part(img):
    img = img.convert('RGB')
    img.thumbnail((2400, 2400))
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=92)
    return {'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(buf.getvalue()).decode()}}


def main():
    root = tk.Tk()
    root.title('Solver Pro V8 | ThanhDevHub')
    root.geometry('380x600')
    root.minsize(360, 500)

    bg = '#101010'
    panel = '#242424'
    accent = '#2d5a88'
    fg = '#ffffff'
    root.configure(bg=bg)

    # Tùy chỉnh thanh Progressbar giao diện tối
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    style.configure(
        'Custom.Horizontal.TProgressbar',
        troughcolor=panel,
        background=accent,
        bordercolor=bg,
        lightcolor=accent,
        darkcolor=accent,
        thickness=12
    )

    key = tk.StringVar(value=load_saved_key())
    status = tk.StringVar(value='Chưa kết nối')
    events = queue.Queue()
    cache = {}
    busy = False
    buttons = []
    result = None

    # Footer Copyright cố định ở đáy cửa sổ
    footer = tk.Frame(root, bg='#0a0a0a')
    footer.pack(side='bottom', fill='x')
    tk.Label(
        footer, text=COPYRIGHT_TEXT, bg='#0a0a0a', fg='#777777',
        font=('Segoe UI', 8, 'bold'), pady=5
    ).pack()

    frame = tk.Frame(root, bg=bg)
    frame.pack(fill='both', expand=True, padx=14, pady=12)

    def clear():
        buttons.clear()
        for w in frame.winfo_children():
            w.destroy()

    def label(t, size=12, anchor='w', color=fg):
        lbl = tk.Label(frame, text=t, bg=bg, fg=color, font=('Segoe UI', size, 'bold'))
        lbl.pack(anchor=anchor, pady=4)
        return lbl

    def button(parent, t, cmd, bg_color=panel, side=None, expand=False):
        b = tk.Button(
            parent, text=t, command=cmd, bg=bg_color, fg=fg,
            activebackground='#404040', activeforeground=fg,
            relief='flat', font=('Segoe UI', 10, 'bold' if bg_color == accent else 'normal'),
            pady=7, cursor='hand2'
        )
        if side:
            b.pack(side=side, fill='x', expand=expand, padx=2, pady=3)
        else:
            b.pack(fill='x', pady=3)
        buttons.append(b)
        return b

    def state():
        tk.Label(frame, textvariable=status, bg=bg, fg='#bcbcbc', wraplength=340, justify='left').pack(fill='x', pady=4)

    # --- BƯỚC 1: MÀN HÌNH LOADING & NÚT BẮT ĐẦU ---
    def splash():
        root.unbind('<Control-v>')
        clear()

        box = tk.Frame(frame, bg=bg)
        box.pack(expand=True, fill='x', padx=10)

        tk.Label(box, text='SOLVER PRO V8', bg=bg, fg=fg, font=('Segoe UI', 22, 'bold')).pack(pady=(10, 2))
        tk.Label(box, text='Developed by ThanhDevHub', bg=bg, fg='#4da6ff', font=('Segoe UI', 10, 'bold')).pack(pady=(0, 24))

        load_msg = tk.StringVar(value='Đang khởi tạo hệ thống... 0%')
        tk.Label(box, textvariable=load_msg, bg=bg, fg='#bcbcbc', font=('Segoe UI', 9)).pack(pady=(0, 6))

        pbar = ttk.Progressbar(box, style='Custom.Horizontal.TProgressbar', orient='horizontal', mode='determinate', maximum=100)
        pbar.pack(fill='x', pady=(0, 20))

        start_btn = tk.Button(
            box, text='BẮT ĐẦU', command=login, bg='#333333', fg='#888888',
            activebackground='#3b73ad', activeforeground=fg,
            relief='flat', font=('Segoe UI', 11, 'bold'), pady=9, state='disabled'
        )
        start_btn.pack(fill='x', pady=6)

        steps = [
            (20, 'Đang tải giao diện & DPI Scaling...'),
            (45, 'Đang nạp cấu hình người dùng...'),
            (75, 'Đang chuẩn bị kết nối Gemini API...'),
            (100, 'Hệ thống đã sẵn sàng!')
        ]

        def animate(val=0):
            if val <= 100:
                pbar['value'] = val
                msg_prefix = 'Đang khởi tạo...'
                for threshold, text in steps:
                    if val <= threshold:
                        msg_prefix = text
                        break
                load_msg.set(f'{msg_prefix} ({val}%)')
                root.after(18, animate, val + 2)
            else:
                start_btn.configure(
                    state='normal', bg=accent, fg=fg, cursor='hand2',
                    text='BẮT ĐẦU →'
                )

        animate(0)

    # --- BƯỚC 2: MÀN HÌNH DÁN API KEY ---
    def login():
        if busy:
            return
        root.unbind('<Control-v>')
        clear()
        status.set('Nhập hoặc dán Gemini API Key để tiếp tục.')

        label('SOLVER PRO / V8', 18)
        label('Kết nối Gemini API', 11, color='#bcbcbc')

        key_entry = tk.Entry(
            frame, textvariable=key, show='*', bg=panel, fg=fg,
            insertbackground=fg, relief='flat', font=('Segoe UI', 12)
        )
        key_entry.pack(fill='x', ipady=8, pady=(8, 6))
        key_entry.focus_set()

        def paste_api():
            try:
                clip = root.clipboard_get().strip()
                if clip:
                    key.set(clip)
                    status.set('Đã dán API Key từ Clipboard.')
                else:
                    status.set('Clipboard đang trống.')
            except tk.TclError:
                status.set('Không có văn bản trong Clipboard.')

        def toggle_show():
            if key_entry.cget('show') == '*':
                key_entry.configure(show='')
                btn_eye.configure(text='Ẩn Key')
            else:
                key_entry.configure(show='*')
                btn_eye.configure(text='Hiện Key')

        row_api = tk.Frame(frame, bg=bg)
        row_api.pack(fill='x', pady=(0, 4))
        button(row_api, 'Dán API Key', paste_api, side='left', expand=True)
        btn_eye = button(row_api, 'Hiện Key', toggle_show, side='left', expand=True)

        button(frame, 'Kiểm tra & Kết nối', lambda: run(), bg_color=accent)
        state()

    # --- BƯỚC 3: MÀN HÌNH LÀM VIỆC CHÍNH ---
    def home():
        nonlocal result
        clear()
        label('SOLVER PRO / V8', 16)
        state()

        entry = tk.Text(
            frame, height=4, bg=panel, fg=fg, insertbackground=fg,
            wrap='word', relief='flat', font=('Segoe UI', 10)
        )
        entry.pack(fill='x', pady=4)

        def solve_text():
            s = entry.get('1.0', 'end').strip()
            if s:
                run([{'text': s}])
            else:
                status.set('Hãy nhập hoặc dán nội dung bài tập trước.')

        def paste_smart(event=None):
            if busy:
                return
            try:
                clip_img = ImageGrab.grabclipboard()
                if isinstance(clip_img, Image.Image):
                    status.set('Đã nhận ảnh từ Clipboard...')
                    run([image_to_part(clip_img)])
                    return 'break'
                elif isinstance(clip_img, list) and clip_img:
                    first = clip_img[0]
                    if os.path.isfile(first) and first.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        with Image.open(first) as im:
                            run([image_to_part(ImageOps.exif_transpose(im))])
                        return 'break'
            except Exception:
                pass

            try:
                txt = root.clipboard_get()
                if event is None:
                    entry.delete('1.0', 'end')
                    entry.insert('1.0', txt)
            except tk.TclError:
                status.set('Clipboard trống.')

        row1 = tk.Frame(frame, bg=bg)
        row1.pack(fill='x')
        button(row1, 'Chụp vùng màn hình', screen_capture, bg_color=accent, side='left', expand=True)
        button(row1, 'Dán (Text / Ảnh)', paste_smart, side='left', expand=True)

        row2 = tk.Frame(frame, bg=bg)
        row2.pack(fill='x')
        button(row2, 'Giải văn bản', solve_text, side='left', expand=True)
        button(row2, 'Cắt từ file ảnh', crop_image, side='left', expand=True)

        button(frame, 'Chọn file ảnh giải ngay', choose_image)

        label('Kết quả đối chiếu', 10)
        result = tk.Text(
            frame, height=6, bg=panel, fg=fg, wrap='word',
            relief='flat', font=('Segoe UI', 10)
        )
        result.pack(fill='both', expand=True, pady=(0, 4))
        result.configure(state='disabled')

        bar = tk.Frame(frame, bg=bg)
        bar.pack(fill='x', pady=(2, 0))

        def copy_result():
            txt = result.get('1.0', 'end').strip()
            if txt:
                root.clipboard_clear()
                root.clipboard_append(txt)
                status.set('Đã sao chép kết quả.')

        tk.Button(bar, text='Sao chép', command=copy_result, bg=panel, fg=fg, relief='flat', padx=8, pady=3, cursor='hand2').pack(side='left')
        tk.Button(bar, text='Đổi API', command=login, bg=panel, fg=fg, relief='flat', padx=8, pady=3, cursor='hand2').pack(side='right')

        scale = tk.Scale(
            bar, from_=75, to=100, orient='horizontal', showvalue=False,
            bg=bg, fg=fg, troughcolor=panel, highlightthickness=0, length=110,
            command=lambda v: root.attributes('-alpha', float(v) / 100)
        )
        scale.set(100)
        scale.pack(side='right', padx=8)

        root.bind('<Control-v>', paste_smart)

    def screen_capture():
        if busy:
            return
        root.withdraw()
        overlay = tk.Toplevel(root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.30)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='black')

        canvas = tk.Canvas(overlay, bg='black', cursor='crosshair', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        canvas.create_text(
            24, 24, anchor='nw',
            text='Kéo chuột chọn vùng bài tập • Nhấn Esc để hủy (ThanhDevHub)',
            fill='white', font=('Segoe UI', 15, 'bold')
        )

        start = []
        rect = [None]

        def cancel(e=None):
            overlay.destroy()
            root.deiconify()

        def down(e):
            start[:] = [e.x_root, e.y_root, e.x, e.y]
            rect[0] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline='#00d9ff', width=2)

        def move(e):
            if start:
                canvas.coords(rect[0], start[2], start[3], e.x, e.y)

        def up(e):
            if not start:
                return
            x, y = start[:2]
            box = (min(x, e.x_root), min(y, e.y_root), max(x, e.x_root), max(y, e.y_root))
            overlay.destroy()
            root.deiconify()
            if box[2] - box[0] < 10 or box[3] - box[1] < 10:
                status.set('Vùng chọn quá nhỏ.')
                return

            def grab():
                try:
                    im = ImageGrab.grab(bbox=box, all_screens=True)
                    run([image_to_part(im)])
                except Exception as exc:
                    status.set(str(exc))

            root.after(200, grab)

        canvas.bind('<ButtonPress-1>', down)
        canvas.bind('<B1-Motion>', move)
        canvas.bind('<ButtonRelease-1>', up)
        overlay.bind('<Escape>', cancel)
        overlay.focus_force()

    def crop_image():
        if busy:
            return
        path = filedialog.askopenfilename(filetypes=[('Ảnh', '*.png *.jpg *.jpeg *.webp')])
        if not path:
            return
        try:
            with Image.open(path) as source:
                original = ImageOps.exif_transpose(source).convert('RGB')
        except Exception as exc:
            status.set(str(exc))
            return

        root.unbind('<Control-v>')
        clear()

        max_w = min(820, root.winfo_screenwidth() - 60)
        max_h = min(680, root.winfo_screenheight() - 100)
        root.geometry(f'{max_w}x{max_h}')

        label('Kéo chọn vùng ảnh bài tập', 13)
        bar = tk.Frame(frame, bg=bg)
        bar.pack(side='bottom', fill='x', pady=4)
        state()

        preview = original.copy()
        preview.thumbnail((max_w - 40, max_h - 170))
        photo = ImageTk.PhotoImage(preview)

        canvas = tk.Canvas(frame, width=preview.width, height=preview.height, bg=panel, highlightthickness=0, cursor='crosshair')
        canvas.pack(expand=True)
        canvas.create_image(0, 0, anchor='nw', image=photo)
        canvas.image = photo

        selection = {}

        def point(e):
            return max(0, min(preview.width, e.x)), max(0, min(preview.height, e.y))

        def start_drag(e):
            canvas.delete('selection')
            selection.clear()
            selection['start'] = point(e)

        def drag(e):
            if 'start' not in selection:
                return
            canvas.delete('selection')
            selection['end'] = point(e)
            canvas.create_rectangle(*selection['start'], *selection['end'], outline='#00d9ff', width=2, dash=(4, 3), tags='selection')

        canvas.bind('<ButtonPress-1>', start_drag)
        canvas.bind('<B1-Motion>', drag)
        canvas.bind('<ButtonRelease-1>', drag)

        def back():
            root.geometry('380x600')
            home()

        def submit():
            if 'end' not in selection:
                status.set('Hãy kéo chọn vùng ảnh trước.')
                return
            x, y = selection['start']
            u, v = selection['end']
            if abs(x - u) < 5 or abs(y - v) < 5:
                status.set('Vùng chọn quá nhỏ.')
                return
            sx = original.width / preview.width
            sy = original.height / preview.height
            cropped = original.crop((
                int(min(x, u) * sx),
                int(min(y, v) * sy),
                math.ceil(max(x, u) * sx),
                math.ceil(max(y, v) * sy)
            ))
            back()
            run([image_to_part(cropped)])

        button(bar, 'Giải vùng đã chọn', submit, bg_color=accent, side='left', expand=True)
        button(bar, 'Quay lại', back, side='left', expand=True)

    def choose_image():
        if busy:
            return
        path = filedialog.askopenfilename(filetypes=[('Ảnh', '*.png *.jpg *.jpeg *.webp')])
        if not path:
            return
        try:
            with open(path, 'rb') as f:
                raw = f.read(10 * 1024 * 1024 + 1)
            if len(raw) > 10 * 1024 * 1024:
                raise ValueError('Ảnh vượt quá 10 MB.')
            mime = mimetypes.guess_type(path)[0] or 'image/png'
            run([{'inlineData': {'mimeType': mime, 'data': base64.b64encode(raw).decode()}}])
        except Exception as exc:
            status.set(str(exc))

    def run(parts=None):
        nonlocal busy
        if busy:
            return
        token = key.get().strip()
        if not token:
            status.set('Vui lòng nhập hoặc dán API Key.')
            return
        busy = True
        for b in buttons:
            b.configure(state='disabled')
        status.set('Đang kiểm tra kết nối...' if parts is None else 'Đang giải bài...')

        def worker():
            try:
                check = parts is None
                version, models = discover(token) if check else (cache['version'], cache['models'])
                content = [{'text': 'Reply OK.'}] if check else [{'text': SYSTEM_PROMPT}] + parts
                order = list(models)
                active = cache.get('active')
                if not check and active in order:
                    order.remove(active)
                    order.insert(0, active)
                errors = []
                for model in order[:2]:
                    events.put(('progress', 'Đang gọi ' + model.split('/')[-1] + '...'))
                    try:
                        answer = generate(token, version, model, content, check)
                        events.put(('ok', version, models, model, answer, check))
                        return
                    except Exception as exc:
                        errors.append(describe(exc, token))
                        if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403):
                            break
                raise RuntimeError(' | '.join(errors))
            except Exception as exc:
                events.put(('error', describe(exc, token)))

        threading.Thread(target=worker, daemon=True).start()

    def poll():
        nonlocal busy
        try:
            while True:
                e = events.get_nowait()
                if e[0] == 'progress':
                    status.set(e[1])
                    continue
                busy = False
                for b in buttons:
                    b.configure(state='normal')
                if e[0] == 'error':
                    status.set(e[1])
                    continue
                _, version, models, model, answer, check = e
                cache.update(version=version, models=models, active=model)
                status.set(model.split('/')[-1] + ' | Sẵn sàng')
                if check:
                    save_key(key.get())
                    home()
                else:
                    result.configure(state='normal')
                    result.delete('1.0', 'end')
                    result.insert('end', answer)
                    result.configure(state='disabled')
        except queue.Empty:
            pass
        root.after(100, poll)

    splash()
    poll()
    root.mainloop()


if __name__ == '__main__':
    main()
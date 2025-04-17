from PIL import Image, ImageDraw, ImageFont
import os, time, sys, json

def calc_ws(font):
    try: bbox = font.getbbox('W')
    except: bbox = font.getbbox(' ')
    cw, ch = max(bbox[2]-bbox[0],1), max(bbox[3]-bbox[1],1); area = cw*ch
    if area == 0: return [], 1, 1
    ws, img = [], Image.new('L', (cw, ch)); draw = ImageDraw.Draw(img)
    for i in range(32, 127): # ASCII printable
        draw.rectangle((0, 0, cw, ch), fill=0)
        try: draw.text((0, 0), chr(i), font=font, fill=255, anchor='lt')
        except TypeError: draw.text((0, 0), chr(i), font=font, fill=255) # Fallback for older PIL
        ws.append(sum(p > 0 for p in img.getdata()) / area) # Calculate weight
    return ws, cw, ch

def create_lt(ws): # Create brightness -> char LUT
    lt = [' '] * 256; low, high, space = 10, 245, ' ' # Thresholds
    if not ws: return lt
    try: b_idx, _ = max(enumerate(ws), key=lambda i: i[1]); bright = chr(b_idx + 32)
    except ValueError: bright = '#'
    for lvl in range(256):
        if lvl <= low: lt[lvl] = space
        elif lvl >= high: lt[lvl] = bright
        else:
            norm_b = lvl/255.0; b_diff, b_idx = 1.0, 0
            for idx, w in enumerate(ws):
                diff = abs(w - norm_b) # Find char with closest weight
                if diff < b_diff: b_diff, b_idx = diff, idx
            lt[lvl] = chr(b_idx + 32)
    return lt

def extract_f(gif, fill=True): # Extract frames, make transparent black if fill=True
    frms, idx = [], 0
    while True:
        try:
            gif.seek(idx); fdata = gif.convert('RGBA')
            if fill: nf=Image.new('RGBA', gif.size,(0,0,0,255)); nf.paste(fdata,(0,0),fdata); frms.append(nf)
            else: frms.append(fdata)
            idx += 1
        except EOFError: break
    return frms

def to_ascii(img, cw, ch, lt):
    (ix, iy) = img.size; term_aspect = 1.85 # Terminal char aspect ratio correction
    th = max(1, int(iy / ch)); tw = max(1, int(ix * term_aspect / ch)) # Target size
    img = img.resize((tw, th), Image.LANCZOS).convert("L"); px = img.getdata()
    rows = []; p_idx = 0
    for _ in range(th): rows.append("".join([lt[px[p_idx + x]] for x in range(tw)])); p_idx += tw
    return "\n".join(rows)

def animate(frms, fps=30, iters=20, clr=True):
    pause = 1.0 / max(1, fps); home = "\x1b[H" # ANSI home cursor
    for _ in range(iters):
        t_start = time.perf_counter()
        for frm in frms:
            if clr: sys.stdout.write(home)
            sys.stdout.write(frm); sys.stdout.flush()
            elapsed = time.perf_counter() - t_start
            time.sleep(max(0, pause - elapsed)); t_start = time.perf_counter() # Frame timing
    sys.stdout.write("\n"); sys.stdout.flush()

# --- Main ---
save_path = None;
args = sys.argv[1:]
gif_path = args[0] if args else None

if not gif_path: print("Specify GIF path"); sys.exit(1)
if "--save" in args:
    try: save_path = args[args.index("--save") + 1]
    except IndexError: pass

gif = Image.open(gif_path)
font = ImageFont.load_default(); weights, cw, ch = calc_ws(font); lut = create_lt(weights)
img_frms = extract_f(gif); ascii_frms = [f for f in [to_ascii(f, cw, ch, lut) for f in img_frms] if f]

if save_path:
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(ascii_frms, f); print(f"Saved to {save_path}")

if ascii_frms: animate(ascii_frms, fps=22)
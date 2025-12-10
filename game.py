# 「Pyxelでアクションゲームを作る」　ソースコード変更箇所確認用
# 6-02　縦方向のスクロール

import pyxel
pyxel.init(256,256,title="ハマトラ")
pyxel.load("mygame.pyxres")

STAGE_WIDTH = 256 * 8
STAGE_HEIGHT = 256 * 2
LEFT_LINE = 96
RIGHT_LINE = pyxel.width - 130
UPPER_LINE = 40
BOTTOM_LINE = pyxel.height - 40
scroll_x = 0
scroll_y = 0
x = 8
y = 420
dx = 0
dy = 0
pldir = 1
jump = 0
score = 0

# --- プレイヤー 16×16 に対応した 9点チェック ---
chkpoint = [
    (1,1), (8,1), (15,1),        # 上
    (1,8), (8,8), (15,8),        # 中
    (1,15),(8,15),(15,15),       # 下
]

# --- 16×16 壁タイル（左上１つだけ書けば OK）---
# 例：(4,3) のタイルを左上にした 2×2 が壁
WALL_16 = [
    (4, 3),
    (0, 2),
    (2, 2),
    (7, 2),
    # 必要なだけ追加！
]

# --- 16×16 ダメージタイル（左上１つだけ書けば OK）---
# 指定されたタイル値 U,V = (64,0), (80,0), (96,0), (128,0) は 8x8 タイル基準なので、
# 16x16 ブロックの左上タイルを定義します。
# U値を8で割って U座標、V値を8で割って V座標を取得します。
# 例：(64,0) -> U: 64/8 = 8, V: 0/8 = 0 -> (8, 0)
DAMAGE_16 = [ # <--- 追加・修正箇所
    (8, 0),     # (64, 0) 8x8 タイルに対応する 16x16 ブロックの左上
    (10, 0),    # (80, 0) 8x8 タイルに対応する 16x16 ブロックの左上
    (12, 0),    # (96, 0) 8x8 タイルに対応する 16x16 ブロックの左上
    (16, 0),    # (128, 0) 8x8 タイルに対応する 16x16 ブロックの左上
]


# --- 壁タイルか判定（16×16 の4タイルを自動判定） ---
def is_wall_tile(tile):
    u, v = tile

    for wu, wv in WALL_16:
        # 16×16 を構成する 2×2 タイル
        if tile in [
            (wu, wv),    # 左上
            (wu+1, wv),  # 右上
            (wu, wv+1),  # 左下
            (wu+1, wv+1) # 右下
        ]:
            return True

    return False

# --- ダメージタイルか判定（16×16 の4タイルを自動判定） --- <--- 追加箇所
def is_damage_tile(tile):
    u, v = tile

    for du, dv in DAMAGE_16:
        # 16×16 を構成する 2×2 タイル
        if tile in [
            (du, dv),    # 左上
            (du+1, dv),  # 右上
            (du, dv+1),  # 左下
            (du+1, dv+1) # 右下
        ]:
            return True

    return False


# --- 壁判定本体（9点判定） ---
def chkwall(cx, cy):
    c = 0

    # 画面外判定（必要なら調整）
    if cx < 0 or STAGE_WIDTH - 8 < cx:
        c += 1
    if STAGE_HEIGHT < cy:
        c += 1

    # 衝突判定
    for cpx, cpy in chkpoint:
        xi = (cx + cpx) // 8
        yi = (cy + cpy) // 8

        tile = pyxel.tilemap(0).pget(xi, yi)

        if is_wall_tile(tile):
            c += 1

    return c





def update():
    global scroll_x,scroll_y,x,y,dx,dy,pldir,jump,score

    # 操作判定
    if pyxel.btn(pyxel.KEY_LEFT):
        if -3 < dx:
            dx = dx - 1
        pldir = -1
    elif pyxel.btn(pyxel.KEY_RIGHT):
        if dx < 3:
            dx = dx + 1
        pldir = 1
    else:
        dx = int(dx*0.7)

    # 横方向の移動
    lr = pyxel.sgn(dx)
    loop = abs(dx)
    while 0 < loop :
        if chkwall( x + lr, y) != 0:
            dx = 0
            break
        x = x + lr
        loop = loop -1

    # 左方向へのスクロール
    if x < scroll_x + LEFT_LINE:
        scroll_x = x - LEFT_LINE
        if scroll_x < 0:
            scroll_x = 0

    # 右方向へのスクロール
    if scroll_x + RIGHT_LINE < x:
        scroll_x = x - RIGHT_LINE
        if STAGE_WIDTH - pyxel.width < scroll_x:
            scroll_x = STAGE_WIDTH - pyxel.width

    # ジャンプと落下
    if jump == 0:
        if chkwall(x,y+1) == 0:
            jump = 2  # 床が無ければ落下
        if pyxel.btnp(pyxel.KEY_SPACE):
            dy = 8
            jump = 1   # ジャンプ開始
    else:
        dy = dy - 1
        if dy < 0:
            jump = 2   # 頂点で落下開始

    ud = pyxel.sgn(dy)
    loop = abs(dy)
    while 0 < loop :
        if chkwall(x, y - ud) != 0:
            dy = 0
            if jump == 1:
                jump = 2   # 壁にぶつかって落下
            elif jump == 2:
                jump = 0   # 着地　落下終了
            break
        y = y - ud
        loop = loop -1

    # 上方向へのスクロール
    if y < scroll_y + UPPER_LINE:
        scroll_y = y - UPPER_LINE
        if scroll_y < 0:
            scroll_y = 0

    # 下方向へのスクロール
    if scroll_y + BOTTOM_LINE < y:
        scroll_y = y - BOTTOM_LINE
        if STAGE_HEIGHT - pyxel.height < scroll_y:
            scroll_y = STAGE_HEIGHT - pyxel.height

    # コイン判定
    xi = (x + 4)//8
    yi = (y + 4)//8
    if (14,0) == pyxel.tilemap(0).pget(xi,yi):
        score = score + 1
        pyxel.tilemap(0).pset(xi,yi,(0,0))

    
    # --- ダメージブロック判定とゲームオーバー処理 --- <--- 追加箇所
    for cpx, cpy in chkpoint:
        xi = (x + cpx) // 8
        yi = (y + cpy) // 8
        tile = pyxel.tilemap(0).pget(xi, yi)

        if is_damage_tile(tile):
            # ダメージブロックに触れたらゲームオーバー
            pyxel.quit()
            return
    # ---------------------------------------------
    
    return

def draw():
    pyxel.cls(0)
    
    pyxel.camera()
    pyxel.bltm(0,0, 0, scroll_x,scroll_y, pyxel.width,pyxel.height, 0)

    pyxel.camera(scroll_x,scroll_y)
    pyxel.blt( x, y, 0,  16, 0, pldir*16,16, 0)

    if 10 == score :
        pyxel.text(scroll_x+45,scroll_y+56,"FINISH!",7)

    return



pyxel.run(update, draw)


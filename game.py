import pygame
import random
import sys
import os

# 初期化と画面設定
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("2D Run Game")
clock = pygame.time.Clock()
FONT = pygame.font.Font("assets/mini-wakuwaku.otf", 80)
text_surface = FONT.render("スコア：123", True, (0, 0, 0))
screen.blit(text_surface, (50, 50))

# === 定数 ===
GROUND_Y = HEIGHT - 50

PLAYER_SHRINK = (0.9, 0.1)
ENEMY_SHRINK = (0.1, 0.2)

# === 背景画像 ===
background_img = pygame.image.load("background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# === スコア管理 ===
def load_highscore():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# === プレイヤークラス ===
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_images = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join("assets", f"run{i}.png")).convert_alpha()
            self.run_images.append(pygame.transform.scale(img, (600, 280)))

        self.jump_image = pygame.image.load(os.path.join("assets", "jump.png")).convert_alpha()
        self.jump_image = pygame.transform.scale(self.jump_image, (600, 280))

        self.image = self.run_images[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (200, GROUND_Y)

        self.vel_y = 0
        self.jump_power = -22
        self.gravity = 0.8
        self.on_ground = True

        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        # 当たり判定のオフセット（右ずれを修正）
        self.hitbox_offset_x = -40  # 左に40ピクセル移動（適宜調整）
        self.hitbox_offset_y = 0    # 上下移動なし

    def get_hitbox(self):
        """実際の当たり判定矩形を計算"""
        # 縮小率を取得
        w_ratio, h_ratio = PLAYER_SHRINK
        shrink_w = int(self.rect.width * w_ratio)
        shrink_h = int(self.rect.height * h_ratio)
        
        # 矩形を縮小
        hitbox = self.rect.inflate(-shrink_w, -shrink_h)
        
        # 位置調整
        hitbox.x += self.hitbox_offset_x
        hitbox.y += self.hitbox_offset_y
        
        return hitbox

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.on_ground:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_images)
            self.image = self.run_images[self.frame_index]
        else:
            self.image = self.jump_image

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

            jump_sound.stop()
            jump_sound.play()

# === 敵クラス ===
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, speed=6):  # ← speed を受け取れるように
        super().__init__()
        image = pygame.image.load(os.path.join("assets", "enemy.png")).convert_alpha()
        self.image = pygame.transform.scale(image, (180, 200))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = GROUND_Y + 10  # 少し下に潜らせる
        self.speed = speed  # ここで受け取ったspeedを使用する（修正箇所）

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    # 衝突判定関数の修正
def collide_rect_shrink(sprite1, sprite2, shrink1, shrink2):
    # プレイヤーの当たり判定
    w_ratio1, h_ratio1 = shrink1
    shrink_w1 = int(sprite1.rect.width * w_ratio1)
    shrink_h1 = int(sprite1.rect.height * h_ratio1)
    r1 = sprite1.rect.inflate(-shrink_w1, -shrink_h1)
    r1.x += sprite1.hitbox_offset_x  # オフセット適用

    # 敵の当たり判定
    w_ratio2, h_ratio2 = shrink2
    shrink_w2 = int(sprite2.rect.width * w_ratio2)
    shrink_h2 = int(sprite2.rect.height * h_ratio2)
    r2 = sprite2.rect.inflate(-shrink_w2, -shrink_h2)

    return r1.colliderect(r2)

# === ゲームオーバー画面 ===
def show_game_over(score, highscore):
    screen.fill((30, 30, 30))
    text1 = FONT.render("GAME OVER", True, (255, 0, 0))
    text2 = FONT.render(f"Score: {score}", True, (255, 255, 255))
    text3 = FONT.render(f"High Score: {highscore}", True, (255, 255, 0))
    text4 = FONT.render("Press SPACE to Restart", True, (200, 200, 200))

    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 100))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 250))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, 350))
    screen.blit(text4, (WIDTH // 2 - text4.get_width() // 2, 550))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# === 音楽の初期化と再生 ===
pygame.mixer.init()
pygame.mixer.music.load("assets/Pixelated Legends.mp3")
pygame.mixer.music.set_volume(0.5)  # 音量50%
pygame.mixer.music.play(-1)  # 無限ループ再生

# === 効果音読み込み ===
jump_sound = pygame.mixer.Sound("assets/jump,_8-bit,_game.wav")
jump_sound.set_volume(0.5)  # 任意で音量調整（0.0〜1.0）

# === メイン関数 ===
def main():
    bg_x = 0
    bg_speed = 2
    highscore = load_highscore()

    while True:
        player = Player()
        player_group = pygame.sprite.Group(player)
        enemy_group = pygame.sprite.Group()
        enemy_timer = 0
        enemy_interval = 150

        start_ticks = pygame.time.get_ticks()
        game_over = False

        # === 衝突判定用の定数 ===
        PLAYER_SHRINK = (0.9, 0.1)  # (幅縮小率, 高さ縮小率)
        ENEMY_SHRINK = (0.4, 0.3)   # (幅縮小率, 高さ縮小率)

        while not game_over:
            clock.tick(60)
            # 経過時間と敵スピード計算
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            enemy_speed = min(8 + seconds // 5, 25)
            bg_speed = enemy_speed * 0.3  # 背景も連動

            bg_x -= bg_speed
            if bg_x <= -WIDTH:
                bg_x = 0

            # 背景と地面の描画
            screen.blit(background_img, (bg_x, 0))
            screen.blit(background_img, (bg_x + WIDTH, 0))
            pygame.draw.rect(screen, (0, 0, 0), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()

                    if event.key == pygame.K_ESCAPE:  # ← ここ！
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.FINGERDOWN:
                    player.jump()

            # 毎フレーム更新の中で
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            enemy_speed = min(8 + seconds // 5, 25)

            # 敵の生成（修正箇所）
            enemy_timer += 1
            if enemy_timer > enemy_interval:
                # enemy_speedを渡して敵を生成
                enemy = Enemy(WIDTH + 50, speed=enemy_speed)
                enemy_group.add(enemy)
                enemy_timer = 0
                enemy_interval = random.randint(60, 120)  # 次回の間隔を再設定

            # 更新
            player_group.update()
            enemy_group.update()

            # === メインループ内の衝突チェック ===
            for enemy in enemy_group:
                # プレイヤーと敵の当たり判定をチェック
                if collide_rect_shrink(player, enemy, 
                                      shrink1=PLAYER_SHRINK, 
                                      shrink2=ENEMY_SHRINK):
                    game_over = True
                    break

            # ===== 修正箇所1: ゲームオーバー処理 =====
            if game_over:
                seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                if seconds > highscore:
                    highscore = seconds
                    save_highscore(highscore)
                show_game_over(seconds, highscore)
                break  # ループを抜けてゲーム再開

            # 描画
            player_group.draw(screen)
            enemy_group.draw(screen)



            # スコアの描画
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            score_surf = FONT.render(f"Score: {seconds}", True, (0, 0, 0))
            screen.blit(score_surf, (10, 10))

            pygame.display.flip()

# === 実行開始 ===
if __name__ == "__main__":
    main()
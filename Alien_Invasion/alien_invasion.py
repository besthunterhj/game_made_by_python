import pygame
import game_function as gf
from settings import Settings
from ship import Ship
from pygame.sprite import Group
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


def run_game():
    # 初始化游戏并创建一个屏幕对象
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height)
    )
    pygame.display.set_caption("Alien Invasion   --powered by Pygame made by Wong")

    # 创建Play和Help按钮
    play_button = Button(ai_settings, screen, "Play", -125, (0, 255, 0))
    help_button = Button(ai_settings, screen, "Help", 125, (255, 0, 0))

    # 创建一艘飞船
    ship = Ship(ai_settings, screen)

    # 创建一个用于存储子弹的编组
    bullets = Group()

    # 创建一个外星人
    aliens = Group()

    # 创建外星人群
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # 初始化背景音乐
    pygame.mixer.init()
    # 加载音乐
    pygame.mixer.music.load("bgm/03.mp3")

    # 创建一个用于存储游戏统计信息的实例
    stats = GameStats(ai_settings)

    # 创建一个记分牌
    score = Scoreboard(ai_settings, screen, stats)

    # 开始游戏的主循环
    while True:
        # 检查有无音乐流
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

        # 监视键盘和鼠标事件
        gf.check_events(ai_settings, screen, stats, score, ship, aliens, bullets, play_button, help_button)

        # 当游戏处于活动状态才正常开始
        if stats.game_active:
            # 船的每次移动都需要更新位置以便重新绘制屏幕
            ship.update()

            # 子弹的移动同理，也要不断更换位置以便重新绘制屏幕
            gf.update_bullet(ai_settings, screen, stats, score, ship, aliens, bullets)

            # 每次外星人移动都需要重新绘制屏幕
            gf.update_aliens(ai_settings, screen, stats, score, ship, aliens, bullets)

        # 每次循环时都重新绘制屏幕
        gf.update_screen(ai_settings, screen, stats, score, ship, aliens, bullets, play_button, help_button)


run_game()

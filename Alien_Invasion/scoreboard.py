import pygame.font
from pygame.sprite import Group
from ship import Ship


class Scoreboard():
    """这是一个用来显示分数的类"""

    def __init__(self, ai_settings, screen, stats):
        """初始化显示分数涉及的属性"""
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats = stats
        self.score_image = None
        self.score_rect = None
        self.high_score_image = None
        self.high_score_rect = None
        self.level_image = None
        self.level_rect = None
        self.ships = None

        # 显示得分信息时使用的字体设置
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont("Consolas", 28)

        # 准备包含最高得分、飞船个数、当前游戏等级和初始得分的图像
        self.prep_images()

    def prep_images(self):
        # 调用绘制得分的函数
        self.prep_score()

        # 调用绘制最高得分的函数
        self.prep_high_score()

        # 调用绘制当前等级的函数
        self.prep_level()

        # 调用绘制飞船个数的函数
        self.prep_ships()

    def prep_score(self):
        """将得分转化为屏幕中渲染的图像"""
        # 将得分圆整为10的倍数
        rounded_score = int(round(self.stats.score, -1))
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color,
                                            self.ai_settings.background_color)

        # 将得分放在屏幕右上角
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 0

    def prep_high_score(self):
        """将最高得分转换为屏幕中渲染的图像"""
        high_score = int(round(self.stats.high_score, -1))
        high_score_str = "{:,}".format(high_score)
        string2 = "Highest Score:  " + high_score_str
        self.high_score_image = self.font.render(string2, True, self.text_color,
                                                 self.ai_settings.background_color)

        # 将最高得分放在屏幕顶部中央
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.screen_rect.top

    def prep_level(self):
        """将等级转换为屏幕上渲染的图像"""
        string3 = "Level: " + str(self.stats.level)
        self.level_image = self.font.render(string3, True, self.text_color,
                                            self.ai_settings.background_color)

        # 将等级放在得分的下面
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 5

    def prep_ships(self):
        """显示还余下多少艘船"""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_settings, self.screen)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 0
            self.ships.add(ship)

    def show_score(self):
        """在屏幕右上角显示得分"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        # 在左上角显示飞船个数
        self.ships.draw(self.screen)

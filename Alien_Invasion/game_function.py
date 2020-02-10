import sys
import pygame
import json
import os
from bullet import Bullet
from alien import Alien
from time import sleep


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """响应键盘某键的按下"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_UP:
        ship.moving_top = True
    elif event.key == pygame.K_DOWN:
        ship.moving_bottom = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_ESCAPE:
        sys.exit()


def check_high_score(stats, score):
    """检查是否诞生了新的最高得分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        score.prep_high_score()


def fire_bullet(ai_settings, screen, ship, bullets):
    """如果screen中的子弹没有超过限制，那么让飞船发射子弹"""
    # 创建一颗子弹，将其加入到编组bullets中
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    """响应键盘某键松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_UP:
        ship.moving_top = False
    elif event.key == pygame.K_DOWN:
        ship.moving_bottom = False


def check_events(ai_settings, screen, stats, score, ship, aliens, bullets, play_button, help_button):
    """响应鼠标点击和键盘事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_help_button(ai_settings, screen, stats, help_button, mouse_x, mouse_y)
            check_play_button(ai_settings, screen, stats, score, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def check_help_button(ai_settings, screen, stats, help_button, mouse_x, mouse_y):
    """当用户单击Help按钮时，弹出提示"""
    help_button_checked = help_button.rect.collidepoint(mouse_x, mouse_y)
    if help_button_checked and not stats.game_active:

        # 打开Readme文件
        os.startfile("readme.txt")


def check_play_button(ai_settings, screen, stats, score, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    """当用户单击Play按钮时，游戏开始"""
    button_checked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_checked and not stats.game_active:
        # 重置游戏设置
        ai_settings.initialize_dynamic_settings()

        # 隐藏光标，提升游戏体验
        pygame.mouse.set_visible(False)

        # 重置游戏统计信息
        stats.reset_stats()
        stats.game_active = True

        # 重置记分牌的相关图像
        score.prep_images()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并让飞船居中
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def check_bullet_alien_collisions(ai_settings, screen, stats, score, ship, aliens, bullets):
    """检查是否有子弹击中了外星人， 如果有，就是删除相应的子弹和外星人"""
    # 若将第一个True改为False，则会成为穿透子弹
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        # 遍历collisions（碰撞情况）返回的字典中的值（即一颗子弹撞到的外星人），如果一颗子弹射中了多个外星人，则单个分数乘上击落个数
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            score.prep_score()
        check_high_score(stats, score)

    if len(aliens) == 0:
        # 若当前外星人被全部击落，则新建另一群，并删除屏幕现有子弹
        start_new_level(ai_settings, screen, stats, score, ship, aliens, bullets)


def start_new_level(ai_settings, screen, stats, score, ship, aliens, bullets):
    """当一个等级的外星人被消灭后，开始下一等级"""

    bullets.empty()  # 删除屏幕现有子弹
    ship.center_ship()  # 将飞船移回起始点
    ai_settings.increase_speed()    # 游戏机制提速

    # 提高等级
    stats.level += 1
    score.prep_level()

    sleep(0.5)
    create_fleet(ai_settings, screen, ship, aliens)  # 创建一群新的外星人


def update_bullet(ai_settings, screen, stats, score, ship, aliens, bullets):
    """更新子弹的位置，并删除已经飞出Screen的子弹"""
    # 更新子弹的位置
    bullets.update()

    # 删除已经飞出去的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, score, ship, aliens, bullets)


def get_number_aliens_x(ai_settings, alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width  # 可容纳外星人的屏幕宽度
    number_aliens_x = int(available_space_x / (2 * alien_width))  # 一行能放置的外星人数目
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """计算可以容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """创建一个外星人并将其加入当前行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width  # 真正在屏幕中的是rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人，并计算一行可容纳多少个外星人
    # 外星人之间的间距（上下左右）是它的宽度
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    # 创建多行外星人，即生成一群外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """将整群外星人下移，并改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def update_aliens(ai_settings, screen, stats, score, ship, aliens, bullets):
    """检查是否有外星人位于屏幕边缘，更新外星人群中所有外星人的位置"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检测外星人和飞船有无发生碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, score, ship, aliens, bullets)

    # 检查是否有外星人到达屏幕底部
    check_aliens_bottom(ai_settings, screen, stats, score, ship, aliens, bullets)


def ship_hit(ai_settings, screen, stats, score, ship, aliens, bullets):
    """响应被外星人撞到了飞船"""
    if stats.ships_left > 0:  # 当飞船还有生命值剩余时
        # 将ships_left 减去 1
        stats.ships_left -= 1

        # 更新飞船个数并绘制到左上角
        score.prep_ships()

        # 清空外星人列表和子弹列表（清屏）
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并将飞船放回到屏幕底部中央（初始点）
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)

    else:
        # 游戏结束，导出最高分到本地
        if stats.high_score > ai_settings.local_highest_score:
            filename = "highest_score.json"
            with open(filename, "w") as f_obj:
                json.dump(stats.high_score, f_obj)

        # 游戏结束，游戏活动状态设为未开始
        stats.game_active = False
        # 游戏结束后，让鼠标可见
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, screen, stats, score, ship, aliens, bullets):
    """检查是否有外星人到达屏幕底部"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞一样处理
            ship_hit(ai_settings, screen, stats, score, ship, aliens, bullets)
            break


def update_screen(ai_settings, screen, stats, score, ship, aliens, bullets, play_button, help_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    # 每次循环时都重新绘制屏幕,这里设置它的背景颜色
    screen.fill(ai_settings.background_color)

    # 在飞船和外星人后面重新绘制所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    # 绘制飞船
    ship.blitme()

    # 绘制一群外星人
    aliens.draw(screen)

    # 实时更新显示游戏得分
    score.show_score()

    # 如果游戏处于非活动状态，就显示Play按钮
    if not stats.game_active:
        play_button.draw_button()
        help_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()

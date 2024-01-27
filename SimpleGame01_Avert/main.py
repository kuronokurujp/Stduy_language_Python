#!/usr/bin/env python
import sys
import pygame
import asyncio
import threading
import time
from random import randint
from pygame.rect import Rect
from pygame.locals import QUIT, KEYDOWN, K_SPACE


class GameObject(object):
    __image: pygame.Surface = None
    __x: float = 0.0
    __y: float = 0.0
    __current_anim_idx: int = 0
    __anim_rect: list[Rect] = list()
    __anim_loop_count: int = 0
    __speed: float = 0.0

    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, x: float):
        self.__x = x

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, y: float):
        self.__y = y

    @property
    def anim_loop_count(self) -> int:
        return self.__anim_loop_count

    def get_size(self) -> tuple[float, float]:
        current_rect: Rect = self.__anim_rect[self.__current_anim_idx]
        return (current_rect.top, current_rect.bottom)

    def __init__(
        self, img_filepath: str, anim_speed: float, anim_rect: list[Rect]
    ) -> None:
        self.__image = pygame.image.load(img_filepath)
        self.__anim_rect = anim_rect
        self.__current_anim_idx = 0
        self.__x = 0
        self.__y = 0
        self.__speed = anim_speed
        self.__anim_loop_count = 0
        self.__thread = threading.Thread(daemon=True, target=self.__update)

    def play(self):
        self.__thread.start()

    def __update(self):
        while True:
            time.sleep(self.__speed / 60.0)
            self.__current_anim_idx = (self.__current_anim_idx + 1) % len(
                self.__anim_rect
            )
            if self.__current_anim_idx == 0:
                self.__anim_loop_count += 1

    def draw(self, surface: pygame.Surface):
        current_rect: Rect = self.__anim_rect[self.__current_anim_idx]
        size: tuple[int, int] = current_rect.size
        surface.blit(
            self.__image, (self.__x - size[0] / 2, self.__y - size[1] / 2), current_rect
        )


async def main():
    pygame.init()

    surface: pygame.Surface = pygame.display.set_mode((800, 600))
    fps_clock: pygame.time.Clock = pygame.time.Clock()
    pygame.key.set_repeat(5, 5)

    velocity: float = 0.0
    score: int = 0
    slope: int = randint(1, 6)
    sysfont: pygame.font.Font = pygame.font.SysFont(None, 36)
    ship_obj: GameObject = GameObject(
        "res/img/airship.png",
        1,
        [
            Rect(0, 32, 32, 32),
            Rect(32, 32, 32, 32),
            Rect(64, 32, 32, 32),
        ],
    )
    ship_obj.x = 16
    ship_obj.y = 250
    ship_obj.play()

    bom_eff_obj: GameObject = GameObject(
        "res/img/bom_eff.png",
        3,
        [
            Rect(240 * 0, 0, 240, 240),
            Rect(240 * 1, 0, 240, 240),
            Rect(240 * 2, 0, 240, 240),
            Rect(240 * 3, 0, 240, 240),
            Rect(240 * 4, 0, 240, 240),
        ],
    )

    holes: list[Rect] = list()

    walls: int = 100
    wall_size_x: float = 10
    for xpos in range(walls):
        holes.append(Rect(xpos * wall_size_x, 100, 10, surface.get_size()[1] * 0.8))
    game_over: bool = False
    accel: float = 0.1
    hole_speed: float = 1
    step: int = 0

    while True:
        match step:
            case 0:
                is_space_down: bool = False
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            is_space_down = True

                if not game_over:
                    score += 1
                    velocity += -accel if is_space_down else accel

                    if holes[0].x <= -wall_size_x * 2:
                        edge: Rect = Rect(
                            holes[-1].x + wall_size_x,
                            holes[-1].y,
                            10,
                            surface.get_size()[1] * 0.8,
                        )
                        test: Rect = edge.move(0, slope)

                        if test.top <= 0 or test.bottom >= surface.get_size()[1]:
                            slope = randint(1, 6) * (-1 if slope > 0 else 1)
                            edge.inflate_ip(0, -10)
                            edge.move_ip(0, slope)
                        else:
                            edge = test

                        holes.append(edge)
                        del holes[0]

                    holes = [x.move(-hole_speed, 0) for x in holes]

                    ship_obj.y = ship_obj.y + velocity
                    if holes[0].top > ship_obj.y or holes[0].bottom < ship_obj.y:
                        bom_eff_obj.x = ship_obj.x
                        bom_eff_obj.y = ship_obj.y
                        bom_eff_obj.play()
                        step += 1

        surface.fill((0, 255, 0))
        for hole in holes:
            pygame.draw.rect(surface, (0, 0, 0), hole)

        match step:
            case 0:
                ship_obj.draw(surface)
            case 1:
                if 0 < bom_eff_obj.anim_loop_count:
                    step += 1
                bom_eff_obj.draw(surface)

        score_image: pygame.surface = sysfont.render(
            "score is {}".format(score), True, (0, 0, 225)
        )

        surface.blit(score_image, (600, 20))

        pygame.display.update()

        # FPS値を設定
        fps_clock.tick(60)


if __name__ == "__main__":
    asyncio.run(main())

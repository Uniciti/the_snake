from random import choice
from typing import Optional

import pygame as pg

pg.init()

"""Константы для размеров поля и сетки"""
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MENU_WIDTH, MENU_HEIGHT = 200, 200
TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT = MENU_WIDTH, 50
MIDDLE_SCREEN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
MENU_FONT_SIZE = 35
TITLE_FONT_SIZE = 60
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FIELD_SIZE = GRID_WIDTH * GRID_HEIGHT
FIELD_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

"""Направления движения"""
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

"""Цвета объектов и игрового поля."""
BOARD_BACKGROUND_COLOR = (47, 71, 22)
BORDER_COLOR = (93, 216, 228)
MAIN_MENU_COLOR = (200, 200, 200)
MENU_BORDER_COLOR = (25, 25, 25)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (107, 99, 92)
DEFAULT_COLOR = (0, 0, 0)

"""Управление скорость и замедлением игры."""
GAME_SPEED = 60
SLOW_SPEED = 10

"""Количество игровых объектов на поле."""
DEFAULT_COUNT_APPLES = 20
DEFAULT_COUNT_STONES = 10
DEFAULT_STONE_WEIGHT = 5

"""Клавиши."""
KEY_ENTER = 13

"""Основной эран игры."""
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

"""Меню игры."""
main_menu = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
main_menu_rect = main_menu.get_rect(center=MIDDLE_SCREEN)
title_menu = pg.Surface((TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT))
title_menu_rect = main_menu.get_rect(
    center=(SCREEN_WIDTH // 2, main_menu_rect.y + TITLE_MENU_HEIGHT)
)

"""Объект в котором будет хранится фон для игры."""
background_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

"""Создание фона для созданиея на ней текстуры (например песка)."""
background_surface.fill(BOARD_BACKGROUND_COLOR)

"""Отрисовка фона на экране"""
screen.blit(background_surface, (0, 0))

"""Создаем объект для управления заголовком игры."""
game_caption = pg.display.set_caption
game_caption('Змейка')

"""Создаем объект текст."""
menu_font = pg.font.Font(None, MENU_FONT_SIZE)
title_font = pg.font.Font(None, TITLE_FONT_SIZE)

"""Объект для управления временем."""
clock = pg.time.Clock()


class GameObject():
    """Базовый класс от которого наследуются все игровые объекты."""

    def __init__(self,
                 body_color: tuple[int, int, int] = DEFAULT_COLOR,
                 name: Optional[str] = None) -> None:
        """Инициализирует новый экземпляр класса {GameObject}."""
        self.position: tuple[int, int] = MIDDLE_SCREEN
        self.body_color = body_color
        self.name = name or str(type(self).__name__).lower()

    def draw(self) -> None:
        """Базовый метод рисования объектов. Определяется для
        каждого подкласса отдельно.
        """

    def draw_cell(self, position: tuple[int, int],
                  color: Optional[tuple[int, int, int]] = None,
                  tail: bool = False) -> None:
        """Отрисовывает ячейку заданых размеров."""
        color = color or self.body_color

        rect = pg.Rect(
            position,
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, color, rect)
        if not tail:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self,
                           used_cells: list[tuple[int, int]] = []) -> None:
        """Задаёт объекту случайные координаты."""
        self.position = choice(tuple(FIELD_CELLS - set(used_cells)))


class Apple(GameObject):
    """Класс описывающий игровой объект Яблоко."""

    def __init__(self,
                 body_color: tuple[int, int, int] = APPLE_COLOR,
                 used_cells: list = [],
                 name: Optional[str] = None) -> None:
        """Инициализирует экземпляр класса {Apple}."""
        super().__init__(body_color, name)
        self.randomize_position(used_cells)

    def draw(self) -> None:
        """Рисует объект на экране."""
        self.draw_cell(self.position)


class Stone(GameObject):
    """Класс описывающий игровой объект Камень."""

    def __init__(self,
                 body_color: tuple[int, int, int] = STONE_COLOR,
                 used_cells: list = [],
                 weight: int = DEFAULT_STONE_WEIGHT) -> None:
        """Инициализирует экземпляр класса."""
        super().__init__(body_color)
        self.randomize_position(used_cells)
        self.weight = weight

    def draw(self) -> None:
        """Рисует объет на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс описывающий игровой объект 'Змейка'."""

    def __init__(self,
                 body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        """Инициализирует экземпляр класса {Snake}."""
        super().__init__(body_color)
        self.reset()
        self.direction: tuple[int, int] = RIGHT

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [self.position]
        self.length = 1
        self.last: Optional[tuple[int, int]] = None
        self.direction = choice([RIGHT, LEFT, UP, DOWN])

    def update_direction(self, direction: tuple[int, int]) -> None:
        """Обновляет направление движения змейки."""
        self.direction = direction

    def new_head(self) -> tuple[int, int]:
        """Возвращает координаты новой головы."""
        pos_x, pos_y = self.get_head_position()
        return (
            (pos_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (pos_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

    def grow_up(self, new_segment: tuple[int, int]) -> None:
        """Увиличивает змейку на один сегмент."""
        self.positions.insert(0, new_segment)
        self.update_size_info()

    def cut_tail(self) -> None:
        """Уменьшает змейку на один сегмент с конца."""
        self.positions.pop()
        self.update_size_info()

    def update_size_info(self) -> None:
        """Обновляет информацию о размере змейки."""
        self.length = len(self.positions)
        game.update_snake_length(self.length)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self) -> None:
        """Отрисовывает змейку на экране и если {last} содержит
        координаты старого сегмента, затирает его.
        """
        for position in self.positions:
            self.draw_cell(position, SNAKE_COLOR)

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, True)

    def move(self, new_head: tuple[int, int]) -> None:
        """Сдвигает змейку на одну клетку игрового поля."""
        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def can_bite_itself(self, new_head: tuple[int, int]) -> bool:
        """Проверяет может ли следующим ходом змейка укусить сама себя."""
        return new_head in self.positions

    def try_bite(self, new_head: tuple[int, int], object: GameObject) -> bool:
        """Принимает на вход объект и проверяет можно ли его укусить."""
        return object.position == new_head


class GameManager():
    """Класс для управления общей логикой игры."""

    def __init__(self) -> None:
        """Инициализирует экземпляр класса
        и базовые атрибуты.
        """
        self.reset: bool = False
        self.new_game: bool = True
        self.__game_is_run: bool = False
        self.__slow_count: int = 0
        self.__snake_length: int = 1
        self.__eaten_apples: int = 0
        self.__status_menu: bool = True
        self.__menu_value: int = 0
        self.__menu_sections: list = [
            'Новая игра',
            'Продолжить',
            'Выход'
        ]

    def is_run(self) -> bool:
        """Возвращяет {True} если игра включена и {False} если нет."""
        return self.__game_is_run

    def switch_on(self) -> None:
        """Переключатель игры в положение - включено."""
        self.__game_is_run = True

    def switch_off(self) -> None:
        """Переключатель игры в положение - выключено."""
        self.__game_is_run = False

    def menu_is_open(self) -> bool:
        """Отображает статус меню (активно / не активно)."""
        return self.__status_menu

    def close_menu(self) -> None:
        """Закрывает меню."""
        self.__status_menu = False

    def open_menu(self) -> None:
        """Открывает меню."""
        self.__status_menu = True

    def menu_up(self) -> None:
        """Передвижение по меню вверх."""
        self.__menu_value -= 1 if self.__menu_value > 0 else 0

    def menu_down(self) -> None:
        """Передвижение по меню вниз."""
        x = len(self.__menu_sections) - 1
        if self.__menu_value < x:
            self.__menu_value += 1
        else:
            self.__menu_value = x

    def menu_title(self) -> str:
        """Возвращает название выбранного пункта меню."""
        return self.__menu_sections[self.__menu_value]

    def get_menu_step(self) -> int:
        """Возвращает расстояние между пунктами меню исходя из размеров
        высоты меню, заданных константой {MENU_HEIGHT}, и их количества.
        """
        return (MENU_HEIGHT // (len(self.__menu_sections) + 1))

    def get_menu_list(self) -> list:
        """Возвращает списо из пунктов меню."""
        return self.__menu_sections

    def slow_mode(self, how_slow: int = SLOW_SPEED) -> bool:
        """Возвращает {False} пока действует замедление для выбранного
        блока кода, и {True} в момент когда код должен быть выполнен.
        Работает по принципу пропуска кадров, количество пропущенных
        кадров по умолчанию = {SLOW_SPEED}. Чем больше значение
        тем сильнее замедление.
        """
        self.__slow_count += 1
        if self.__slow_count > how_slow:
            self.__slow_count = 0

        return self.__slow_count == how_slow

    def update_eaten_apples(self) -> None:
        """Обновляет количество съеденных яблок."""
        self.__eaten_apples += 1

    def update_snake_length(self, length: int) -> None:
        """Обновляет значение длины зъмейки."""
        self.__snake_length = length

    def reset_info(self) -> None:
        """Сбрасывает информаци о текущей игре."""
        self.__snake_length = 1
        self.__eaten_apples = 0

    def info(self) -> str:
        """Выводит информацию об игре."""
        info = (
            f'Длина змейки: {self.__snake_length} || '
            f'Яблок съедено: {self.__eaten_apples} || '
        )
        return info

    def over(self) -> None:
        """Реализует логику при проигрыше"""
        pass


"""Инициализируем {GameManager} для возможнисти управлять всей логикой."""
game = GameManager()


def handle_keys(snake: Snake) -> None:
    """Отслеживает нажатые клавиши для управления змейкой."""
    keys = pg.key.get_pressed()
    direction: Optional[tuple[int, int]] = None

    if keys[pg.K_UP] and snake.direction != DOWN:
        direction = UP
    elif keys[pg.K_DOWN] and snake.direction != UP:
        direction = DOWN
    elif keys[pg.K_LEFT] and snake.direction != RIGHT:
        direction = LEFT
    elif keys[pg.K_RIGHT] and snake.direction != LEFT:
        direction = RIGHT

    if direction:
        snake.update_direction(direction)


def handle_keys_menu() -> None:
    """Отслеживает нажатые клавиши для управления в меню."""
    keys = pg.key.get_pressed()

    if keys[KEY_ENTER] and game.menu_title() == 'Новая игра':
        if game.new_game:
            game.new_game = False
        else:
            game.reset = True
        game.close_menu()
    elif (keys[KEY_ENTER] and game.menu_title() == 'Продолжить'
          and not game.new_game):
        game.close_menu()
    elif keys[KEY_ENTER] and game.menu_title() == 'Выход':
        game.switch_off()
        game.close_menu()

    if game.slow_mode(1):
        if keys[pg.K_UP]:
            game.menu_up()
        elif keys[pg.K_DOWN]:
            game.menu_down()


def quit_game() -> None:
    """Завершает игру."""
    pg.quit()
    raise SystemExit


def quit_pressed() -> bool:
    """Реализует логику нажатия на клавишу ESCAPE."""
    keys = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
            if game.new_game:
                game.switch_off()
            else:
                return True

    return False


def get_apples(count: int = DEFAULT_COUNT_APPLES,
               used_cells: list = []) -> tuple[list, list]:
    """Создает список хороших яблок. И возвращает его."""

    apples = []
    for _ in range(count):
        apple = Apple(used_cells=used_cells)
        apples.append(apple)
        used_cells.append(apple.position)

    return apples, used_cells


def get_stones(count: int = DEFAULT_COUNT_STONES,
               used_cells: list = []) -> tuple[list, list]:
    """Создает список камней. И возвращает его."""
    stones = []
    for _ in range(count):
        stone = Stone(used_cells=used_cells)
        stones.append(stone)
        used_cells.append(stone.position)

    return stones, used_cells


def get_all_position(snake: Snake, obstacles: list[GameObject]) -> list:
    """Возвращает список состоящий из координат всех
    созданных объектов, змейка в список не входит.
    """
    return [obstacle.position for obstacle in obstacles] + snake.positions


def init_game_obgects() -> tuple[Snake, list[GameObject]]:
    """Инициализирует все игровые объекты."""
    snake = Snake()
    used_cells = list.copy(snake.positions)
    good_apples, used_cells = get_apples(used_cells=used_cells)
    stones, used_cells = get_stones(used_cells=used_cells)

    return snake, [*good_apples, *stones]


def reset_game(new_game: bool = False) -> tuple[Snake, list[GameObject]]:
    """Сбрасывает змейку к исходному состоянию и задаёт ей случайное
    направление. Всем препятствиям задаются новые координаты. Если
    {new_game} = {True} информация об игре будет сброшена. Если
    {new_game} = {False} информация об игре будет обновлена.
    """
    if new_game:
        game.reset_info()
    else:
        game.update_snake_length(1)

    return init_game_obgects()


def snake_can_move(new_head: tuple[int, int], snake: Snake,
                   obstacles) -> bool:
    """Проверяет есть ли на пути препятствия. Если нет то возвращает {True}
    и змейка двигается дальше. Если есть препятствие, возвращется {False}.
    В зависимости от препятсвия змейка вырастет, уменьшится или сбросится
    в начальное состояние.
    """
    if snake.can_bite_itself(new_head):
        game.reset = True
        return False

    for obstacle in obstacles:

        if snake.try_bite(new_head, obstacle) and type(obstacle) is Apple:
            if obstacle.name == 'apple':
                snake.grow_up(obstacle.position)

            game.update_eaten_apples()

            if snake.length + len(obstacles) <= FIELD_SIZE:
                all_positons = get_all_position(snake, obstacles)
                obstacle.randomize_position(all_positons)
            else:
                game.reset = True

            return False

        elif snake.try_bite(new_head, obstacle) and type(obstacle) is Stone:
            if snake.length <= obstacle.weight:
                game.reset = True
            else:
                for _ in range(obstacle.weight):
                    snake.cut_tail()
                all_positons = get_all_position(snake, obstacles)
                obstacle.randomize_position(all_positons)

            return False

    return True


def draw_menu():
    """Отрисовывает главное меню."""
    title_menu.fill('Black')
    text = title_font.render('Змейка', True, 'White')
    txt_x, txt_y = TITLE_MENU_WIDTH // 2, TITLE_MENU_HEIGHT // 2
    text_rect = text.get_rect(center=(txt_x, txt_y))
    title_menu.blit(text, text_rect)

    main_menu.fill(MAIN_MENU_COLOR)
    rect = (0, 0, MENU_WIDTH, MENU_HEIGHT)
    step = game.get_menu_step()

    pg.draw.rect(main_menu, MENU_BORDER_COLOR, rect, 4)
    y_tmp = step

    for item in game.get_menu_list():
        if item == 'Продолжить' and game.new_game:
            text = menu_font.render(item, True, 'DarkGray')
        else:
            text = menu_font.render(item, True, 'Black')

        text_rect = text.get_rect(center=(MENU_WIDTH // 2, y_tmp))
        main_menu.blit(text, text_rect)

        if game.menu_title() == item:
            text_rect.inflate_ip(MENU_FONT_SIZE // 2, MENU_FONT_SIZE // 2)
            pg.draw.rect(main_menu, SNAKE_COLOR, text_rect, 5)

        y_tmp += step

    screen.blit(main_menu, main_menu_rect)
    screen.blit(title_menu, title_menu_rect)


def main():
    """Реализует базовую логику игры и инициализацию всех объектов."""
    snake, obstacles = init_game_obgects()
    game.switch_on()

    while game.is_run():
        screen.blit(background_surface, (0, 0))

        if game.menu_is_open():
            game_caption('Змейка || Основное меню')
            if quit_pressed():
                game.close_menu()

            draw_menu()
            handle_keys_menu()
            if game.reset:
                snake, obstacles = reset_game(True)
                game.reset = False
        else:
            if quit_pressed():
                game.open_menu()

            snake.draw()
            for obstacle in obstacles:
                obstacle.draw()

            handle_keys(snake)

            if game.slow_mode():
                new_head = snake.new_head()

                if snake_can_move(new_head, snake, obstacles):
                    snake.move(new_head)
                elif game.reset:
                    snake, obstacles = reset_game()
                    game.reset = False

            game_caption(game.info())

        clock.tick(GAME_SPEED)
        pg.display.update()

    quit_game()


if __name__ == '__main__':
    main()

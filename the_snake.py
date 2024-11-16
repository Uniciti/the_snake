
from random import choice, randint
from typing import Optional
from time import time

import pygame as pg

pg.init()

"""Размеры игрового окна и элементов интерфейса""" 
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MENU_WIDTH, MENU_HEIGHT = 200, 200
TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT = MENU_WIDTH, 50
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
MENU_FONT_SIZE = 35
TITLE_FONT_SIZE = 60
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
TOTAL_CELLS = GRID_WIDTH * GRID_HEIGHT
AVAILABLE_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

"""Векторы перемещения"""
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

"""Цветовая схема игры"""
BOARD_BACKGROUND_COLOR = (47, 71, 22)
BORDER_COLOR = (93, 216, 228)
MAIN_MENU_COLOR = (200, 200, 200)
MENU_BORDER_COLOR = (25, 25, 25)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (107, 99, 92)
DEFAULT_COLOR = (0, 0, 0)

"""Параметры игровой механики"""
FPS = 60
SLOW_MODE_FPS = 10

"""Настройки игровых объектов"""
INITIAL_APPLES = 20
INITIAL_STONES = 10
STONE_DAMAGE = 5

"""Управление"""
KEY_ENTER = 13

"""Инициализация игрового окна"""
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

"""Инициализация меню"""
main_menu = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
main_menu_rect = main_menu.get_rect(center=SCREEN_CENTER)
title_menu = pg.Surface((TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT))
title_menu_rect = main_menu.get_rect(
    center=(SCREEN_WIDTH // 2, main_menu_rect.y + TITLE_MENU_HEIGHT)
)

"""Создание фонового слоя"""
background_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background_surface.fill(BOARD_BACKGROUND_COLOR)
screen.blit(background_surface, (0, 0))

"""Настройка заголовка окна"""
set_window_title = pg.display.set_caption
set_window_title('Змейка')

"""Инициализация шрифтов"""
menu_font = pg.font.Font(None, MENU_FONT_SIZE)
title_font = pg.font.Font(None, TITLE_FONT_SIZE)

"""Инициализация таймера"""
clock = pg.time.Clock()


class GameObject():
    """Базовый класс для всех игровых объектов"""

    def __init__(self,
                 body_color: tuple[int, int, int] = DEFAULT_COLOR,
                 name: Optional[str] = None) -> None:
        """Создает новый игровой объект с заданным цветом и именем"""
        self.position: tuple[int, int] = SCREEN_CENTER
        self.body_color = body_color
        self.name = name or str(type(self).__name__).lower()

    def draw(self) -> None:
        """Отрисовывает объект на экране"""

    def render_cell(self, position: tuple[int, int],
                  color: Optional[tuple[int, int, int]] = None,
                  is_tail: bool = False) -> None:
        """Отрисовывает клетку объекта с заданным цветом и границей"""
        color = color or self.body_color

        rect = pg.Rect(
            position,
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, color, rect)
        if not is_tail:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def place_randomly(self,
                      occupied_cells: list[tuple[int, int]] = []) -> None:
        """Размещает объект в случайной свободной клетке поля"""
        self.position = choice(tuple(AVAILABLE_CELLS - set(occupied_cells)))


class Apple(GameObject):
    """Игровой объект, который змейка может съесть для роста"""

    def __init__(self,
                 body_color: tuple[int, int, int] = APPLE_COLOR,
                 occupied_cells: list = [],
                 name: Optional[str] = None) -> None:
        """Создает яблоко в случайной позиции"""
        super().__init__(body_color, name)
        self.place_randomly(occupied_cells)

    def draw(self) -> None:
        """Отрисовывает яблоко на экране"""
        self.render_cell(self.position)


class Stone(GameObject):
    """Препятствие, которое уменьшает длину змейки при столкновении"""

    def __init__(self,
                 body_color: tuple[int, int, int] = STONE_COLOR,
                 occupied_cells: list = [],
                 damage: int = STONE_DAMAGE) -> None:
        """Создает камень с заданным уроном"""
        super().__init__(body_color)
        self.place_randomly(occupied_cells)
        self.damage = damage

    def draw(self) -> None:
        """Отрисовывает камень на экране"""
        self.render_cell(self.position)

class Snake(GameObject):
    """Основной игровой персонаж, управляемый игроком"""

    def __init__(self,
                 body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        """Создает змейку в начальном состоянии"""
        super().__init__(body_color)
        self.reset()
        self.direction: tuple[int, int] = RIGHT

    def reset(self) -> None:
        """Возвращает змейку в начальное состояние"""
        self.segments = [self.position]
        self.length = 1
        self.last_segment: Optional[tuple[int, int]] = None
        self.direction = choice([RIGHT, LEFT, UP, DOWN])

    def set_direction(self, direction: tuple[int, int]) -> None:
        """Изменяет направление движения змейки"""
        self.direction = direction

    def calculate_next_head(self) -> tuple[int, int]:
        """Вычисляет позицию следующего сегмента головы"""
        head_x, head_y = self.get_head_position()
        return (
            (head_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

    def add_segment(self, position: tuple[int, int]) -> None:
        """Добавляет новый сегмент в начало змейки"""
        self.segments.insert(0, position)
        self.update_length()

    def remove_tail(self) -> None:
        """Удаляет последний сегмент змейки"""
        self.segments.pop()
        self.update_length()

    def update_length(self) -> None:
        """Обновляет информацию о текущей длине змейки"""
        self.length = len(self.segments)
        game.update_snake_stats(self.length)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает текущую позицию головы змейки"""
        return self.segments[0]

    def draw(self) -> None:
        """Отрисовывает все сегменты змейки"""
        for position in self.segments:
            self.render_cell(position, SNAKE_COLOR)

        if self.last_segment:
            self.render_cell(self.last_segment, BOARD_BACKGROUND_COLOR, True)

    def move_forward(self, new_head: tuple[int, int]) -> None:
        """Перемещает змейку на одну клетку вперед"""
        self.segments.insert(0, new_head)
        self.last_segment = self.segments.pop()

    def will_collide_with_self(self, new_head: tuple[int, int]) -> bool:
        """Проверяет столкновение с собственным телом"""
        return new_head in self.segments

    def will_collide_with(self, new_head: tuple[int, int], object: GameObject) -> bool:
        """Проверяет столкновение с другим объектом"""
        return object.position == new_head


class GameManager():
    """Управляет общим состоянием и логикой игры"""

    def __init__(self) -> None:
        """Инициализирует менеджер игры с базовыми настройками"""
        self.needs_reset: bool = False
        self.is_new_game: bool = True
        self.__game_active: bool = False
        self.__slow_mode_counter: int = 0
        self.__current_snake_length: int = 1
        self.__apples_eaten: int = 0
        self.__menu_active: bool = True
        self.__selected_menu_item: int = 0
        self.__menu_options: list = [
            'Новая игра',
            'Продолжить',
            'Выход'
        ]

    def is_running(self) -> bool:
        """Проверяет активна ли игра"""
        return self.__game_active

    def start_game(self) -> None:
        """Запускает игру"""
        self.__game_active = True

    def stop_game(self) -> None:
        """Останавливает игру"""
        self.__game_active = False

    def is_menu_open(self) -> bool:
        """Проверяет открыто ли меню"""
        return self.__menu_active

    def hide_menu(self) -> None:
        """Скрывает игровое меню"""
        self.__menu_active = False

    def show_menu(self) -> None:
        """Показывает игровое меню"""
        self.__menu_active = True

    def select_previous_item(self) -> None:
        """Перемещает выбор меню на предыдущий пункт"""
        self.__selected_menu_item -= 1 if self.__selected_menu_item > 0 else 0

    def select_next_item(self) -> None:
        """Перемещает выбор меню на следующий пункт"""
        max_index = len(self.__menu_options) - 1
        if self.__selected_menu_item < max_index:
            self.__selected_menu_item += 1
        else:
            self.__selected_menu_item = max_index

    def get_selected_option(self) -> str:
        """Возвращает текущий выбранный пункт меню"""
        return self.__menu_options[self.__selected_menu_item]

    def calculate_menu_spacing(self) -> int:
        """Вычисляет вертикальное расстояние между пунктами меню"""
        return (MENU_HEIGHT // (len(self.__menu_options) + 1))

    def get_menu_options(self) -> list:
        """Возвращает список доступных пунктов меню"""
        return self.__menu_options

    def should_update(self, delay: int = SLOW_MODE_FPS) -> bool:
        """Проверяет нужно ли обновлять состояние с учетом замедления"""
        self.__slow_mode_counter += 1
        if self.__slow_mode_counter > delay:
            self.__slow_mode_counter = 0

        return self.__slow_mode_counter == delay

    def increment_score(self) -> None:
        """Увеличивает счетчик съеденных яблок"""
        self.__apples_eaten += 1

    def update_snake_stats(self, length: int) -> None:
        """Обновляет статистику о длине змейки"""
        self.__current_snake_length = length

    def reset_stats(self) -> None:
        """Сбрасывает игровую статистику"""
        self.__current_snake_length = 1
        self.__apples_eaten = 0

    def get_game_stats(self) -> str:
        """Формирует строку с текущей игровой статистикой"""
        return (
            f'Длина змейки: {self.__current_snake_length} || '
            f'Яблок съедено: {self.__apples_eaten} || '
        )
    
"""Инициализируем основной класс игры"""
game = GameManager()

def handle_snake_input(snake: Snake) -> None:
    """Обрабатывает пользовательский ввод для управления змейкой"""
    keys = pg.key.get_pressed()
    new_direction: Optional[tuple[int, int]] = None

    if keys[pg.K_UP] and snake.direction != DOWN:
        new_direction = UP
    elif keys[pg.K_DOWN] and snake.direction != UP:
        new_direction = DOWN
    elif keys[pg.K_LEFT] and snake.direction != RIGHT:
        new_direction = LEFT
    elif keys[pg.K_RIGHT] and snake.direction != LEFT:
        new_direction = RIGHT

    if new_direction:
        snake.set_direction(new_direction)


def handle_menu_input() -> None:
    """Обрабатывает пользовательский ввод в меню"""
    keys = pg.key.get_pressed()

    if keys[KEY_ENTER]:
        selected_option = game.get_selected_option()
        if selected_option == 'Новая игра':
            if game.is_new_game:
                game.is_new_game = False
            else:
                game.needs_reset = True
            game.hide_menu()
        elif selected_option == 'Продолжить' and not game.is_new_game:
            game.hide_menu()
        elif selected_option == 'Выход':
            game.stop_game()
            game.hide_menu()

    if game.should_update(1):
        if keys[pg.K_UP]:
            game.select_previous_item()
        elif keys[pg.K_DOWN]:
            game.select_next_item()


def terminate_game() -> None:
    """Корректно завершает игру"""
    pg.quit()
    raise SystemExit


def check_exit_request() -> bool:
    """Проверяет запрос на выход из игры"""
    keys = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
            if game.is_new_game:
                game.stop_game()
            else:
                return True

    return False


def create_apples(count: int = INITIAL_APPLES,
                 occupied_cells: list = []) -> tuple[list, list]:
    """Создает заданное количество яблок на свободных клетках"""
    apples = []
    for _ in range(count):
        apple = Apple(occupied_cells=occupied_cells)
        apples.append(apple)
        occupied_cells.append(apple.position)

    return apples, occupied_cells


def create_stones(count: int = INITIAL_STONES,
                 occupied_cells: list = []) -> tuple[list, list]:
    """Создает заданное количество камней на свободных клетках"""
    stones = []
    for _ in range(count):
        stone = Stone(occupied_cells=occupied_cells)
        stones.append(stone)
        occupied_cells.append(stone.position)

    return stones, occupied_cells


def get_occupied_positions(snake: Snake, obstacles: list[GameObject]) -> list:
    """Собирает список всех занятых позиций на поле"""
    return [obstacle.position for obstacle in obstacles] + snake.segments


def initialize_game_objects() -> tuple[Snake, list[GameObject]]:
    """Создает начальное состояние игровых объектов"""
    snake = Snake()
    occupied_cells = list.copy(snake.segments)
    apples, occupied_cells = create_apples(occupied_cells=occupied_cells)
    stones, occupied_cells = create_stones(occupied_cells=occupied_cells)

    return snake, [*apples, *stones]


def restart_game(new_game: bool = False) -> tuple[Snake, list[GameObject]]:
    """Перезапускает игру, сбрасывая или сохраняя статистику"""
    if new_game:
        game.reset_stats()
    else:
        game.update_snake_stats(1)
        
    return initialize_game_objects()


def check_collision(new_head: tuple[int, int], snake: Snake,
                   obstacles) -> bool:
    """Проверяет столкновения и обрабатывает их последствия"""
    if snake.will_collide_with_self(new_head):
        game.needs_reset = True
        return False

    for obstacle in obstacles:
        if snake.will_collide_with(new_head, obstacle):
            if isinstance(obstacle, Apple):
                handle_apple_collision(snake, obstacle, obstacles)
                return False
            elif isinstance(obstacle, Stone):
                handle_stone_collision(snake, obstacle, obstacles)
                return False

    return True


def handle_apple_collision(snake: Snake, apple: Apple, obstacles: list) -> None:
    """Обрабатывает столкновение змейки с яблоком"""
    snake.add_segment(apple.position)
    game.increment_score()

    if snake.length + len(obstacles) <= TOTAL_CELLS:
        occupied_positions = get_occupied_positions(snake, obstacles)
        apple.place_randomly(occupied_positions)
    else:
        game.needs_reset = True


def handle_stone_collision(snake: Snake, stone: Stone, obstacles: list) -> None:
    """Обрабатывает столкновение змейки с камнем"""
    if snake.length <= stone.damage:
        game.needs_reset = True
    else:
        for _ in range(stone.damage):
            snake.remove_tail()
        occupied_positions = get_occupied_positions(snake, obstacles)
        stone.place_randomly(occupied_positions)


def render_menu():
    """Отрисовывает игровое меню"""

    title_menu.fill('Black')
    title_text = title_font.render('Змейка', True, 'White')
    title_x = TITLE_MENU_WIDTH // 2
    title_y = TITLE_MENU_HEIGHT // 2
    title_rect = title_text.get_rect(center=(title_x, title_y))
    title_menu.blit(title_text, title_rect)

    main_menu.fill(MAIN_MENU_COLOR)
    menu_border = (0, 0, MENU_WIDTH, MENU_HEIGHT)
    spacing = game.calculate_menu_spacing()

    pg.draw.rect(main_menu, MENU_BORDER_COLOR, menu_border, 4)
    current_y = spacing

    for option in game.get_menu_options():
        if option == 'Продолжить' and game.is_new_game:
            text = menu_font.render(option, True, 'DarkGray')
        else:
            text = menu_font.render(option, True, 'Black')
        text_rect = text.get_rect(center=(MENU_WIDTH // 2, current_y))
        main_menu.blit(text, text_rect)

        if game.get_selected_option() == option:
            highlighted_rect = text_rect.inflate(MENU_FONT_SIZE // 2, MENU_FONT_SIZE // 2)
            pg.draw.rect(main_menu, SNAKE_COLOR, highlighted_rect, 5)

        current_y += spacing

    screen.blit(main_menu, main_menu_rect)
    screen.blit(title_menu, title_menu_rect)


def main():
    """Основной игровой цикл"""
    snake, obstacles = initialize_game_objects()
    game.start_game()

    while game.is_running():
        screen.blit(background_surface, (0, 0))

        if game.is_menu_open():
            set_window_title('Змейка || Основное меню')
            if check_exit_request():
                game.hide_menu()

            render_menu()
            handle_menu_input()
            
            if game.needs_reset:
                snake, obstacles = restart_game(True)
                game.needs_reset = False
        else:
            if check_exit_request():
                game.show_menu()

            snake.draw()
            for obstacle in obstacles:
                obstacle.draw()

            handle_snake_input(snake)

            if game.should_update():
                new_head = snake.calculate_next_head()

                if check_collision(new_head, snake, obstacles):
                    snake.move_forward(new_head)
                elif game.needs_reset:
                    snake, obstacles = restart_game()
                    game.needs_reset = False

            set_window_title(game.get_game_stats())

        clock.tick(FPS)
        pg.display.update()

    terminate_game()

if __name__ == '__main__':
    main()
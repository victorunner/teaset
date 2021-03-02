from enum import Enum
from operator import itemgetter
from typing import Dict, Optional

import attr
from anytree import NodeMixin, RenderTree

# Размеры стола
TABLE_WIDTH = 3
TABLE_HEIGHT = 2

# Максимально число шагов для решения задачи
MAX_STEPS = 18


class Item(Enum):
    CUP_1 = '①'  # чашка № 1
    CUP_2 = '②'  # чашка № 2
    CUP_3 = '③'  # чашка № 3
    POT = '◆'  # чайник
    MILK_JUG = '◇'  # молочник

    def __str__(self):
        return self.value


class Direction(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    DOWN = (0, -1)
    UP = (0, 1)

    def __str__(self):
        return {
            Direction.LEFT: '⬅',
            Direction.RIGHT: '➡',
            Direction.DOWN: '⬇',
            Direction.UP: '⬆'
        }[self]

    def reverse(self):
        return Direction(tuple(-coor for coor in self.value))


@attr.s(auto_attribs=True)
class Step(NodeMixin):
    item: Optional[Item]
    direction: Direction

    def is_reversed_for(self, other: 'Step'):
        return (
            other.item == self.item
            and
            self.direction == other.direction.reverse()
        )

    def __str__(self):
        return f'{self.item} {self.direction}'

    @classmethod
    def nonestep(cls):
        return cls(None, None)

    def __bool__(self):
        return self != type(self).nonestep()


@attr.s(auto_attribs=True, frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(*(sum(c) for c in zip(self, other)))

    def __iter__(self):
        yield self.x
        yield self.y

    def is_within_rect(self, xmax, ymax, xmin=0, ymin=0):
        return (
            xmin <= self.x < xmax
            and
            ymin <= self.y < ymax
        )


@attr.s(auto_attribs=True)
class Table:
    configuration: Dict

    def is_position_vacant(self, position: Position):
        return all(p != position for p in self.configuration.values())

    def is_step_possible(self, step: Step):
        new_position = self.configuration[step.item] + step.direction.value
        return (
            new_position.is_within_rect(TABLE_WIDTH, TABLE_HEIGHT)
            and
            self.is_position_vacant(new_position)
        )

    @classmethod
    def fromstep(cls, table: 'Table', step: Step):
        configuration = table.configuration.copy()
        configuration[step.item] += step.direction.value
        return cls(configuration)


INITIAL_TABLE = Table(
    {
        Item.CUP_1: Position(0, 1),
        Item.CUP_2: Position(0, 0),
        Item.CUP_3: Position(1, 0),
        Item.POT: Position(2, 1),
        Item.MILK_JUG: Position(2, 0)
    }
)


def is_result_table(table: Table) -> bool:
    config = table.configuration
    return (
        config[Item.POT] == Position(2, 0)
        and
        config[Item.MILK_JUG] == Position(2, 1)
    )


def do_next_step(prev_table: Table, prev_step: Step,
                 prev_steps_count=0) -> bool:
    if prev_steps_count == MAX_STEPS:
        return False

    steps = [
        step
        for item in Item
        for direction in Direction
        if (
            prev_table.is_step_possible(step := Step(item, direction))
            and (
                not prev_step or
                not step.is_reversed_for(prev_step)
            )
        )
    ]

    success = False
    for step in steps:
        table = Table.fromstep(prev_table, step)
        if is_result_table(table):
            step.parent = prev_step
            success = True
            break
        if do_next_step(table, step, prev_steps_count + 1):
            step.parent = prev_step
            success = True

    return success


if __name__ == '__main__':
    root_step = Step.nonestep()
    do_next_step(INITIAL_TABLE, root_step)

    for pre, _, node in RenderTree(root_step):
        print(f'{pre}{node}')

    result = [(leaf.depth - 1, leaf) for leaf in root_step.leaves]
    result.sort(key=itemgetter(0))

    for n, r in enumerate(result, start=1):
        print(f'--- Вариант {n} с числом ходов {r[0]} ---')
        print(', '.join(str(s) for s in r[1].path if s), end='\n\n')

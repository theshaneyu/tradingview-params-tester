from typing import Literal, TypedDict, List


CurrentParams = TypedDict(
    'CurrentParams',
    {
        'period': str,
        'amplification': str,
        'long_take_profit': str,
        'short_take_profit': str,
    },
)

Params = List[
    Literal['period', 'amplification', 'long_take_profit', 'short_take_profit']
]

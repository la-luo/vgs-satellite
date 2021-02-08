import random
import re
import uuid
from abc import ABC, abstractmethod
from typing import Iterable, List, Set, Type

from base58 import b58encode

from . import AliasGeneratorType


class AliasGenerator(ABC):
    @abstractmethod
    def generate(self, value: str) -> str:
        pass


class UUID(AliasGenerator):
    def generate(self, value: str) -> str:
        value = str(uuid.uuid4())
        return f'tok_sat_{b58encode(value).decode("UTF-8")}'[:30]


class RawUUID(AliasGenerator):
    def generate(self, value: str) -> str:
        return str(uuid.uuid4())


class ValidatingAliasGenerator(AliasGenerator):
    accepted_format: re.Pattern = None
    fallback_generator_cls: Type[AliasGenerator] = None

    def is_valid(self, value: str) -> bool:
        return self.accepted_format.fullmatch(value) is not None

    def generate(self, value: str) -> str:
        if not self.is_valid(value):
            return self.fallback_generator_cls().generate(value)
        return self._generate(value)

    @abstractmethod
    def _generate(self, value: str) -> str:
        pass


class LuhnValidCardNumber(ValidatingAliasGenerator):
    accepted_format: re.Pattern = re.compile(r'\d+')
    fallback_generator_cls: Type[AliasGenerator] = RawUUID
    fixed_digits: List[slice] = []

    def is_valid(self, value: str) -> bool:
        return super().is_valid(value) and check_luhn(value)

    def _generate(self, value: str) -> str:
        card_len = len(value)
        fixed_indexes = set()
        for s in self.fixed_digits:
            start, stop, _ = s.indices(card_len)
            fixed_indexes.update(range(start, stop))
        loose_indexes = set(range(card_len)) - fixed_indexes

        digits = _random_digits(map(int, value), loose_indexes)

        m = _mod10(digits)
        if m != 0:
            idx = next(iter(loose_indexes))
            r_idx = len(digits) - idx - 1
            if r_idx % 2:
                d = LUHN_DIGITS[digits[idx]]
                if d < m:
                    d += 10 - m
                else:
                    d -= m
                d = LUHN_DIGITS.index(d)
            else:
                d = digits[idx]
                if d < m:
                    d += 10 - m
                else:
                    d -= m
            digits[idx] = d

        return ''.join(map(str, digits))


class LuhnValidCardNumber6T4(LuhnValidCardNumber):
    accepted_format: re.Pattern = re.compile(r'\d{14}\d*')
    fallback_generator_cls: Type[AliasGenerator] = UUID
    fixed_digits = [slice(None, 6), slice(-4, None)]


class LuhnValidCardNumberT4(LuhnValidCardNumber):
    accepted_format: re.Pattern = re.compile(r'\d{14}\d*')
    fixed_digits = [slice(-4, None)]


class LuhnValidCardNumberPFPT(LuhnValidCardNumber):
    accepted_format: re.Pattern = re.compile(r'\d{13,19}')
    fixed_digits = [slice(None, 5), slice(-4, None)]

    def _generate(self, value: str) -> str:
        pad = '0' * (16 - len(value))
        return super()._generate(f'991{value[0:2]}{pad}{value[2:]}')


class LuhnInvalidCardNumber(ValidatingAliasGenerator):
    accepted_format: re.Pattern = re.compile(r'\d{13,16}')
    fallback_generator_cls: Type[AliasGenerator] = RawUUID

    def _generate(self, value: str) -> str:
        digits = [random.randint(0, 9) for _ in range(len(value))]
        if _mod10(digits) == 0:
            digits[-1] = (digits[-1] + 1) % 10
        return ''.join(map(str, digits))


class NumLenPreserving(ValidatingAliasGenerator):
    accepted_format: re.Pattern = re.compile(r'\d{3,}')
    fallback_generator_cls: Type[AliasGenerator] = RawUUID

    def _generate(self, value: str) -> str:
        return ''.join(map(str, _random_digits(map(int, value))))


def get_alias_generator(generator_type: AliasGeneratorType) -> AliasGenerator:
    return _supported_generators[generator_type]


_supported_generators = {
    AliasGeneratorType.FPE_SIX_T_FOUR: LuhnValidCardNumber6T4(),
    AliasGeneratorType.FPE_T_FOUR: LuhnValidCardNumberT4(),
    AliasGeneratorType.NON_LUHN_FPE_ALPHANUMERIC: LuhnInvalidCardNumber(),
    AliasGeneratorType.NUM_LENGTH_PRESERVING: NumLenPreserving(),
    AliasGeneratorType.PFPT: LuhnValidCardNumberPFPT(),
    AliasGeneratorType.RAW_UUID: RawUUID(),
    AliasGeneratorType.UUID: UUID(),
}


LUHN_DIGITS = [0, 2, 4, 6, 8, 1, 3, 5, 7, 9]


def _mod10(digits: List[int]) -> int:
    return sum(
        LUHN_DIGITS[d] if i % 2 else d
        for i, d in enumerate(digits[::-1])
    ) % 10


def _random_digits(
    digits: Iterable[int],
    loose_indexes: Set[int] = None,
) -> List[int]:
    result = []
    for i, d in enumerate(digits):
        if not loose_indexes or i in loose_indexes:
            v = random.randint(0, 9)
            if v == d:
                v = (d + 1) % 10
        else:
            v = d

        result.append(v)

    return result


def check_luhn(card_number: str) -> bool:
    return _mod10(list(map(int, card_number))) == 0

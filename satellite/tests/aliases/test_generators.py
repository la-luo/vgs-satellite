from unittest.mock import Mock

import pytest

from satellite.aliases import AliasGeneratorType
from satellite.aliases.generators import check_luhn, get_alias_generator


def test_uuid(monkeypatch):
    monkeypatch.setattr(
        'satellite.aliases.generators.uuid.uuid4',
        Mock(return_value='b5e183e7-b879-4613-bf04-6edfb427a020')
    )
    generator = get_alias_generator(AliasGeneratorType.UUID)
    assert generator.generate('4444333322221111') == 'tok_sat_kFcAR1mbg67HwR8PSRytM4'


def test_raw_uuid(monkeypatch):
    monkeypatch.setattr(
        'satellite.aliases.generators.uuid.uuid4',
        Mock(return_value='b5e183e7-b879-4613-bf04-6edfb427a020')
    )
    generator = get_alias_generator(AliasGeneratorType.RAW_UUID)
    result = generator.generate('4444333322221111')
    assert result == 'b5e183e7-b879-4613-bf04-6edfb427a020'


def test_fpe_six_t_four_ok():
    generator = get_alias_generator(AliasGeneratorType.FPE_SIX_T_FOUR)
    value = '4444333322221111'
    result = generator.generate(value)
    assert result != value
    assert result[:6] == '444433'
    assert result[-4:] == '1111'
    assert check_luhn(result)


@pytest.mark.parametrize('value', ['abc', '4111', '4111111111111112'])
def test_fpe_six_t_four_invalid(monkeypatch, value: str):
    monkeypatch.setattr(
        'satellite.aliases.generators.UUID.generate',
        Mock(return_value='default-alias')
    )
    generator = get_alias_generator(AliasGeneratorType.FPE_SIX_T_FOUR)
    result = generator.generate(value)
    assert result == 'default-alias'


def test_fpe_t_four():
    generator = get_alias_generator(AliasGeneratorType.FPE_T_FOUR)
    value = '4444333322221111'
    result = generator.generate(value)
    assert result != value
    assert result[-4:] == '1111'
    assert check_luhn(result)


@pytest.mark.parametrize('value', ['abc', '4111', '4111111111111112'])
def test_fpe_t_four_invalid(monkeypatch, value: str):
    monkeypatch.setattr(
        'satellite.aliases.generators.RawUUID.generate',
        Mock(return_value='default-alias')
    )
    generator = get_alias_generator(AliasGeneratorType.FPE_T_FOUR)
    result = generator.generate(value)
    assert result == 'default-alias'


def test_pfpt():
    generator = get_alias_generator(AliasGeneratorType.PFPT)
    value = '4444333322221111'
    result = generator.generate(value)
    assert result != value
    assert len(result) == 19
    assert result[0:5] == '99144'
    assert result[-4:] == '1111'
    assert check_luhn(result)


@pytest.mark.parametrize('value', ['abc', '4111', '4111111111111112'])
def test_pfpt_invalid(monkeypatch, value: str):
    monkeypatch.setattr(
        'satellite.aliases.generators.RawUUID.generate',
        Mock(return_value='default-alias')
    )
    generator = get_alias_generator(AliasGeneratorType.PFPT)
    result = generator.generate(value)
    assert result == 'default-alias'


def test_non_luhn_fpe_alphanumeric():
    generator = get_alias_generator(AliasGeneratorType.NON_LUHN_FPE_ALPHANUMERIC)
    value = '4444333322221111'
    result = generator.generate(value)
    assert result != value
    assert result.isdigit()
    assert len(result) == len(value)
    assert not check_luhn(result)


@pytest.mark.parametrize('value', ['abc', '4111'])
def test_non_luhn_fpe_alphanumeric_invalid(monkeypatch, value: str):
    monkeypatch.setattr(
        'satellite.aliases.generators.RawUUID.generate',
        Mock(return_value='default-alias')
    )
    generator = get_alias_generator(AliasGeneratorType.NON_LUHN_FPE_ALPHANUMERIC)
    result = generator.generate(value)
    assert result == 'default-alias'


def test_num_length_preserving_ok():
    generator = get_alias_generator(AliasGeneratorType.NUM_LENGTH_PRESERVING)
    value = '123'
    result = generator.generate(value)
    assert result != value
    assert result.isdigit()
    assert len(value) == len(result)


@pytest.mark.parametrize('value', ['1x2', 'abc', '12'])
def test_num_length_preserving_invalid(monkeypatch, value: str):
    monkeypatch.setattr(
        'satellite.aliases.generators.RawUUID.generate',
        Mock(return_value='default-alias')
    )
    generator = get_alias_generator(AliasGeneratorType.NUM_LENGTH_PRESERVING)
    result = generator.generate(value)
    assert result == 'default-alias'

import pytest


@pytest.mark.asyncio
async def test_sample_data(sample_data):
    assert sample_data == "hello pytest"

# this file has name conftest because we use global fixture in some files
# https://docs.pytest.org/en/6.2.x/fixture.html?highlight=conftest
import pytest
import tests.find.gen as generator

@pytest.fixture(name='generator_photo', scope="function")
def gen_photo():
    return generator.gen("blue", 350, 350, 'Arial_Bold', 150, "File")

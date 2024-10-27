import pytest
import tests.find.gen as generator

@pytest.fixture(name='generator_photo', scope="function")
def gen_photo():
    return generator.gen("blue", 350, 350, 'Arial_Bold', 150, "File")
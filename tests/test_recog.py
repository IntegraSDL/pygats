"""Module with library tests"""
from pathlib import Path
import numpy as np
import pytest
import math
import pygats.recog as rec
import pygats.pygats as pyg
from pygats.formatters import MarkdownFormatter as MD
from PIL import Image, ImageDraw, ImageFont
from tests.find import gen
import cv2 as cv

@pytest.fixture(name='formatter', scope="session", autouse=True)
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


@pytest.fixture(scope="session", autouse=True)
def fixture_create_ctx(formatter: MD):
    """ctx fixture for check for ctx creation"""
    global ctx
    ctx = pyg.Context(formatter)
    return ctx


@pytest.fixture(scope="function")
def gen_photo():
    img = Image.open(f'tests/find/background/blue.jpg')
    font = ImageFont.truetype(f'tests/find/fonts/Arial.ttf', size=70)
    draw_text = ImageDraw.Draw(img)
    draw_text.text((350, 350), "TEST", font=font, fill=('#FFFFFF'))
    img.save('tests/find/1.png')
    return img


@pytest.fixture(scope="function")
def words_for_bg():
    gen.color_shade_gen((85, 85, 85), (350, 350))
    file = open("tests/find/words.en.txt")
    lines = file.readlines()
    font = ImageFont.truetype(f'tests/find/fonts/Arial_Bold.ttf', size=27)
    texts = []
    colors = Path('tests/find/color_shades')
    colors_and_texts = Path(f'tests/find/fill_colors')
    colors_and_texts.mkdir(parents=True, exist_ok=True)
    for photo in colors.glob('*'):
        img = Image.open(photo)
        for line in lines:
            if not line.strip():
                continue
            new_img = img.copy()
            draw_text = ImageDraw.Draw(new_img)
            draw_text.text((100, 100),line.strip(), font=font, fill="#000000")
            text = rec.SearchedText(line.strip(), "eng", None)
            texts.append(text)
            subfolder_name = photo.stem
            folder_path = Path(f'{colors_and_texts}/{subfolder_name}')
            folder_path.mkdir(parents=True, exist_ok=True)
            new_img.save(f'{colors_and_texts}/{subfolder_name}/{line.strip()}.png', quality=100)
    return texts
  

def test_check_text_1(words_for_bg, capsys):
    successful_count = 0
    failed_count = 0
    fill_color = Path(f'tests/find/fill_colors')
    folder_result = Path(f'tests/find/result.txt')
    for folders in fill_color.glob('*'):
        image_count = 0
        assert folders.is_dir()
        for expected_text in words_for_bg:
            image_path = folders / f"{expected_text.content}.png"
            image_count += 1 
            try:
                if image_path.exists():
                    img = Image.open(image_path)
                    width, height = img.size
                    assert width > 0
                    assert height > 0
                    result = rec.check_text(ctx, img, expected_text)
                    cptrd = capsys.readouterr()
                    if '![Успешно]' in cptrd.out:
                        successful_count += 1
                    else:
                        failed_count += 1
                        assert cptrd == f"{expected_text} не найден на изображении"
            except pyg.TestException:
                    failed_count += 1
            if image_count >= 100:
                with open(folder_result, 'a') as file:
                    file.write(f"Папка: {folders}\n")
                    file.write(f"Успешно распознанных слов: {successful_count}\n")
                    file.write(f"Не распознанных слов: {failed_count}\n")
                    file.write(f"---------------------------------\n")
                successful_count = 0
                failed_count = 0
                assert successful_count == 0
                assert failed_count == 0
                break


@pytest.mark.parametrize(
    "img_path, expected_value",
    [
        ("tests/find/background/blue.jpg", 3.767),
        ("tests/find/background/gray.jpg", 3.568),
        ("tests/find/background/white.jpg", 1.0),
        ("tests/find/background/yellow-grad.jpg", 5.297)
    ]
)
def test_contrast(img_path, expected_value):
    img = Image.open(img_path)
    contrast = rec.contrast(img)
    assert math.isclose(contrast, expected_value, rel_tol=1e-09, abs_tol=0.0)


@pytest.mark.parametrize(
    "img_path",
    [
        ("tests/find/background/yellow-grad.jpg"),
        ("tests/find/background/white.jpg"),
    ]
)
def test_find_keypoints_failed(img_path):
    img = Image.open(img_path)
    img.transpose(Image.ROTATE_90)
    keypoints, _, _ = rec.find_keypoints(img)
    assert keypoints == ()


def test_find_keypoints_success(gen_photo):
    gen_photo
    img = Image.open("tests/find/1.png")
    img.transpose(Image.ROTATE_90)
    keypoints, _, coord_list = rec.find_keypoints(img)
    for kp in keypoints:
        x, y = kp.pt
        assert [x, y] in coord_list
    assert len(keypoints) > 0


def test_hdbscan_cluster(gen_photo):
    gen_photo
    img_with_keypoints = Path('tests/find/img_with_keypoints')
    img_with_keypoints.mkdir(parents=True, exist_ok=True)
    img_path = "./tests/find/1.png"
    img = Image.open(img_path)
    keypoints, _, coord_list = rec.find_keypoints(img)
    img_cv = cv.imread(img_path)
    for cluster_selection_epsilon in range(2, 30, 1):
        clusters = rec.hdbscan_cluster(keypoints, coord_list,
            min_cluster_size=2,
            min_samples=1,
            cluster_selection_epsilon=cluster_selection_epsilon
        )
        img_with_clusters = img_cv.copy()
        assert len(clusters) > 0
        for cluster in clusters:
            keypoints_cluster = cluster.keypoints
            coord_rect = cluster.coord_rect
            if keypoints_cluster:
                img_with_clusters = cv.drawKeypoints(
                    img_with_clusters, keypoints_cluster, img_with_clusters,
                    flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                x_min, y_min, x_max, y_max = coord_rect
                cv.rectangle(img_with_clusters, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        output_path = img_with_keypoints / f'min_samples-{cluster_selection_epsilon}.png'
        cv.imwrite(str(output_path), img_with_clusters)

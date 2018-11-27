import numpy as np
import scipy.ndimage as ndi
from skimage.measure import regionprops
import matplotlib.pyplot as plt
import pytest
from numpy.testing import assert_array_equal

from butterfly import tracing


@pytest.fixture()
def fake_butterfly():
    butterfly = np.zeros((1000, 2000))
    butterfly[250:500, 250:500] = 1  # left wing
    butterfly[250:500, 1500:1750] = 1  # right wing
    butterfly[500:900, 400:1600] = 1  # body
    butterfly[250:500, 800:1200] = 1  # head

    return butterfly


def test_split(fake_butterfly):
    middle = tracing.split_picture(fake_butterfly)
    assert middle == 999


def test_remove_antenna(fake_butterfly):
    middle = tracing.split_picture(fake_butterfly)

    binary_left = fake_butterfly[:, :middle]
    binary_right = fake_butterfly[:, middle:]

    # Adding antennae
    binary_left[260, 500:800] = 1
    binary_right[260, 201:501] = 1

    without_antenna_l = tracing.remove_antenna(binary_left)
    without_antenna_r = tracing.remove_antenna(binary_right)

    assert np.sum(without_antenna_l[260, 500:800]) == 0
    assert np.sum(without_antenna_r[260, 201:501]) == 0


def test_outer_pix(fake_butterfly):
    middle = tracing.split_picture(fake_butterfly)

    binary_left = fake_butterfly[:, :middle]
    binary_right = fake_butterfly[:, middle:]

    outer_pix_l = tracing.detect_outer_pix(binary_left, 'l')
    outer_pix_r = tracing.detect_outer_pix(binary_right, 'r')
    outer_pix_r = outer_pix_r + np.array([0, middle])

    assert_array_equal(outer_pix_l, np.array([250, 250]))
    assert_array_equal(outer_pix_r, np.array([250, 1749]))


def test_inner_pix(fake_butterfly):

    middle = tracing.split_picture(fake_butterfly)

    binary_left = fake_butterfly[:, :middle]
    binary_right = fake_butterfly[:, middle:]

    # Relative outer pixels
    outer_pix_l = np.array([250, 250])
    outer_pix_r = np.array([250, 750])

    inner_pix_l = tracing.detect_inner_pix(binary_left, outer_pix_l, 'l')
    inner_pix_l = inner_pix_l + np.array([0, outer_pix_l[1]])

    inner_pix_r = tracing.detect_inner_pix(binary_right, outer_pix_r, 'r')
    inner_pix_r = inner_pix_r + np.array([0, middle])

    assert_array_equal(inner_pix_l, np.array([499, 799]))
    assert_array_equal(inner_pix_r, np.array([499, 1200]))
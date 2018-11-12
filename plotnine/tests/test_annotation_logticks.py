from plotnine import (
    ggplot,
    aes,
    geom_point,
    scale_x_continuous,
    scale_y_continuous,
    annotation_logticks,
    coord_flip,
)
from plotnine.exceptions import PlotnineWarning
from plotnine.data import mtcars
from plotnine.geoms.annotation_logticks import _geom_logticks
import pytest
import numpy as np
import types


def test_annotation_logticks():
    p = (
        ggplot(mtcars)
        + geom_point(aes("wt", "mpg"))
        + scale_x_continuous(
            trans="log10", minor_breaks=8, limits=(1, 10), breaks=[1, 10]
        )
        + scale_y_continuous(
            trans="log10", limits=(10, 100), minor_breaks=8, breaks=[10, 100]
        )
        + annotation_logticks(sides="bl")
    )
    assert p == "annotation_logticks"


def test_annotation_logticks_coord_flip():
    p = (
        ggplot(mtcars)
        + geom_point(aes("wt", "mpg"))
        + scale_x_continuous(
            trans="log10", minor_breaks=8, limits=(1, 10), breaks=[1, 10]
        )
        + scale_y_continuous(
            trans="log10", limits=(10, 100), minor_breaks=8, breaks=[10, 100]
        )
        + annotation_logticks(sides="b")  # which ends up on the left
        + coord_flip()
    )
    assert p == "annotation_logticks_coord_flip"


def test_annotation_logticks_warnings():
    # high level test
    anno = annotation_logticks(sides="bl")
    p = ggplot(mtcars) + geom_point(aes("wt", "mpg")) + anno
    with pytest.warns(PlotnineWarning):
        assert p == "annotation_logticks_non_log_x_axis"

    # checking all paths...
    scale_x_10 = scale_x_continuous(
        trans="log10", minor_breaks=8, limits=(1, 10), breaks=[1, 10]
    )
    scale_y_10 = scale_x_continuous(
        trans="log10", minor_breaks=8, limits=(1, 10), breaks=[1, 10]
    )
    scale_x = scale_x_continuous()
    scale_y = scale_x_continuous()

    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "lb", types.SimpleNamespace(x=scale_x, y=scale_y), False
        )
        assert len(warnings) == 2

    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "lb", types.SimpleNamespace(x=scale_x_10, y=scale_y), False
        )
        assert len(warnings) == 1
    with pytest.warns(None) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "b", types.SimpleNamespace(x=scale_x_10, y=scale_y), False
        )
        assert len(warnings) == 0
    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "l", types.SimpleNamespace(x=scale_x_10, y=scale_y), False
        )
        assert len(warnings) == 1

    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "lb", types.SimpleNamespace(x=scale_x, y=scale_y_10), False
        )
        assert len(warnings) == 1
    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "b", types.SimpleNamespace(x=scale_x, y=scale_y_10), False
        )
        assert len(warnings) == 1
    with pytest.warns(None) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "l", types.SimpleNamespace(x=scale_x, y=scale_y_10), False
        )
        assert len(warnings) == 0

    with pytest.warns(None) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "b", types.SimpleNamespace(x=scale_x, y=scale_y_10), True
        )
        assert len(warnings) == 0
    with pytest.warns(PlotnineWarning) as warnings:
        anno._annotation_geom._check_scale_consistency(
            "l", types.SimpleNamespace(x=scale_x, y=scale_y_10), True
        )
        assert len(warnings) == 1


def test_calc_ticks():
    assert _geom_logticks._calc_ticks(-1, 5, [1.0]) == pytest.approx(
        [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0]
    )
    assert _geom_logticks._calc_ticks(
        int(np.log10(0.001)), int(np.log10(1000)), [1.0]
    ) == pytest.approx([0.001, 0.01, 0.1, 1, 10, 100, 1000])
    assert _geom_logticks._calc_ticks(
        int(np.log10(0.001)), int(np.log10(1000)), [0.5]
    ) == pytest.approx(
        [0.0001 * 5, 0.001 * 5, 0.01 * 5, 0.1 * 5, 1 * 5, 10 * 5, 100 * 5]
    )
    assert _geom_logticks._calc_ticks(
        int(np.log10(0.001)), int(np.log10(1000)), [0.2]
    ) == pytest.approx(
        [0.0001 * 2, 0.001 * 2, 0.01 * 2, 0.1 * 2, 1 * 2, 10 * 2, 100 * 2]
    )

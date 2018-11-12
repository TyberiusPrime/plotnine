import numpy as np

from ..doctools import document
from .annotate import annotate
import pandas as pd
from .geom_rug import geom_rug
import mizani.transforms
import math
from ..coords import coord_flip
import warnings
from ..exceptions import PlotnineWarning


class _geom_logticks(geom_rug):
    """internal geom implementing drawing of annotation_logticks"""

    DEFAULT_AES = {}
    DEFAULT_PARAMS = {
        'stat': 'identity',
        'position': 'identity',
        'na_rm': False,
        'sides': 'bl',
        'alpha': 1,
        'color': 'black',
        'size': 0.5,
        'linetype': 'solid',
        'width': (1.2, 0.75, 0.4),
    }
    legend_geom = 'path'

    @staticmethod
    def _check_scale_consistency(sides, scales, is_coord_flip):
        x_is_log_10 = isinstance(scales.x.trans, mizani.transforms.log10_trans)
        y_is_log_10 = isinstance(scales.y.trans, mizani.transforms.log10_trans)
        if is_coord_flip:
            x_is_log_10, y_is_log_10 = y_is_log_10, x_is_log_10
        result = []
        if (not x_is_log_10 and ('t' in sides or 'b' in sides)):
            warnings.warn("annotation_logticks for x-axis,"
                          " but x-axis is not log10 - nonsensical marks show.",
                          PlotnineWarning)
        if (not y_is_log_10 and ('l' in sides or 'r' in sides)):
            warnings.warn("annotation_logticks for y-axis,"
                          " but y-axis is not log10 - nonsensical marks show.",
                          PlotnineWarning)
        return result

    @classmethod
    def draw_group(cls, ignored_data, panel_params, coord, ax, **params):
        if 'l' in params['sides'] or 'r' in params['sides']:
            ymin, ymax = panel_params['y_range']
            cls.draw_one_axis('y', ymin, ymax, panel_params, coord, ax, params)
        if 'b' in params['sides'] or 't' in params['sides']:
            xmin, xmax = panel_params['x_range']
            cls.draw_one_axis('x', xmin, xmax, panel_params, coord, ax, params)

    @staticmethod
    def _calc_ticks(lower_log, upper_log, marks_at):
        """Calculate log10 tick marks between two logs
        (input is -1..4, not 0.1..10000).
        Marks are set at the percentages defined by marks_at
        ([0..1, ...]])
        """
        result = []
        for l in range(lower_log, upper_log + 1):
            for m in marks_at:
                result.append(10**(l + np.log10(m)))
        return result

    @classmethod
    def draw_one_axis(cls, axis, min_value, max_value, panel_params, coord, ax,
                      params):
        cls._check_scale_consistency(params['sides'], panel_params['scales'],
                                     isinstance(coord, coord_flip))

        lower_log = int(math.floor(min_value))
        upper_log = int(math.ceil(max_value)) + 1
        major = np.log10(cls._calc_ticks(lower_log, upper_log, [1.0]))
        middle = np.log10(cls._calc_ticks(lower_log, upper_log, [0.5]))
        minor = np.log10(cls._calc_ticks(lower_log, upper_log,
                         [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]))

        all_widths = params.get('width', cls.DEFAULT_PARAMS['width'])
        if len(all_widths) != 3:
            raise ValueError(
                "widths for annotation_logticks must be a tuple of 3 floats")

        if 'width' in params:
            del params['width']

        for (positions, width) in [
            (major, all_widths[0]),
            (middle, all_widths[1]),
            (minor, all_widths[2]),
        ]:
            data = pd.DataFrame({
                axis: positions,
                'size': params['size'],
                'color': params['color'],
                'alpha': params['alpha'],
                'linetype': params['linetype'],
            })
            super().draw_group(
                data, panel_params, coord, ax, width=width, **params)


@document
class annotation_logticks(annotate):
    """
    Marginal log10 ticks.

    If added to a plot that does not have a log10 axis
    on the respective side, will add a log10 scale
    (replacing the existing scale).

    {usage}

    Parameters
    ----------
    {common_parameters}
    sides : str (default: bl)
        Sides onto which to draw the marks. Any combination
        chosen from the characters ``btlr``, for *bottom*, *top*,
        *left* or *right* side marks. If coord_flip() is used,
        these are the sides *after* the flip.

    width: tuple (default (1.2, 0.75, 0.4),)
        Width of the ticks drawn for full / half / tenth
        ticks relative to geom_rug default size.
    """

    def __init__(self,
                 sides='bl',
                 **kwargs):
        self.sides = sides
        self._annotation_geom = _geom_logticks(sides=sides, **kwargs)

    def __radd__(self, gg, inplace=False):
        return self._annotation_geom.__radd__(gg, inplace=inplace)

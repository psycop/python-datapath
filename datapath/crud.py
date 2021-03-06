from copy import deepcopy

from datapath.format import compact_path
from datapath.parser import parse_path
from datapath import constants as c
from datapath.walk import walk_path, walk


def set_path(data, path_string, value, copy=False):
    return set_path_parts(data, parse_path(path_string), value, copy)


def get_path(data, path_string, default=None):
    return get_path_parts(data, parse_path(path_string), default)


def find_path(data, path_string, on_mismatch=c.ON_MISMATCH_CONTINUE):
    return find_path_parts(data, parse_path(path_string), on_mismatch)


def flatten(input_data, formatter=compact_path):
    out = {}

    def _flatten(data_type, data, path, **_):
        if data_type & c.TYPE_LEAF:
            out[formatter(reversed(path), is_reversed=True)] = data

    walk(input_data, _flatten)

    return out


def unflatten(input_data, existing=None):
    if existing is None:
        existing = {}

    for path_string, value in input_data.iteritems():
        set_path(existing, path_string, value)

    return existing


# ----------------- #
# Path part methods

def find_path_parts(input_data, path_parts, on_mismatch=c.ON_MISMATCH_CONTINUE):
    items = []

    def _read(data, terminal, **_):
        if terminal:
            items.append(data)

        return c.WALK_CONTINUE

    walk_path(input_data, _read, path_parts, on_mismatch=on_mismatch)

    return items


def explain_path_parts(input_data, path_parts,
                       on_mismatch=c.ON_MISMATCH_CONTINUE):
    items = []

    def _read(data, path, terminal, **_):
        if terminal:
            items.append({'value': data, 'path': path})

        return c.WALK_CONTINUE

    walk_path(input_data, _read, path_parts, on_mismatch=on_mismatch)

    return items


def get_path_parts(input_data, path_parts, default=None):
    item = [default]

    def _read_one(data, terminal, **_):
        if terminal:
            item[0] = data

            return c.WALK_TERMINATE

        return c.WALK_CONTINUE

    walk_path(input_data, _read_one, path_parts,
              on_mismatch=c.ON_MISMATCH_CONTINUE)

    return item[0]


def set_path_parts(data, path_parts, value, copy=False):
    def _write(terminal, parent, key, **_):
        # Don't try and set values above the root
        if terminal and parent:
            parent[key] = deepcopy(value) if copy else value

        return c.WALK_CONTINUE

    walk_path(data, _write, path_parts, on_missing=c.ON_MISSING_CREATE)

    return data

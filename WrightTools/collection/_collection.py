"""Collection."""


# --- import --------------------------------------------------------------------------------------


import os
import shutil
import tempfile

import numpy as np

import h5py

from .. import data as wt_data


# --- define --------------------------------------------------------------------------------------


__all__ = ['Collection']


# --- classes -------------------------------------------------------------------------------------


class Collection(h5py.Group):
    """Nestable Collection of Data objects."""

    def __init__(self, filepath=None, parent=None, name=None, edit_local=False, **kwargs):
        """Create a ``Collection`` object.

        Parameters
        ----------
        channels : list
            A list of Channel objects. Channels are also inherited as
            attributes using the channel name: ``data.ai0``, for example.
        axes : list
            A list of Axis objects. Axes are also inherited as attributes using
            the axis name: ``data.w1``, for example.
        constants : list
            A list of Axis objects, each with exactly one point.
        **kwargs
            Additional keyword arguments are added to the attrs dictionary
            and to the natural namespace of the object (if possible).
        """
        # TODO: redo docstring
        # parse / create file
        if edit_local and filepath is None:
            raise Exception  # TODO: better exception
        if not edit_local:
            self.filepath = tempfile.NamedTemporaryFile(prefix='', suffix='.wt5').name
            if filepath:
                shutil.copyfile(src=filepath, dst=self.filepath)
        elif edit_local and filepath:
            self.filepath = filepath
        # parse / create group
        if parent is None:
            p = '/'
        else:
            p = parent + '/' + name
        file = h5py.File(self.filepath, 'a')
        if '__version__' not in file.attrs.keys():
            file.attrs['__version__'] = '0.0.0'
        file.require_group(p)
        h5py.Group.__init__(self, file[p].id)
        # assign
        self.source = kwargs.pop('source', None)  # TODO
        if name is None:
            name = self.attrs.get('name', 'collection')
        self.attrs.update(kwargs)
        self.attrs['class'] = 'Collection'
        self.attrs['name'] = name
        # load from file
        self.items = []
        for name in self.item_names:
            self.items.append(self[name])
        self.__version__  # assigns, if it doesn't already exist

    def __iter__(self):
        return iter([self[key] for key in self.item_names])

    def __repr__(self):
        return '<WrightTools.Collection \'{0}\' {1} at {2}>'.format(self.natural_name,
                                                                    self.item_names,
                                                                    '::'.join([self.filepath,
                                                                               self.name]))

    @property
    def __version__(self):
        return self.file.attrs['__version__']

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self.item_names[key]
        out = h5py.Group.__getitem__(self, key)
        if 'class' in out.attrs.keys():
            if out.attrs['class'] == 'Data':
                return wt_data.Data(filepath=self.filepath, parent=self.name, name=key)
        else:
            return out

    #def __setitem__():
    #    pass

    @property
    def natural_name(self):
        return self.attrs['name']

    @property
    def item_names(self):
        if 'item_names' not in self.attrs.keys():
            self.attrs['item_names'] = np.array([], dtype='S')
        return [s.decode() for s in self.attrs['item_names']]

    def add_collection(self, collection, position=None, **kwargs):
        if isinstance(collection, h5py.Group):
            self.copy(collection, collection.natural_name)
            #TODO use getitem?
            collection = Collection(self.filepath, self.name, collection.natural_name, True, **kwargs)
        else:
            collection = Collection(self.filepath, self.name, collection, True, **kwargs)
        if position is None:
            self.items.append(collection)
            self.attrs['item_names'] = np.append(self.attrs['item_names'], collection.natural_name.encode())
        else:
            self.items.insert(position, collection)
            self.attrs['item_names'] = np.insert(self.attrs['item_names'], position, collection.natural_name.encode())
        return collection

    def add_data(self, position=None, **kwargs):
        data = wt_data.Data(filepath=self.filepath, parent=self.name, edit_local=True, **kwargs)
        if position is None:
            self.items.append(data)
            self.attrs['item_names'] = np.append(self.attrs['item_names'], data.natural_name.encode())
        else:
            self.items.insert(position, data)
            self.attrs['item_names'] = np.insert(self.attrs['item_names'], position, data.natural_name.encode())
        return data

    def index():
        raise NotImplementedError

    def flush():
        self.file.flush()

    def save(self, filepath=None, verbose=True):
        # TODO: documentation
        self.file.flush()  # ensure all changes are written to file
        if filepath is None:
            filepath = os.path.join(os.getcwd(), self.natural_name + '.wt5')
        elif len(os.path.basename(filepath).split('.')) == 1:
            filepath += '.wt5'
        filepath = os.path.expanduser(filepath)
        shutil.copyfile(src=self.filepath, dst=filepath)
        if verbose:
            print(filepath)
        return filepath

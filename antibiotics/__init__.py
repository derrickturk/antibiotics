#  Copyright 2020 terminus data science, LLC

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import types
import typing
from typing import cast, Annotated, Any, Callable, Dict, Iterable, List
from typing import NamedTuple, Optional, TextIO, Tuple, Type, TypeVar

import dataclasses as dc

_T = TypeVar('_T')

TypeSerDeMap = Dict[
    Type[Any],
    Tuple[Callable[[Any], str], Callable[[str], Any]]
]
'''A serialization/deserialization function map by type.'''

class ExternalName(NamedTuple):
    '''Use with `typing.Annotated` to specify an external name for a member.

    For example, given:

    ```
    class Example(NamedTuple):
        x: Annotated[int, ExternalName('Fancy_X')]
    ```

    Objects of class `Example` will be read and written assuming the name
    "Fancy_X" appears in delimited-file headers for the column corresponding
    to the `x` data member.
    '''

    name: str
    '''The external name.'''

def _id(x: _T) -> _T:
    return x

def _bool_from_str(s: str) -> bool:
    if s == 'False':
        return False
    if s == 'True':
        return True
    raise ValueError(f'Unrecognized boolean value "{s}".')

def _none_from_str(s: str) -> None:
    if s == '':
        return None
    else:
        raise ValueError(f'Found "{s}"; expected empty string (NoneType).')

_TYPE_SERDE: TypeSerDeMap = {
    bool: (str, _bool_from_str),
    int: (str, int),
    float: (str, float),
    complex: (str, complex),
    str: (_id, _id),
    bytes: (lambda b: cast(str, b.decode('utf8')), lambda s: s.encode('utf8')),
    type(None): (lambda _: '', _none_from_str),
}

_BUF_SIZE: int = 1024

@dc.dataclass
class Delimited():
    '''a reader and writer for delimited data

    parameters may be specified when initializing a Delimited object as either
    positional or named arguments; the `__init__` signature is more-or-less:

    ```
    Delimited(sep=',', quote='"', escape='"', newline='\r\n',
      type_serde_ext=None)
    ```

    the default values are suitable for reading and writing "standard" CSV files

    the core concept behind antibiotics is the type-driven
      serialization/deserialization map

    this map is a dictionary from types `T` to tuples of a serialization
      function `Callable[[T], str]` and a deserialization function
      `Callable[[str], T]`

    entries provided in type_serde_ext will override any default entries
      for the same type

    default entries are provided for `bool`, `int`, `float`, `complex`,
      `str`, `bytes`, and `None`

    antibiotics automatically handles serialization/deserialization for types
      which are unions of types with map entries - for example, `Optional[T]`
      will use either the `None` serializer/deserializer or the `T`
      serializer/deserializer, depending on the runtime value; deserializers
      for union types are tried in order of declaration until one runs without
      raising an exception

    much like the `csv` module, files opened for use with `antibiotics` should
      be opened with `newline=''`
    '''

    sep: str = ','
    '''the separator between delimited entries [default `','`]'''

    quote: Optional[str] = '"'
    '''the character, if any, used to introduce and close quoted entries (which
      may include the delimiter verbatim) [default `'"'`]
    '''

    escape: Optional[str] = '"'
    '''the character, if any, used to escape verbatim quote characters occurring
      inside quoted entries [default `'"'`]
    '''

    newline: str = '\r\n'
    '''the character used to terminate lines; may occur inside quoted entries
      [default `'\r\n'`]
    '''

    type_serde_ext: dc.InitVar[Optional[TypeSerDeMap]] = None
    '''optionally, a dictionary containing additional entries for the
      type-driven serialization/deserialization map
    '''

    type_serde: TypeSerDeMap = dc.field(
            default_factory=_TYPE_SERDE.copy, init=False)

    def __post_init__(self, type_serde_ext: Optional[TypeSerDeMap]) -> None:
        if type_serde_ext is not None:
            self.type_serde.update(type_serde_ext)

    def write(self, cls: Type[_T], recs: Iterable[_T], stream: TextIO,
            header: bool = True) -> None:
        '''write a sequence of typed records to a stream, with or
          without a header
        '''
        if header:
            self.write_header(cls, stream)
        for r in recs:
            self.write_record(r, stream)

    def write_header(self, cls: Type[Any], stream: TextIO) -> None:
        '''write an appropriate header for a given record type to a stream'''
        stream.write(self._delimit(_field_names(cls)))
        stream.write(self.newline)

    def write_record(self, rec: _T, stream: TextIO) -> None:
        '''write a single typed record to a stream'''
        stream.write(self._delimit(self._render(rec)))
        stream.write(self.newline)

    def read_header(self, cls: Type[Any], stream: TextIO) -> None:
        '''read a header for a given record type from a stream, and check it
          against the expected field names, raising a `ValueError` on failure
        '''
        hdr = self._line(stream)
        expected = _field_names(cls)
        if hdr != expected:
            raise ValueError(
                f'Invalid header for provided type: expected {expected}, found {hdr}.')

    def read_record(self, cls: Type[_T], stream: TextIO) -> Optional[_T]:
        '''read a single typed record from a stream'''
        line = self._line(stream)
        if line is None:
            return None
        return self._parse(cls, line)

    def read(self, cls: Type[_T], stream: TextIO,
            header: bool = True) -> Iterable[_T]:
        '''lazily read a sequence of typed records from a stream, with or
          without a header
        '''
        if header:
            self.read_header(cls, stream)
        while True:
            rec = self.read_record(cls, stream)
            if rec is None:
                break
            yield rec

    def _delimit(self, elems: List[str]) -> str:
        quoted = list()
        for e in elems:
            if self.quote is not None and self.quote in e:
                if self.escape is not None:
                    e = e.replace(self.quote, self.escape + self.quote)
                else:
                    raise ValueError(
                        f'Quote {self.quote} appears in value "{e}" and no escape character is set.')

            if self.sep in e:
                if self.quote is not None:
                    quoted.append(f'{self.quote}{e}{self.quote}')
                else:
                    raise ValueError(
                        f'Separator {self.sep} appears in value "{e}" and no quote character is set.')
            else:
                quoted.append(e)

        return self.sep.join(quoted)

    def _render(self, rec: _T) -> List[str]:
        tys = _field_types(type(rec))
        vals = _field_vals(type(rec), rec)
        elems = list()
        for ty, v in zip(tys, vals):
            if _union_types(ty):
                # v could be one of several types: just use its runtime
                #   type as an index
                try:
                    elems.append(self.type_serde[type(v)][0](v))
                except KeyError as ex:
                    raise TypeError(
                            f'Unsupported type in serialization: {v}: {type(v)} as {ty}.'
                    ) from ex
            else:
                try:
                    elems.append(self.type_serde[ty][0](v))
                except KeyError as ex:
                    raise TypeError(
                        f'Unsupported type in serialization: {v} as {ty}.'
                    ) from ex
        return elems

    def _line(self, stream: TextIO) -> Optional[List[str]]:
        elems = list()
        this_elem: List[str] = list()
        in_quote = False
        in_escape = False
        nl_len = len(self.newline)
        did_nl_seek = False

        while True:
            pos = stream.tell()
            buf = stream.read(_BUF_SIZE)
            n = len(buf)
            if n == 0:
                # missing final terminator
                if this_elem:
                    elems.append(''.join(this_elem))
                    return elems
                return None

            for i in range(n):
                if in_escape and self.escape == self.quote:
                    if buf[i] == self.quote:
                        in_escape = False
                        this_elem.append(buf[i])
                        continue
                    else:
                        # that "escape" was a closing quote!
                        in_escape = False
                        in_quote = False
                elif in_escape:
                    this_elem.append(buf[i])
                    in_escape = False
                    continue

                if in_quote:
                    if buf[i] == self.escape:
                        in_escape = True
                        continue
                    if buf[i] == self.quote:
                        in_quote = False
                        continue
                    this_elem.append(buf[i])
                    continue

                if buf[i] == self.sep:
                    elems.append(''.join(this_elem))
                    this_elem = list()
                elif buf[i] == self.quote:
                    in_quote = True
                # handle the case where we can't check for newline because it's
                #   potentially split across reads by seeking to current
                #   position and trying again...
                elif i + nl_len > n and not did_nl_seek:
                    stream.seek(pos + i, 0)
                    did_nl_seek = True
                    break # to continue the while
                elif buf[i:i + nl_len] == self.newline:
                    did_nl_seek = False
                    elems.append(''.join(this_elem))
                    stream.seek(pos + i + nl_len, 0)
                    return elems
                else:
                    this_elem.append(buf[i])

    def _parse(self, cls: Type[_T], elems: List[str]) -> _T:
        tys = _field_types(cls)
        if len(elems) != len(tys):
            raise ValueError(
                f'Record length {len(elems)} does not match required field count ({len(tys)}).')
        vals: List[Any] = list()
        for ty, e in zip(tys, elems):
            un_tys = _union_types(ty)
            if un_tys:
                found = False
                for try_ty in un_tys:
                    try:
                        vals.append(self.type_serde[try_ty][1](e))
                        found = True
                        break
                    except KeyError as ex:
                        raise TypeError(
                                f'Unsupported type in deserialization: "{e}" as {try_ty}.'
                        ) from ex
                    except:
                        pass
                if not found:
                    raise ValueError(f'Unable to parse "{e}" as {ty}')
            else:
                try:
                    vals.append(self.type_serde[ty][1](e))
                except KeyError as ex:
                    raise TypeError(
                            f'Unsupported type in deserialization: "{e}" as {ty}.'
                    ) from ex
                except Exception as ex:
                    raise ValueError('Unable to parse "{e}" as {ty}.') from ex
        return cls(*vals)

def _field_names(cls: Type[Any]) -> List[str]:
    annots = typing.get_type_hints(cls, include_extras=True)
    names = []
    for name, annot in annots.items():
        if typing.get_origin(annot) is Annotated:
            ext_names = [
              n.name for n in typing.get_args(annot)
              if isinstance(n, ExternalName)
            ]

            if len(ext_names) == 0:
                names.append(name)
            elif len(ext_names) > 1:
                raise TypeError(
                  f'Too many ExternalName annotations for field {name}.')
            else:
                names.append(ext_names[0])
        else:
            names.append(name)
    return names

def _field_types(cls: Type[Any]) -> List[Type[Any]]:
    return list(typing.get_type_hints(cls).values())

def _field_vals(cls: Type[_T], rec: _T) -> List[Any]:
    try:
        return list(rec) # type: ignore
    except:
        pass
    try:
        return list(dc.astuple(rec)) # type: ignore
    except:
        pass
    raise ValueError("This type is not a NamedTuple or @dataclass.")

def _union_types(ty: Type[Any]) -> Optional[List[Type[Any]]]:
    # see: https://stackoverflow.com/questions/49171189/whats-the-correct-way-to-check-if-an-object-is-a-typing-generic
    origin = typing.get_origin(ty)
    if origin in (typing.Union, types.UnionType):
        args = typing.get_args(ty)
        # move NoneType to front of list, so it gets tried
        #   first in deserialization, ensuring "correct" behavior when
        #   deserializing types Optional[T] where the deserializer for T
        #   does not fail on a '' argument - that is, ensure we prioritize
        #   deserializing None for empty strings when necessary.
        return ([a for a in args if a is type(None)] +
                [a for a in args if a is not type(None)])
    else:
        return None

__all__ = [
    'TypeSerDeMap',
    'ExternalName',
    'Delimited',
]

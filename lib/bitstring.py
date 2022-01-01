
    bytepos -- The current byte position in the bitstring.
    bytes -- The bitstring as a bytes object.
    float -- Interpret as a floating point number.
    floatbe -- Interpret as a big-endian floating point number.
    floatle -- Interpret as a little-endian floating point number.
    floatne -- Interpret as a native-endian floating point number.
    hex -- The bitstring as a hexadecimal string.
    int -- Interpret as a two's complement signed integer.
    intbe -- Interpret as a big-endian signed integer.
    intle -- Interpret as a little-endian signed integer.
    intne -- Interpret as a native-endian signed integer.
    len -- Length of the bitstring in bits.
    oct -- The bitstring as an octal string.
    pos -- The current bit position in the bitstring.
    se -- Interpret as a signed exponential-Golomb code.
    ue -- Interpret as an unsigned exponential-Golomb code.
    sie -- Interpret as a signed interleaved exponential-Golomb code.
    uie -- Interpret as an unsigned interleaved exponential-Golomb code.
    uint -- Interpret as a two's complement unsigned integer.
    uintbe -- Interpret as a big-endian unsigned integer.
    uintle -- Interpret as a little-endian unsigned integer.
    uintne -- Interpret as a native-endian unsigned integer.

    """

    __slots__ = ('_pos',)

    def __init__(self, auto=None, length=None, offset=None, pos=0, **kwargs):
        """Either specify an 'auto' initialiser:
        auto -- a string of comma separated tokens, an integer, a file object,
                a bytearray, a boolean iterable or another bitstring.

        Or initialise via **kwargs with one (and only one) of:
        bytes -- raw data as a string, for example read from a binary file.
        bin -- binary string representation, e.g. '0b001010'.
        hex -- hexadecimal string representation, e.g. '0x2ef'
        oct -- octal string representation, e.g. '0o777'.
        uint -- an unsigned integer.
        int -- a signed integer.
        float -- a floating point number.
        uintbe -- an unsigned big-endian whole byte integer.
        intbe -- a signed big-endian whole byte integer.
        floatbe - a big-endian floating point number.
        uintle -- an unsigned little-endian whole byte integer.
        intle -- a signed little-endian whole byte integer.
        floatle -- a little-endian floating point number.
        uintne -- an unsigned native-endian whole byte integer.
        intne -- a signed native-endian whole byte integer.
        floatne -- a native-endian floating point number.
        se -- a signed exponential-Golomb code.
        ue -- an unsigned exponential-Golomb code.
        sie -- a signed interleaved exponential-Golomb code.
        uie -- an unsigned interleaved exponential-Golomb code.
        bool -- a boolean (True or False).
        filename -- a file which will be opened in binary read-only mode.

        Other keyword arguments:
        length -- length of the bitstring in bits, if needed and appropriate.
                  It must be supplied for all integer and float initialisers.
        offset -- bit offset to the data. These offset bits are
                  ignored and this is intended for use when
                  initialising using 'bytes' or 'filename'.
        pos -- Initial bit position, defaults to 0.

        """
        pass

    def __new__(cls, auto=None, length=None, offset=None, pos=0, **kwargs):
        x = super(ConstBitStream, cls).__new__(cls)
        x._initialise(auto, length, offset, **kwargs)
        x._pos = x._datastore.bitlength + pos if pos < 0 else pos
        if x._pos < 0 or x._pos > x._datastore.bitlength:
            raise CreationError("Cannot set pos to {0} when length is {1}".format(pos, x._datastore.bitlength))
        return x

    def _setbytepos(self, bytepos):
        """Move to absolute byte-aligned position in stream."""
        self._setbitpos(bytepos * 8)

    def _getbytepos(self):
        """Return the current position in the stream in bytes. Must be byte aligned."""
        if self._pos % 8:
            raise ByteAlignError("Not byte aligned in _getbytepos().")
        return self._pos // 8

    def _setbitpos(self, pos):
        """Move to absolute position bit in bitstream."""
        if pos < 0:
            raise ValueError("Bit position cannot be negative.")
        if pos > self.len:
            raise ValueError("Cannot seek past the end of the data.")
        self._pos = pos

    def _getbitpos(self):
        """Return the current position in the stream in bits."""
        return self._pos

    def _clear(self):
        Bits._clear(self)
        self._pos = 0

    def __copy__(self):
        """Return a new copy of the ConstBitStream for the copy module."""
        # Note that if you want a new copy (different ID), use _copy instead.
        # The copy can use the same datastore as it's immutable.
        s = ConstBitStream()
        s._datastore = self._datastore
        # Reset the bit position, don't copy it.
        s._pos = 0
        return s

    def __add__(self, bs):
        """Concatenate bitstrings and return new bitstring.

        bs -- the bitstring to append.

        """
        s = Bits.__add__(self, bs)
        s._pos = 0
        return s

    def read(self, fmt):
        """Interpret next bits according to the format string and return result.

        fmt -- Token string describing how to interpret the next bits.

        Token examples: 'int:12'    : 12 bits as a signed integer
                        'uint:8'    : 8 bits as an unsigned integer
                        'float:64'  : 8 bytes as a big-endian float
                        'intbe:16'  : 2 bytes as a big-endian signed integer
                        'uintbe:16' : 2 bytes as a big-endian unsigned integer
                        'intle:32'  : 4 bytes as a little-endian signed integer
                        'uintle:32' : 4 bytes as a little-endian unsigned integer
                        'floatle:64': 8 bytes as a little-endian float
                        'intne:24'  : 3 bytes as a native-endian signed integer
                        'uintne:24' : 3 bytes as a native-endian unsigned integer
                        'floatne:32': 4 bytes as a native-endian float
                        'hex:80'    : 80 bits as a hex string
                        'oct:9'     : 9 bits as an octal string
                        'bin:1'     : single bit binary string
                        'ue'        : next bits as unsigned exp-Golomb code
                        'se'        : next bits as signed exp-Golomb code
                        'uie'       : next bits as unsigned interleaved exp-Golomb code
                        'sie'       : next bits as signed interleaved exp-Golomb code
                        'bits:5'    : 5 bits as a bitstring
                        'bytes:10'  : 10 bytes as a bytes object
                        'bool'      : 1 bit as a bool
                        'pad:3'     : 3 bits of padding to ignore - returns None

        fmt may also be an integer, which will be treated like the 'bits' token.

        The position in the bitstring is advanced to after the read items.

        Raises ReadError if not enough bits are available.
        Raises ValueError if the format is not understood.

        """
        if isinstance(fmt, numbers.Integral):
            if fmt < 0:
                raise ValueError("Cannot read negative amount.")
            if fmt > self.len - self._pos:
                raise ReadError("Cannot read {0} bits, only {1} available.",
                                fmt, self.len - self._pos)
            bs = self._slice(self._pos, self._pos + fmt)
            self._pos += fmt
            return bs
        p = self._pos
        _, token = tokenparser(fmt)
        if len(token) != 1:
            self._pos = p
            raise ValueError("Format string should be a single token, not {0} "
                             "tokens - use readlist() instead.".format(len(token)))
        name, length, _ = token[0]
        if length is None:
            length = self.len - self._pos
        value, self._pos = self._readtoken(name, self._pos, length)
        return value

    def readlist(self, fmt, **kwargs):
        """Interpret next bits according to format string(s) and return list.

        fmt -- A single string or list of strings with comma separated tokens
               describing how to interpret the next bits in the bitstring. Items
               can also be integers, for reading new bitstring of the given length.
        kwargs -- A dictionary or keyword-value pairs - the keywords used in the
                  format string will be replaced with their given value.

        The position in the bitstring is advanced to after the read items.

        Raises ReadError is not enough bits are available.
        Raises ValueError if the format is not understood.

        See the docstring for 'read' for token examples. 'pad' tokens are skipped
        and not added to the returned list.

        >>> h, b1, b2 = s.readlist('hex:20, bin:5, bin:3')
        >>> i, bs1, bs2 = s.readlist(['uint:12', 10, 10])

        """
        value, self._pos = self._readlist(fmt, self._pos, **kwargs)
        return value

    def readto(self, bs, bytealigned=None):
        """Read up to and including next occurrence of bs and return result.

        bs -- The bitstring to find. An integer is not permitted.
        bytealigned -- If True the bitstring will only be
                       found on byte boundaries.

        Raises ValueError if bs is empty.
        Raises ReadError if bs is not found.

        """
        if isinstance(bs, numbers.Integral):
            raise ValueError("Integers cannot be searched for")
        bs = Bits(bs)
        oldpos = self._pos
        p = self.find(bs, self._pos, bytealigned=bytealigned)
        if not p:
            raise ReadError("Substring not found")
        self._pos += bs.len
        return self._slice(oldpos, self._pos)

    def peek(self, fmt):
        """Interpret next bits according to format string and return result.

        fmt -- Token string describing how to interpret the next bits.

        The position in the bitstring is not changed. If not enough bits are
        available then all bits to the end of the bitstring will be used.

        Raises ReadError if not enough bits are available.
        Raises ValueError if the format is not understood.

        See the docstring for 'read' for token examples.

        """
        pos_before = self._pos
        value = self.read(fmt)
        self._pos = pos_before
        return value

    def peeklist(self, fmt, **kwargs):
        """Interpret next bits according to format string(s) and return list.

        fmt -- One or more strings with comma separated tokens describing
               how to interpret the next bits in the bitstring.
        kwargs -- A dictionary or keyword-value pairs - the keywords used in the
                  format string will be replaced with their given value.

        The position in the bitstring is not changed. If not enough bits are
        available then all bits to the end of the bitstring will be used.

        Raises ReadError if not enough bits are available.
        Raises ValueError if the format is not understood.

        See the docstring for 'read' for token examples.

        """
        pos = self._pos
        return_values = self.readlist(fmt, **kwargs)
        self._pos = pos
        return return_values

    def bytealign(self):
        """Align to next byte and return number of skipped bits.

        Raises ValueError if the end of the bitstring is reached before
        aligning to the next byte.

        """
        skipped = (8 - (self._pos % 8)) % 8
        self.pos += self._offset + skipped
        assert self._assertsanity()
        return skipped

    pos = property(_getbitpos, _setbitpos,
                   doc="""The position in the bitstring in bits. Read and write.
                      """)
    bitpos = property(_getbitpos, _setbitpos,
                      doc="""The position in the bitstring in bits. Read and write.
                      """)
    bytepos = property(_getbytepos, _setbytepos,
                       doc="""The position in the bitstring in bytes. Read and write.
                      """)


class BitStream(ConstBitStream, BitArray):
    """A container or stream holding a mutable sequence of bits

    Subclass of the ConstBitStream and BitArray classes. Inherits all of
    their methods.

    Methods:

    all() -- Check if all specified bits are set to 1 or 0.
    any() -- Check if any of specified bits are set to 1 or 0.
    append() -- Append a bitstring.
    bytealign() -- Align to next byte boundary.
    byteswap() -- Change byte endianness in-place.
    count() -- Count the number of bits set to 1 or 0.
    cut() -- Create generator of constant sized chunks.
    endswith() -- Return whether the bitstring ends with a sub-string.
    find() -- Find a sub-bitstring in the current bitstring.
    findall() -- Find all occurrences of a sub-bitstring in the current bitstring.
    insert() -- Insert a bitstring.
    invert() -- Flip bit(s) between one and zero.
    join() -- Join bitstrings together using current bitstring.
    overwrite() -- Overwrite a section with a new bitstring.
    peek() -- Peek at and interpret next bits as a single item.
    peeklist() -- Peek at and interpret next bits as a list of items.
    prepend() -- Prepend a bitstring.
    read() -- Read and interpret next bits as a single item.
    readlist() -- Read and interpret next bits as a list of items.
    replace() -- Replace occurrences of one bitstring with another.
    reverse() -- Reverse bits in-place.
    rfind() -- Seek backwards to find a sub-bitstring.
    rol() -- Rotate bits to the left.
    ror() -- Rotate bits to the right.
    set() -- Set bit(s) to 1 or 0.
    split() -- Create generator of chunks split by a delimiter.
    startswith() -- Return whether the bitstring starts with a sub-bitstring.
    tobytes() -- Return bitstring as bytes, padding if needed.
    tofile() -- Write bitstring to file, padding if needed.
    unpack() -- Interpret bits using format string.

    Special methods:

    Mutating operators are available: [], <<=, >>=, +=, *=, &=, |= and ^=
    in addition to [], ==, !=, +, *, ~, <<, >>, &, | and ^.

    Properties:

    bin -- The bitstring as a binary string.
    bool -- For single bit bitstrings, interpret as True or False.
    bytepos -- The current byte position in the bitstring.
    bytes -- The bitstring as a bytes object.
    float -- Interpret as a floating point number.
    floatbe -- Interpret as a big-endian floating point number.
    floatle -- Interpret as a little-endian floating point number.
    floatne -- Interpret as a native-endian floating point number.
    hex -- The bitstring as a hexadecimal string.
    int -- Interpret as a two's complement signed integer.
    intbe -- Interpret as a big-endian signed integer.
    intle -- Interpret as a little-endian signed integer.
    intne -- Interpret as a native-endian signed integer.
    len -- Length of the bitstring in bits.
    oct -- The bitstring as an octal string.
    pos -- The current bit position in the bitstring.
    se -- Interpret as a signed exponential-Golomb code.
    ue -- Interpret as an unsigned exponential-Golomb code.
    sie -- Interpret as a signed interleaved exponential-Golomb code.
    uie -- Interpret as an unsigned interleaved exponential-Golomb code.
    uint -- Interpret as a two's complement unsigned integer.
    uintbe -- Interpret as a big-endian unsigned integer.
    uintle -- Interpret as a little-endian unsigned integer.
    uintne -- Interpret as a native-endian unsigned integer.

    """

    __slots__ = ()

    # As BitStream objects are mutable, we shouldn't allow them to be hashed.
    __hash__ = None

    def __init__(self, auto=None, length=None, offset=None, pos=0, **kwargs):
        """Either specify an 'auto' initialiser:
        auto -- a string of comma separated tokens, an integer, a file object,
                a bytearray, a boolean iterable or another bitstring.

        Or initialise via **kwargs with one (and only one) of:
        bytes -- raw data as a string, for example read from a binary file.
        bin -- binary string representation, e.g. '0b001010'.
        hex -- hexadecimal string representation, e.g. '0x2ef'
        oct -- octal string representation, e.g. '0o777'.
        uint -- an unsigned integer.
        int -- a signed integer.
        float -- a floating point number.
        uintbe -- an unsigned big-endian whole byte integer.
        intbe -- a signed big-endian whole byte integer.
        floatbe - a big-endian floating point number.
        uintle -- an unsigned little-endian whole byte integer.
        intle -- a signed little-endian whole byte integer.
        floatle -- a little-endian floating point number.
        uintne -- an unsigned native-endian whole byte integer.
        intne -- a signed native-endian whole byte integer.
        floatne -- a native-endian floating point number.
        se -- a signed exponential-Golomb code.
        ue -- an unsigned exponential-Golomb code.
        sie -- a signed interleaved exponential-Golomb code.
        uie -- an unsigned interleaved exponential-Golomb code.
        bool -- a boolean (True or False).
        filename -- a file which will be opened in binary read-only mode.

        Other keyword arguments:
        length -- length of the bitstring in bits, if needed and appropriate.
                  It must be supplied for all integer and float initialisers.
        offset -- bit offset to the data. These offset bits are
                  ignored and this is intended for use when
                  initialising using 'bytes' or 'filename'.
        pos -- Initial bit position, defaults to 0.

        """
        # For mutable BitStreams we always read in files to memory:
        if not isinstance(self._datastore, (ByteStore, ConstByteStore)):
            self._ensureinmemory()

    def __new__(cls, auto=None, length=None, offset=None, pos=0, **kwargs):
        x = super(BitStream, cls).__new__(cls)
        y = ConstBitStream.__new__(BitStream, auto, length, offset, pos, **kwargs)
        x._datastore = ByteStore(y._datastore._rawarray[:],
                                          y._datastore.bitlength,
                                          y._datastore.offset)
        x._pos = y._pos
        return x

    def __copy__(self):
        """Return a new copy of the BitStream."""
        s_copy = BitStream()
        s_copy._pos = 0
        if not isinstance(self._datastore, ByteStore):
            # Let them both point to the same (invariant) array.
            # If either gets modified then at that point they'll be read into memory.
            s_copy._datastore = self._datastore
        else:
            s_copy._datastore = ByteStore(self._datastore._rawarray[:],
                                          self._datastore.bitlength,
                                          self._datastore.offset)
        return s_copy

    def prepend(self, bs):
        """Prepend a bitstring to the current bitstring.

        bs -- The bitstring to prepend.

        """
        bs = self._converttobitstring(bs)
        self._addleft(bs)
        self._pos += bs.len


def pack(fmt, *values, **kwargs):
    """Pack the values according to the format string and return a new BitStream.

    fmt -- A single string or a list of strings with comma separated tokens
           describing how to create the BitStream.
    values -- Zero or more values to pack according to the format.
    kwargs -- A dictionary or keyword-value pairs - the keywords used in the
              format string will be replaced with their given value.

    Token examples: 'int:12'    : 12 bits as a signed integer
                    'uint:8'    : 8 bits as an unsigned integer
                    'float:64'  : 8 bytes as a big-endian float
                    'intbe:16'  : 2 bytes as a big-endian signed integer
                    'uintbe:16' : 2 bytes as a big-endian unsigned integer
                    'intle:32'  : 4 bytes as a little-endian signed integer
                    'uintle:32' : 4 bytes as a little-endian unsigned integer
                    'floatle:64': 8 bytes as a little-endian float
                    'intne:24'  : 3 bytes as a native-endian signed integer
                    'uintne:24' : 3 bytes as a native-endian unsigned integer
                    'floatne:32': 4 bytes as a native-endian float
                    'hex:80'    : 80 bits as a hex string
                    'oct:9'     : 9 bits as an octal string
                    'bin:1'     : single bit binary string
                    'ue' / 'uie': next bits as unsigned exp-Golomb code
                    'se' / 'sie': next bits as signed exp-Golomb code
                    'bits:5'    : 5 bits as a bitstring object
                    'bytes:10'  : 10 bytes as a bytes object
                    'bool'      : 1 bit as a bool
                    'pad:3'     : 3 zero bits as padding

    >>> s = pack('uint:12, bits', 100, '0xffe')
    >>> t = pack(['bits', 'bin:3'], s, '111')
    >>> u = pack('uint:8=a, uint:8=b, uint:55=a', a=6, b=44)

    """
    tokens = []
    if isinstance(fmt, basestring):
        fmt = [fmt]
    try:
        for f_item in fmt:
            _, tkns = tokenparser(f_item, tuple(sorted(kwargs.keys())))
            tokens.extend(tkns)
    except ValueError as e:
        raise CreationError(*e.args)
    value_iter = iter(values)
    s = BitStream()
    try:
        for name, length, value in tokens:
            # If the value is in the kwd dictionary then it takes precedence.
            if value in kwargs:
                value = kwargs[value]
            # If the length is in the kwd dictionary then use that too.
            if length in kwargs:
                length = kwargs[length]
            # Also if we just have a dictionary name then we want to use it
            if name in kwargs and length is None and value is None:
                s._append(kwargs[name])
                continue
            if length is not None:
                length = int(length)
            if value is None and name != 'pad':
                # Take the next value from the ones provided
                value = next(value_iter)
            s._addright(BitStream._init_with_token(name, length, value))
    except StopIteration:
        raise CreationError("Not enough parameters present to pack according to the "
                            "format. {0} values are needed.", len(tokens))
    try:
        next(value_iter)
    except StopIteration:
        # Good, we've used up all the *values.
        return s
    raise CreationError("Too many parameters present to pack according to the format.")


# Whether to label the Least Significant Bit as bit 0. Default is False. Experimental feature.
_lsb0 = False

# Dictionary that maps token names to the function that reads them. Is set in next function.
name_to_read = {}


def _switch_lsb0_methods(lsb0):
    global _lsb0
    _lsb0 = lsb0
    if lsb0:
        ConstByteStore.getbit = ConstByteStore._getbit_lsb0
        Bits._find = Bits._find_lsb0
        Bits._slice = Bits._slice_lsb0
        BitArray._overwrite = BitArray._overwrite_lsb0
        BitArray._insert = BitArray._insert_lsb0
        BitArray._delete = BitArray._delete_lsb0
        BitArray._ror = BitArray._rol_msb0
        BitArray._rol = BitArray._ror_msb0
        ByteStore.setbit = ByteStore._setbit_lsb0
        ByteStore.unsetbit = ByteStore._unsetbit_lsb0
        ByteStore.invertbit = ByteStore._invertbit_lsb0
        BitArray._append = BitArray._append_lsb0
        BitArray._prepend = BitArray._append_msb0  # An LSB0 prepend is an MSB0 append
        Bits._readuint = Bits._readuint_lsb0
        Bits._truncatestart = Bits._truncateright
        Bits._truncateend = Bits._truncateleft
        Bits._validate_slice = Bits._validate_slice_lsb0
    else:
        ConstByteStore.getbit = ConstByteStore._getbit_msb0
        Bits._find = Bits._find_msb0
        Bits._slice = Bits._slice_msb0
        BitArray._overwrite = BitArray._overwrite_msb0
        BitArray._insert = BitArray._insert_msb0
        BitArray._delete = BitArray._delete_msb0
        BitArray._ror = BitArray._ror_msb0
        BitArray._rol = BitArray._rol_msb0
        ByteStore.setbit = ByteStore._setbit_msb0
        ByteStore.unsetbit = ByteStore._unsetbit_msb0
        ByteStore.invertbit = ByteStore._invertbit_msb0
        BitArray._append = BitArray._append_msb0
        BitArray._prepend = BitArray._append_lsb0
        Bits._readuint = Bits._readuint_msb0
        Bits._truncatestart = Bits._truncateleft
        Bits._truncateend = Bits._truncateright
        Bits._validate_slice = Bits._validate_slice_msb0

    global name_to_read
    name_to_read = {'uint': Bits._readuint,
                    'uintle': Bits._readuintle,
                    'uintbe': Bits._readuintbe,
                    'uintne': Bits._readuintne,
                    'int': Bits._readint,
                    'intle': Bits._readintle,
                    'intbe': Bits._readintbe,
                    'intne': Bits._readintne,
                    'float': Bits._readfloat,
                    'floatbe': Bits._readfloat,  # floatbe is a synonym for float
                    'floatle': Bits._readfloatle,
                    'floatne': Bits._readfloatne,
                    'hex': Bits._readhex,
                    'oct': Bits._readoct,
                    'bin': Bits._readbin,
                    'bits': Bits._readbits,
                    'bytes': Bits._readbytes,
                    'ue': Bits._readue,
                    'se': Bits._readse,
                    'uie': Bits._readuie,
                    'sie': Bits._readsie,
                    'bool': Bits._readbool,
                    }


def set_lsb0(v=True):
    """Experimental method changing the bit numbering so that the least significant bit is bit 0"""
    _switch_lsb0_methods(v)


def set_msb0(v=True):
    """Experimental method to reset the bit numbering so that the most significant bit is bit 0"""
    set_lsb0(not v)


# Initialise the default behaviour
set_msb0()


# Dictionaries for mapping init keywords with init functions.
init_with_length_and_offset = {'bytes': Bits._setbytes_safe,
                               'filename': Bits._setfile,
                               }

init_with_length_only = {'uint': Bits._setuint,
                         'int': Bits._setint,
                         'float': Bits._setfloat,
                         'uintbe': Bits._setuintbe,
                         'intbe': Bits._setintbe,
                         'floatbe': Bits._setfloat,
                         'uintle': Bits._setuintle,
                         'intle': Bits._setintle,
                         'floatle': Bits._setfloatle,
                         'uintne': Bits._setuintne,
                         'intne': Bits._setintne,
                         'floatne': Bits._setfloatne,
                         }

init_without_length_or_offset = {'bin': Bits._setbin_safe,
                                 'hex': Bits._sethex,
                                 'oct': Bits._setoct,
                                 'ue': Bits._setue,
                                 'se': Bits._setse,
                                 'uie': Bits._setuie,
                                 'sie': Bits._setsie,
                                 'bool': Bits._setbool,
                                 }


# Aliases for backward compatibility
ConstBitArray = Bits
BitString = BitStream

__all__ = ['ConstBitArray', 'ConstBitStream', 'BitStream', 'BitArray',
           'Bits', 'BitString', 'pack', 'Error', 'ReadError', 'InterpretError',
           'ByteAlignError', 'CreationError', 'bytealigned', 'set_lsb0', 'set_msb0']


def main():
    # check if final parameter is an interpretation string
    fp = sys.argv[-1]
    if fp == '--help' or len(sys.argv) == 1:
        print("""Create and interpret a bitstring from command-line parameters.

Command-line parameters are concatenated and a bitstring created
from them. If the final parameter is either an interpretation string
or ends with a '.' followed by an interpretation string then that
interpretation of the bitstring will be used when printing it.

Typical usage might be invoking the Python module from a console
as a one-off calculation:

$ python -m bitstring int:16=-400
0xfe70
$ python -m bitstring float:32=0.2 bin
00111110010011001100110011001101
$ python -m bitstring 0xff 3*0b01,0b11 uint
65367
$ python -m bitstring hex=01, uint:12=352.hex
01160

This feature is experimental and is subject to change or removal.
        """)
    elif fp in name_to_read.keys():
        # concatenate all other parameters and interpret using the final one
        b1 = Bits(','.join(sys.argv[1: -1]))
        print(b1._readtoken(fp, 0, b1.__len__())[0])
    else:
        # does final parameter end with a dot then an interpretation string?
        interp = fp[fp.rfind('.') + 1:]
        if interp in name_to_read.keys():
            sys.argv[-1] = fp[:fp.rfind('.')]
            b1 = Bits(','.join(sys.argv[1:]))
            print(b1._readtoken(interp, 0, b1.__len__())[0])
        else:
            # No interpretation - just use default print
            b1 = Bits(','.join(sys.argv[1:]))
            print(b1)


if __name__ == '__main__':
    main()

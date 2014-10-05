from hippy.builtin import wrap, Optional
from rpython.rtyper.lltypesystem import rffi, lltype

from hippy.module.bzip2.c_bzip2 import (
    c_bz_buff_to_buff_compress, c_bz_buff_to_buff_decompress,
    BZ_OK, BZ_STREAM_END)


class Bz2Error(Exception):
    def __init__(self, errno):
        self.errno = errno

def _bzcompress(source, blocksize=4, workfactor=0):
    source_len = len(source)
    dest_len = int(source_len * 1.2) + 600
    ll_destLen = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
    ll_destLen[0] = rffi.cast(rffi.INT, dest_len)
    ll_dest = lltype.malloc(rffi.CCHARP.TO, dest_len, flavor='raw')

    with rffi.scoped_str2charp(source) as ll_source:
        errno = c_bz_buff_to_buff_compress(
            ll_dest, ll_destLen, ll_source, len(source),
            blocksize, 0, workfactor)
    if errno == BZ_OK:
        s = rffi.cast(rffi.SIGNED, ll_destLen[0])
        lltype.free(ll_destLen, flavor='raw')
        return rffi.charpsize2str(ll_dest, s)
    lltype.free(ll_destLen, flavor='raw')
    raise Bz2Error(errno)


def _bzdecompress(source, small=0):
    source_len = len(source)
    dest_len = source_len * 10
    ll_destLen = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
    ll_destLen[0] = rffi.cast(rffi.INT, dest_len)
    ll_dest = lltype.malloc(rffi.CCHARP.TO, dest_len, flavor='raw')

    with rffi.scoped_str2charp(source) as ll_source:
        errno = c_bz_buff_to_buff_decompress(
            ll_dest, ll_destLen, ll_source, len(source), small, 0)
    if errno == BZ_OK or errno == BZ_STREAM_END:
        s = rffi.cast(rffi.SIGNED, ll_destLen[0])
        lltype.free(ll_destLen, flavor='raw')
        return rffi.charpsize2str(ll_dest, s)
    lltype.free(ll_destLen, flavor='raw')
    raise Bz2Error(errno)


@wrap(['interp', str, Optional(int), Optional(int)])
def bzcompress(interp, source, blocksize=4, workfactor=0):
    try:
        res = _bzcompress(source, blocksize=blocksize, workfactor=workfactor)
        return interp.space.wrap(res)
    except Bz2Error as e:
        return interp.space.newint(e.errno)


@wrap(['interp', str, Optional(int)])
def bzdecompress(interp, source, small=0):
    try:
        res = _bzdecompress(source, small=small)
        return interp.space.wrap(res)
    except Bz2Error as e:
        return interp.space.newint(e.errno)

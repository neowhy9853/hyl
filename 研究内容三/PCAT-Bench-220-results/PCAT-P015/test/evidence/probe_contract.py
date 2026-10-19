#!/usr/bin/env python3
"""PCA-0001/PCA-0002 contract probe. Usage: <python> probe_contract.py <version> <output_dir>"""
import os, sys, json, struct, tempfile, shutil
import zipfile
from zipfile import ZipInfo

_MASK_UTF_FILENAME = 1 << 11
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'unknown'
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else '.'
results = []

def record(tid, cat, val, detail=''):
    results.append({'test_id':tid,'version':VERSION,'category':cat,'value':str(val),'detail':detail})

def mk_zi(name, fb=0):
    zi = ZipInfo(name)
    zi.flag_bits = fb; zi.compress_type = zipfile.ZIP_STORED
    zi.CRC = 0; zi.compress_size = 0; zi.file_size = 0
    zi.header_offset = 0; zi._end_offset = None
    zi.internal_attr = 0; zi.external_attr = 0
    zi.extra = b''; zi.comment = b''
    zi.extract_version = 10; zi.create_version = 10
    zi.create_system = 3; zi.reserved = 0; zi.volume = 0
    return zi

def ph(header):
    fb = struct.unpack_from('<H', header, 6)[0]
    return fb, header[30:30+struct.unpack_from('<H', header, 26)[0]].hex()

def raw_cp437_zip(fbytes):
    fname = fbytes.decode('cp437')
    td = tempfile.mkdtemp(); zp = os.path.join(td, 'z.zip')
    try:
        with zipfile.ZipFile(zp, 'w') as zf: zf.writestr(fname, b'x')
        with open(zp, 'rb') as f: d = bytearray(f.read())
        lf = d[6]|(d[7]<<8); lf &= ~_MASK_UTF_FILENAME
        d[6]=lf&0xFF; d[7]=(lf>>8)&0xFF
        d[26]=len(fbytes)&0xFF; d[27]=(len(fbytes)>>8)&0xFF
        for i,b in enumerate(fbytes): d[30+i]=b
        cs = d.find(b'PK\x01\x02')
        if cs>=0:
            cf = d[cs+8]|(d[cs+9]<<8); cf &= ~_MASK_UTF_FILENAME
            d[cs+8]=cf&0xFF; d[cs+9]=(cf>>8)&0xFF
            d[cs+28]=len(fbytes)&0xFF; d[cs+29]=(len(fbytes)>>8)&0xFF
            for i,b in enumerate(fbytes): d[cs+46+i]=b
        return bytes(d)
    finally:
        shutil.rmtree(td)

def test_all():
    # FileHeader cp437 names, flag_bits=0
    for tid,real in [('fuenf','fünf'),('cafe','café'),('resume','résumé'),('muenchen','München')]:
        fb,fh = ph(mk_zi(real,0).FileHeader())
        record(f'fh-cp437-{tid}','OUTPUT_FORMAT_CHANGE',f'flags={fb:#06x} bytes={fh}')

    # FileHeader cp437 names, flag_bits=UTF8
    for tid,real in [('fuenf','fünf'),('cafe','café'),('resume','résumé'),('muenchen','München')]:
        fb,fh = ph(mk_zi(real,_MASK_UTF_FILENAME).FileHeader())
        record(f'fh-utf8flag-{tid}','OUTPUT_FORMAT_CHANGE',f'flags={fb:#06x} bytes={fh}')

    # ASCII names with UTF-8 flag
    for n in ['hello.txt','simple','test_file.zip']:
        fb,fh = ph(mk_zi(n,_MASK_UTF_FILENAME).FileHeader())
        record(f'ascii-{n}','OUTPUT_FORMAT_CHANGE',f'flags={fb:#06x} bytes={fh}')

    # Unicode-only names, flag_bits=0
    for tid,real in [('nihao','你好'),('japan','日本語'),('korea','한국어'),('sao','São Paulo')]:
        fb,fh = ph(mk_zi(real,0).FileHeader())
        record(f'unicode-{tid}','OUTPUT_FORMAT_CHANGE',f'flags={fb:#06x} bytes={fh}')

    # _encodeFilenameFlags flag clearing
    _,rf = mk_zi('pure_ascii.txt',_MASK_UTF_FILENAME)._encodeFilenameFlags()
    record('flagbits-clearing','OUTPUT_FORMAT_CHANGE',f'resulting_flags={rf:#06x}')

    # Append preservation
    fbts = 'fünf'.encode('cp437')
    raw = raw_cp437_zip(fbts)
    td = tempfile.mkdtemp(); zp = os.path.join(td, 't.zip')
    try:
        with open(zp,'wb') as f: f.write(raw)
        with zipfile.ZipFile(zp,'a') as zf: zf.writestr('n.txt','n')
        with zipfile.ZipFile(zp,'r') as zf:
            orig = [i for i in zf.infolist() if i.filename!='n.txt'][0]
        record('append-preservation','SIDE_EFFECT_CHANGE',
               f'orig_flag_bits={orig.flag_bits:#06x} names={[i.filename for i in zf.infolist()]}')
    finally:
        shutil.rmtree(td)

    # New write flag_bits
    td = tempfile.mkdtemp(); zp = os.path.join(td, 'n.zip')
    try:
        with zipfile.ZipFile(zp,'w') as zf:
            zf.writestr('a.txt','x'); zf.writestr('b.txt','x')
        with zipfile.ZipFile(zp,'r') as zf:
            for i in zf.infolist():
                record(f'newwrite-{i.filename}','SIDE_EFFECT_CHANGE',f'flag_bits={i.flag_bits:#06x}')
    finally:
        shutil.rmtree(td)

if __name__=='__main__':
    print(f'Probes for {VERSION}...')
    test_all()
    op = os.path.join(OUTDIR, f'probe_results_{VERSION}.json')
    with open(op,'w') as f: json.dump({'version':VERSION,'total':len(results),'results':results},f,indent=2)
    print(f'  {len(results)} results -> {op}')

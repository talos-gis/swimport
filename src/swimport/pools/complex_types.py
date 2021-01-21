from itertools import chain, product
import os
from typing import Dict

from swimport.pools.pools import pools, syspools, IdiomaticPool


@syspools.add(IdiomaticPool)
def np_main(numpy_dir, *, swim):
    swim.add_begin('#define SWIG_FILE_WITH_INIT')
    path = os.path.join(numpy_dir, "numpy.i")
    swim.add_raw(f'%include "{path}"')
    swim.add_init('import_array();')


@syspools.add(IdiomaticPool)
def np_char(*, swim):
    # the NPY_CHAR value is officially deprecated, but currently, numpy.i only makes use of the
    # PyArray_SimpleNew/FromData functions, instead of the PyArray_New function, making it impossible to use flexible
    # types (string, unicode)
    swim.add_raw('%numpy_typemaps(char, NPY_CHAR, size_t)')
    swim.add_raw('%numpy_typemaps(char, NPY_CHAR, int)')


@syspools.add(IdiomaticPool)
def np_applies(dim, additional=(), const_input=True, ref_out=True, typedefs = (), *, swim):
    typedefs = dict(typedefs)
    def dim_params(pref):
        return (pref + ' DIM' + str(i) for i in range(1, dim + 1))

    for data_type in chain(
            (u + t for u, t in product(('unsigned ', ''), ('int', 'long', 'long long', 'short',))),
            ('float', 'double', 'signed char', 'unsigned char'),
            additional):
        alias = None
        if data_type in typedefs:
            alias = typedefs[data_type]
        for dim_type in ('int', 'size_t'):
            if const_input:
                dp = ", ".join(dim_params(dim_type))
                if alias:
                    swim.add_raw(
                        f'%apply ({alias} * IN_ARRAY{dim}, {dp}) '
                        f'{{ ({data_type} * IN_ARRAY{dim}, {dp}) }};'
                    )
                swim.add_raw(
                    f'%apply ({data_type} * IN_ARRAY{dim}, {dp}) '
                    f'{{ ({data_type} const * IN_ARRAY{dim}, {dp}) }};'
                )
                if dim == 1:
                    if alias:
                        swim.add_raw(
                            f'%apply ({alias} * INPLACE_ARRAY_FLAT, {dim_type} DIM_FLAT) '
                            f'{{ ({data_type} * INPLACE_ARRAY_FLAT, {dim_type} DIM_FLAT) }};'
                        )
                    swim.add_raw(
                        f'%apply ({data_type} * INPLACE_ARRAY_FLAT, {dim_type} DIM_FLAT) '
                        f'{{ ({data_type} const * INPLACE_ARRAY_FLAT, {dim_type} DIM_FLAT) }};'
                    )

            if ref_out:
                for out_id in (f'ARGOUTVIEW_ARRAY{dim}', f'ARGOUTVIEWM_ARRAY{dim}'):
                    dp = list(dim_params(''))
                    applies = []
                    main_qdp = None
                    for quals in product('*&', repeat=len(dp)):
                        qdp = ', '.join(dim_type + q + d for (q, d) in zip(quals, dp))
                        if not main_qdp:
                            main_qdp = qdp
                        applies.extend((
                            f'({data_type}*& {out_id}, {qdp})',
                            f'({data_type}** {out_id}, {qdp})',
                        ))
                    applies = ', '.join(applies)
                    if alias:
                        swim.add_raw(
                            f'%apply ({alias}** {out_id}, {main_qdp}) {{({data_type}** {out_id}, {main_qdp})}};'
                        )
                    swim.add_raw(
                        f'%apply ({data_type}** {out_id}, {main_qdp}) {{'
                        + applies +
                        '};'
                    )


@pools.add(IdiomaticPool)
def numpy_arrays(numpy_dir='', additionals=(), typedefs = (), allow_char_arrays=False,
                 const_input=True, ref_out=True, max_dim=1, *,
                 swim):
    """
    adds the inserts for np arrays to used (if you also use the stdint pool, remember to also use the npstdint pool)
    :param numpy_dir: the search path for the numpy.i file
    :param additionals: additional dtypes to support.
    :param allow_char_arrays: whether to include typemaps for char arrays.
    :param const_input: whether to allow const pointers  as arrays (for input only)
    :param ref_out: whether to allow ref (&) pointers as arrays (for output only).
    :param max_dim: the maximum number of numpy dimensions to map for.
    """
    typedefs = dict(typedefs) if typedefs else {}
    if max_dim < 1 or max_dim > 4:
        raise ValueError('maxdim must be between 1 and 4 (inclusive)')

    np_main(numpy_dir, swim)
    additionals = list(additionals)
    if allow_char_arrays:
        np_char(swim=swim)
        additionals.append('char')
    if typedefs:
        additionals.extend(typedefs.keys())

    additionals = tuple(additionals)

    for dim in range(1, max_dim + 1):
        swim(np_applies(dim=dim, const_input=const_input, ref_out=ref_out, additional=additionals, typedefs=tuple(typedefs.items())))

    from swimport.functionswim import ParameterNameTrigger, ParameterTypeTrigger, ApplyBehaviour, FunctionBehaviour

    param_rules = (
        (ParameterNameTrigger('A_.*') & ParameterTypeTrigger.const_ptr) >> ApplyBehaviour('IN_ARRAY1', 'DIM1'),
        (ParameterNameTrigger('A_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour('ARGOUTVIEW_ARRAY1',
                                                                                              'DIM1'),
        (ParameterNameTrigger('AF_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour('ARGOUTVIEWM_ARRAY1',
                                                                                               'DIM1'),
        ParameterNameTrigger('AIO_.*') >> ApplyBehaviour('INPLACE_ARRAY_FLAT', 'DIM_FLAT'),
    )
    # the rules are in reverse order since extendleft reverses the iterable

    # note: in theory, default_parameters_rules should only be changed by the user as a convenience.
    # But we don't expect many collisions on the prefix.
    FunctionBehaviour.default_parameters_rules.extendleft(param_rules)

    for i in range(1, max_dim + 1):
        dim_names = [f'DIM{j}' for j in range(1, i + 1)]
        param_rules = (
            (ParameterNameTrigger(f'A{i}_.*') & ParameterTypeTrigger.const_ptr) >> ApplyBehaviour(
                f'IN_ARRAY{i}', *dim_names),
            (ParameterNameTrigger(f'A{i}_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour(
                f'ARGOUTVIEW_ARRAY{i}', *dim_names),
            (ParameterNameTrigger(f'AF{i}_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour(
                f'ARGOUTVIEWM_ARRAY{i}', *dim_names),
        )
        FunctionBehaviour.default_parameters_rules.extendleft(param_rules)


# todo keep? test? do something?
@pools.add(IdiomaticPool)
def numpy_stdint(swim):
    """
    numpy typemaps for stdint types
    """
    swim.add_raw('''
    %numpy_typemaps(int8_t, NPY_BYTE, int)
    %numpy_typemaps(uint8_t, NPY_UBYTE, int)
    %numpy_typemaps(int16_t, NPY_SHORT, int)
    %numpy_typemaps(uint16_t, NPY_USHORT, int)
    %numpy_typemaps(int32_t, NPY_INT, int)
    %numpy_typemaps(uint32_t, NPY_UINT, int)
    %numpy_typemaps(int64_t, NPY_LONG, int)
    %numpy_typemaps(uint64_t, NPY_ULONG, int)
    %numpy_typemaps(int64_t, NPY_LONGLONG , int)
    %numpy_typemaps(uint64_t, NPY_ULONGLONG, int)
    ''')
    swim.add_nl()
    swim.add_raw('''
    %numpy_typemaps(int8_t, NPY_BYTE, size_t)
    %numpy_typemaps(uint8_t, NPY_UBYTE, size_t)
    %numpy_typemaps(int16_t, NPY_SHORT, size_t)
    %numpy_typemaps(uint16_t, NPY_USHORT, size_t)
    %numpy_typemaps(int32_t, NPY_INT, size_t)
    %numpy_typemaps(uint32_t, NPY_UINT, size_t)
    %numpy_typemaps(int64_t, NPY_LONG, size_t)
    %numpy_typemaps(uint64_t, NPY_ULONG, size_t)
    %numpy_typemaps(int64_t, NPY_LONGLONG , size_t)
    %numpy_typemaps(uint64_t, NPY_ULONGLONG, size_t)
    ''')
    swim.add_nl()


@pools.add(IdiomaticPool)
def buffer(output=bytearray, *, swim):
    """
    adds the necessary typemaps to use bytes objects
    :param output: the type of the python object to output when using bytes
    """
    swim.add_raw("""
    %typemap(in, numinputs=1) (unsigned char const* BUFFER_INPUT, size_t DIM1) (Py_buffer buffer)
    {
        buffer.buf = nullptr;
        auto _buffer = &buffer;
        if (PyObject_GetBuffer($input, _buffer, PyBUF_CONTIG_RO) < 0) SWIG_fail;
        if (_buffer->itemsize != sizeof(unsigned char)){
            PyErr_SetString(PyExc_BufferError, "buffer is of the wrong type in argument: $1_name");
            SWIG_fail;
        }
        $1 = (unsigned char*) _buffer->buf;
        $2 = (size_t) _buffer->len;
    }
    %typemap(freearg, match="in") (unsigned char const* BUFFER_INPUT, size_t DIM1)
    {
        if ((buffer$argnum).buf)
            PyBuffer_Release(&buffer$argnum);
    }
    %typemap(typecheck) (unsigned char const* BUFFER_INPUT, size_t DIM1){
        $1 = PyObject_CheckBuffer($input);
    }
    """)
    if output in (bytearray, bytes):
        out_func = {bytearray: 'PyByteArray_FromStringAndSize', bytes: 'PyBytes_FromStringAndSize'}[output]
        swim.add_raw(f"""
            %typemap(in, numinputs=0) (unsigned char** BUFFER_OUTPUT, size_t* DIM1) (unsigned char* resbuffer, size_t reslen)
            {{
                $1 = &resbuffer;
                $2 = &reslen;
            }}
            %typemap(argout) (unsigned char** BUFFER_OUTPUT, size_t* DIM1)
            {{
                $result = SWIG_Python_AppendOutput($result,{out_func}(*(const char**)$1, *$2));
            }}
            %apply (unsigned char** BUFFER_OUTPUT, size_t* DIM1)
            {{
                (unsigned char*& BUFFER_OUTPUT, size_t& DIM1),
                (unsigned char** BUFFER_OUTPUT, size_t& DIM1),
                (unsigned char*& BUFFER_OUTPUT, size_t* DIM1)
            }};
        
            %typemap(in, numinputs=0) (unsigned char** OUTPUT_FREE, size_t* DIM1) (unsigned char* resbuffer, size_t reslen)
            {{
                $1 = &resbuffer;
                $2 = &reslen;
            }}
            %typemap(argout) (unsigned char** OUTPUT_FREE, size_t* DIM1)
            {{
                $result = SWIG_Python_AppendOutput($result,{out_func}(*(const char**)$1, *$2));
                if ($1 && (*$1))
                    delete[] *$1;
            }}
            %apply (unsigned char** OUTPUT_FREE, size_t* DIM1)
            {{
                (unsigned char*& OUTPUT_FREE, size_t& DIM1),
                (unsigned char** OUTPUT_FREE, size_t& DIM1),
                (unsigned char*& OUTPUT_FREE, size_t* DIM1)
            }};
            """)
    elif output is memoryview:
        # todo test?
        swim.add_raw(f"""
            %typemap(in, numinputs=0) (unsigned char** BUFFER_OUTPUT, size_t* DIM1)(unsigned char* resbuffer, size_t reslen)
            {{
                $1 = &resbuffer;
                $2 = &reslen;
            }}
            %typemap(argout) (unsigned char** BUFFER_OUTPUT, size_t* DIM1)
            {{
                $result = SWIG_Python_AppendOutput($result,PyMemoryView_FromMemory(*(const char**)$1, *$2, PyBUF_WRITE));
            }}
            %apply (unsigned char** BUFFER_OUTPUT, size_t* DIM1)
            {{
                (unsigned char*& BUFFER_OUTPUT, size_t& DIM1),
                (unsigned char** BUFFER_OUTPUT, size_t& DIM1),
                (unsigned char*& BUFFER_OUTPUT, size_t* DIM1)
            }};

            %typemap(in, numinputs=0) (unsigned char** OUTPUT_FREE, size_t* DIM1) (unsigned char* resbuffer, size_t reslen)
            {{
                #error OUTPUT_FREE cannot be used with the memoryview
            }}
            """)
    elif not output:
        pass
    else:
        raise TypeError('could not recognize output')

    from swimport.functionswim import ParameterNameTrigger, ParameterTypeTrigger, ApplyBehaviour, FunctionBehaviour

    param_rules = (
        (ParameterNameTrigger('B_.*') & ParameterTypeTrigger.const_ptr) >> ApplyBehaviour('BUFFER_INPUT', 'DIM1'),
        (ParameterNameTrigger('B_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour('BUFFER_OUTPUT', 'DIM1'),
        (ParameterNameTrigger('BF_.*') & ParameterTypeTrigger.not_const_ptr) >> ApplyBehaviour('OUTPUT_FREE', 'DIM1')
    )
    # the rules are in reverse order since extendleft reverses the iterable

    # note: in theory, default_parameters_rules should only be changed by the user as a convenience.
    # But we don't expect many collisions on the prefix.
    FunctionBehaviour.default_parameters_rules.extendleft(param_rules)

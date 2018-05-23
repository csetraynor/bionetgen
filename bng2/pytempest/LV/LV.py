# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.11
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_LV', [dirname(__file__)])
        except ImportError:
            import _LV
            return _LV
        if fp is not None:
            try:
                _mod = imp.load_module('_LV', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _LV = swig_import_helper()
    del swig_import_helper
else:
    import _LV
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


class intp(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, intp, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, intp, name)
    __repr__ = _swig_repr
    def __init__(self): 
        this = _LV.new_intp()
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _LV.delete_intp
    __del__ = lambda self : None;
    def assign(self, *args): return _LV.intp_assign(self, *args)
    def value(self): return _LV.intp_value(self)
    def cast(self): return _LV.intp_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _LV.intp_frompointer
    if _newclass:frompointer = staticmethod(_LV.intp_frompointer)
intp_swigregister = _LV.intp_swigregister
intp_swigregister(intp)

def intp_frompointer(*args):
  return _LV.intp_frompointer(*args)
intp_frompointer = _LV.intp_frompointer


def new_intp1():
  return _LV.new_intp1()
new_intp1 = _LV.new_intp1

def copy_intp1(*args):
  return _LV.copy_intp1(*args)
copy_intp1 = _LV.copy_intp1

def delete_intp1(*args):
  return _LV.delete_intp1(*args)
delete_intp1 = _LV.delete_intp1

def intp1_assign(*args):
  return _LV.intp1_assign(*args)
intp1_assign = _LV.intp1_assign

def intp1_value(*args):
  return _LV.intp1_value(*args)
intp1_value = _LV.intp1_value

def int_to_uint(*args):
  return _LV.int_to_uint(*args)
int_to_uint = _LV.int_to_uint

def new_doubleArray(*args):
  return _LV.new_doubleArray(*args)
new_doubleArray = _LV.new_doubleArray

def delete_doubleArray(*args):
  return _LV.delete_doubleArray(*args)
delete_doubleArray = _LV.delete_doubleArray

def doubleArray_getitem(*args):
  return _LV.doubleArray_getitem(*args)
doubleArray_getitem = _LV.doubleArray_getitem

def doubleArray_setitem(*args):
  return _LV.doubleArray_setitem(*args)
doubleArray_setitem = _LV.doubleArray_setitem
class doubleArrayClass(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, doubleArrayClass, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, doubleArrayClass, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _LV.new_doubleArrayClass(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _LV.delete_doubleArrayClass
    __del__ = lambda self : None;
    def __getitem__(self, *args): return _LV.doubleArrayClass___getitem__(self, *args)
    def __setitem__(self, *args): return _LV.doubleArrayClass___setitem__(self, *args)
    def cast(self): return _LV.doubleArrayClass_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _LV.doubleArrayClass_frompointer
    if _newclass:frompointer = staticmethod(_LV.doubleArrayClass_frompointer)
doubleArrayClass_swigregister = _LV.doubleArrayClass_swigregister
doubleArrayClass_swigregister(doubleArrayClass)

def doubleArrayClass_frompointer(*args):
  return _LV.doubleArrayClass_frompointer(*args)
doubleArrayClass_frompointer = _LV.doubleArrayClass_frompointer

__N_PARAMETERS__ = _LV.__N_PARAMETERS__
__N_EXPRESSIONS__ = _LV.__N_EXPRESSIONS__
__N_OBSERVABLES__ = _LV.__N_OBSERVABLES__
__N_RATELAWS__ = _LV.__N_RATELAWS__
__N_SPECIES__ = _LV.__N_SPECIES__

def check_flag(*args):
  return _LV.check_flag(*args)
check_flag = _LV.check_flag

def calc_expressions(*args):
  return _LV.calc_expressions(*args)
calc_expressions = _LV.calc_expressions

def calc_observables(*args):
  return _LV.calc_observables(*args)
calc_observables = _LV.calc_observables

def calc_ratelaws(*args):
  return _LV.calc_ratelaws(*args)
calc_ratelaws = _LV.calc_ratelaws

def calc_species_deriv(*args):
  return _LV.calc_species_deriv(*args)
calc_species_deriv = _LV.calc_species_deriv

def initialize_species(*args):
  return _LV.initialize_species(*args)
initialize_species = _LV.initialize_species

def integrate(*args):
  return _LV.integrate(*args)
integrate = _LV.integrate

def bng_protocol(*args):
  return _LV.bng_protocol(*args)
bng_protocol = _LV.bng_protocol
# This file is compatible with both classic and new-style classes.


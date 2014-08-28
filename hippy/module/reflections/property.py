from hippy import consts
from hippy.klass import def_class
from hippy.objects.base import W_Root
from hippy.objects.intobject import W_IntObject
from hippy.objects.instanceobject import W_InstanceObject
from hippy.builtin import wrap_method, ThisUnwrapper, Optional
from hippy.builtin_klass import GetterSetterWrapper
from hippy.error import PHPException
from hippy.module.reflections.exception import k_ReflectionException


IS_STATIC = 1
IS_PUBLIC = 256
IS_PROTECTED = 512
IS_PRIVATE = 1024


class W_ReflectionProperty(W_InstanceObject):
    class_name = ''
    name = ''
    def get_str(self):
        prop = self.ref_prop
        if prop is None:
            inner = '<dynamic> public $%s' % self.name
        else:
            access = ''
            if not prop.is_static():
                access += '<default> '
            if prop.is_public():
                access += 'public'
            elif prop.is_protected():
                access += 'protected'
            elif prop.is_private():
                access += 'private'
            else:
                assert False, 'should not happen'
            if prop.is_static():
                access += ' static'
            inner = '%s $%s' % (access, prop.name)
        return 'Property [ %s ]\n' % inner


@wrap_method(['interp', W_Root, str, Optional(bool)],
             name='ReflectionProperty::export', flags=consts.ACC_STATIC)
def export(interp, w_klass, name, return_string=False):
    refl = k_ReflectionProperty.call_args(interp,
            [w_klass, interp.space.wrap(name)])
    result = refl.get_str()
    if return_string:
        return interp.space.wrap(result)
    else:
        interp.writestr(result)
        interp.writestr('\n')
        return interp.space.w_Null


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty), W_Root, str],
             name='ReflectionProperty::__construct')
def construct(interp, this, w_class, property_name):
    space = interp.space
    if space.is_str(w_class):
        class_name = space.str_w(w_class)
        klass = interp.lookup_class_or_intf(class_name)
        if klass is None:
            msg = "Class %s does not exist" % class_name
            raise PHPException(k_ReflectionException.call_args(
                interp, [space.wrap(msg)]))
    elif isinstance(w_class, W_InstanceObject):
        klass = w_class.klass
        class_name = klass.name
    else:
        msg = ("The parameter class is expected to be either a string "
               "or an object")
        raise PHPException(k_ReflectionException.call_args(
            interp, [space.wrap(msg)]))

    this.class_name = class_name
    this.name = property_name
    this.ref_klass = klass
    this.flags = 0
    try:
        this.ref_prop = klass.properties[property_name]
        if this.ref_prop.is_static():
            this.flags |= IS_STATIC
        if this.ref_prop.is_public():
            this.flags |= IS_PUBLIC
        elif this.ref_prop.is_private():
            this.flags |= IS_PRIVATE
        elif this.ref_prop.is_protected():
            this.flags |= IS_PROTECTED
    except KeyError:
        if (isinstance(w_class, W_InstanceObject) and
                w_class.map.lookup(property_name) is not None):
            this.ref_prop = None
            this.flags = consts.ACC_IMPLICIT_PUBLIC
            return
        msg = "Property %s::$%s does not exist" % (class_name, property_name)
        raise PHPException(k_ReflectionException.call_args(
            interp, [interp.space.wrap(msg)]))


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::getName')
def get_name(interp, this):
    return _get_name(interp, this)


# XXX: getValue & setValue don't work in case of accessible private & protected
# properties
@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty),
              Optional(W_Root)],
             name='ReflectionProperty::getValue')
def get_value(interp, this, w_obj=None):
    property = this.ref_prop
    if property is None:
        return w_obj.getattr(interp, this.name, w_obj.getclass(), give_notice=False)

    if not property.is_public():
        msg = "Cannot access non-public member %s::%s" % (this.class_name,
                                                          this.name)
        raise PHPException(k_ReflectionException.call_args(
            interp, [interp.space.wrap(msg)]))

    if not property.is_static():
        w_value = w_obj.getattr(interp, this.name, w_obj.getclass(), give_notice=False)
    else:
        w_value = property.getvalue(interp.space).deref()
    return w_value


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty),
              W_Root, Optional(W_Root)],
             name='ReflectionProperty::setValue')
def set_value(interp, this, w_arg_1, w_arg_2=None):

    if not this.ref_prop.is_public():
        msg = "Cannot access non-public member %s::%s" % (this.class_name,
                                                          this.name)
        raise PHPException(k_ReflectionException.call_args(
            interp, [interp.space.wrap(msg)]))

    if not this.ref_prop.is_static():
        w_obj = w_arg_1
        w_value = w_arg_2
        w_obj.setattr(interp, this.name, w_value, None)
    else:
        if w_arg_2 is None:
            w_value = w_arg_1
        else:
            w_value = w_arg_2
        this.ref_prop.r_value.store(w_value)


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::getDeclaringClass')
def get_declaring_class(interp, this):
    name = this.ref_prop.klass.name
    k_ReflClass = interp.lookup_class_or_intf('ReflectionClass')
    return k_ReflClass.call_args(interp, [interp.space.newstr(name)])


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::isPublic')
def is_public(interp, this):
    return interp.space.newbool(this.ref_prop.is_public())


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::isPrivate')
def is_private(interp, this):
    return interp.space.newbool(this.ref_prop.is_private())


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::isProtected')
def is_protected(interp, this):
    return interp.space.newbool(this.ref_prop.is_protected())


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::isStatic')
def is_static(interp, this):
    return interp.space.newbool(this.ref_prop.is_static())


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::isDefault')
def is_default(interp, this):
    return interp.space.newbool(True)  # XXX


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::getModifiers')
def get_modifiers(interp, this):
    return interp.space.newint(this.ref_prop.access_flags)


@wrap_method(['interp', ThisUnwrapper(W_ReflectionProperty)],
             name='ReflectionProperty::__toString')
def toString(interp, this):
    return interp.space.newstr(this.get_str())


def _get_class(interp, this):
    return interp.space.newstr(this.class_name)


def _set_class(interp, this, w_value):
    pass


def _get_name(interp, this):
    return interp.space.newstr(this.name)


def _set_name(interp, this, w_value):
    pass


k_ReflectionProperty = def_class(
    'ReflectionProperty',
    [export,
     construct,
     get_name,
     get_value,
     set_value,
     get_declaring_class,
     is_public,
     is_private,
     is_protected,
     is_static,
     is_default,
     get_modifiers,
     toString],
    [GetterSetterWrapper(_get_name, _set_name, 'name', consts.ACC_PUBLIC),
     GetterSetterWrapper(_get_class, _set_class, 'class', consts.ACC_PUBLIC)],
    [('IS_STATIC', W_IntObject(IS_STATIC)),
     ('IS_PUBLIC', W_IntObject(IS_PUBLIC)),
     ('IS_PROTECTED', W_IntObject(IS_PROTECTED)),
     ('IS_PRIVATE', W_IntObject(IS_PRIVATE))],
    instance_class=W_ReflectionProperty
)

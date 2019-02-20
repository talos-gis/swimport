# Swimport
## About
Swimport is a python library to simplify automate the meandering and error-prone parts of making a [SWIG](http://www.swig.org/) interface file for python. 

**Swimport is an advanced tool, users are expected to have above-basic knowledge in both python and C++. As well as having read chapters 1, 2, 5-13, and 34 of [SWIG's documentation](http://www.swig.org/Doc3.0/)**

**At present time, swimport is not, and is not designed to be, an 'automagical' .h to .i converter. Most usages will require additional user configuration to the output files. Users are advised to merely import the output file into a user-written file that includes the parts swimport can't/ isn't designed to handle.**

## Installation and requirements
Swimport requires the [CppHeaderParser module](https://pypi.org/project/CppHeaderParser/). Other than that, install like any other python library (Swimport is pure-python).

Tests and examples might have some additional requirements.
## Usage
### Abstract
* The library reads C++ header files (.h) and creates a SWIG interface file (.i) that, when built with SWIG, using the source files and (optionally) the header files, will compile into a python module utilising the C++ code. 

### Structure
* At first, Source objects are created from header file (.h) paths, they handle the reading and parsing of C++ objects in the source files.
* Then, SwimRules are made to handle the imports of C++ objects. A SwimRule is composed of two distinct objects:
    * A Trigger, that decides whether a C++ objects will be imported by the rule.
    * A Behaviour, that handles the valid C++ objects and wraps them in a Swimporting object.
    * Each C++ object kind (variable, method, ect., see below) has its own types for both Trigger and Behaviour, although custom classes can be used (see below).
* The SwimRule processes a source file, checking which of its cpp objects pass the trigger, and returns Swimporting objects for those objects.
* Swimporting objects are functions specialised for a particular C++ object and importing behaviour. 
* Usage of swimport revolves around the Swim object. The Swim receives the Swimporting objects and adds lines to itself.
* Finally, the Swim object writes its lines to the output file.

### Object Kinds
#### Methods
Importing methods requires special rules for how to handle parameters. These behave in a similar way, each with a trigger and behaviour. Common default behaviours and rules are built-in to the library (and are the default method behaviour, see below).

#### Containers
A container is a collective term for structs, classes, and unions. There are two ways to import containers.
##### Trigger-Behaviour
Containers support a rudimentary trigger-behaviour protocol. Note that this protocol should only be used for simple c structs. Without any constructors, methods, or any private or static members.
##### ContainerSwim
The ContainerSwim object acts a pseudo-Swim object by itself, handling methods, static members, and extension methods (both on c++ and python side). See examples 37-43 for usage examples.

#### Enums
Enums can be imported using SwimRules as normal. Note that enum values are treated as global variables in python.
##### Python enum Behaviour
A special behaviour exists to wrap the c++ enum with a python enum class. Making it usable like a python enum.

#### Variables and Constants
Variables can be imported using SwimRules as normal. Constants declared with #define are not supported. NOTE: sharing a mutable value as a variable between C and python is tricky. See the official SWIG docs for an explanation but in general: all the C variables that are subject ot change during runtime MUST be accessed through the special cvar object in the library.
##### GetSet Behaviour
To avoid the above quirk, a specialized behaviour for variables exists that instead generates getter and setter methods for the C variable. 

#### Typedefs
Typedefs can be imported using SwimRules as normal. In cases where inter-dependant typedefs from multiple source need to be imported, a TypeDefAggregate object can used to aggregate the typedefs and sort them appropriately.

#### Types
A type is a virtual C++ object. A type can be used to convert complex C++ types to Python objects. Swimporting objects for types must be created directly.
##### Typemaps
Using types requires writing SWIG typemaps. The most common way to do this is to enter the body of a cpp function, letting Swimport automatically wrap a function around it, and call it in the typemap. There are other ways to create a typemap, most notably an BuiltinTypemap.

#### Pools
Pools are specialized code snippets that can be added manually to the output code. Some pools are used without arguments, while others are. See `swimport.pools.__doc__` for info on all pools.

#### Direct Inserts
Users can also insert .i code immediately to the output file using the Swim's `add_*` methods.
### Additional Features
#### Repeat Import Blocking
Swim object keep a record of all the object they've accepted Swimportings for, and refuse to swimport the same object twice. This means that when applying rules, users can apply the most narrow rules first, and apply the broader rules without concern for duplicates or excluding already imported objects.  
#### Python Code Templates
SWIG features scopes that allow direct injection of python code to the output file. As useful as these injections are, they are rather limited, not providing macros like the function name and return values. For this reason, python code used as `MethodBehaviour` parameters (like `prepend_python` and `append_python`) are used as templates, with macros of the form `$...` and `${...}`. The replacements occur under the following rules:
* special rule `$$` is an escape for the `$` char.
* macros of the form `$<identifier>` evaluate to a pre-set value:
    * `$retvar`: the variable containing the function output.
* macros of the form `${identifier}` evaluate as python code with the variable `method` as the method being imported.
* all other usages of the `$` character are invalid
```
behaviour = Method.Behaviour(prepend_python='print("entered ${method.name}")',
                             append_python='print("exiting ${method.name}, result: $retval")')
```

#### Custom Behaviours and Triggers
Users can create their Behaviour and Trigger classes, see examples below. When doing this, it is important to subclass `swimport.Trigger`, `swimport.Behaviour` or their specialisations.
```
from swimport import Method

class VoidTrigger(Method.Trigger):  # a trigger class that only matches methods that return void
    def is_valid(self, rule, obj: Method):
        return super().is_valid(rule, obj)\
            and obj.return_type == 'void'  # todo account for dll names
```

#### Rule Assertion
When applying a collection of swimportings (like a method rule result), it returns an int indicating how many swimportings were accepted. These can be used to assert the imported objects:
```
assert swim(method_rule_foo(src)) == 1  # assert that only one object was imported
assert 'foo' in swim(method_rule_foo(src))  # assert that an object of name 'foo' was imported
assert 'foo' in swim(method_rule_foo(src)) == 1  # assert that only an object of name 'foo' was imported
```

Important to mention that **if the script is run with the (little-used) -O flag, the assert, alongside its contents, will be ignored.** To combat this, usage of third-party libraries like [ensure](https://pypi.org/project/ensure/) are recommended.
#### Default parameters rules
Swimport uses the following rules by default to classify method parameters. These can be changed by changing an individual `MethodBehaviour`'s `parameter_rules` or the default with `MethodBehaviour.default_parameter_rules` the following group rules are considered in order:

|prefix|type|action|
|------|----|------|
|AIO_|ANY|an inplace numpy array of any rank [^1][^3]|
|A_|any non-const pointer or reference|a 1D numpy output array [^1][^3]|
|A_|any const pointer or reference|a 1D numpy input array [^1][^3]|
|BF_|non-const pointer or reference|an output byte array that needs to be freed [^1][^3]|
|B_|non-const pointer or reference|an output byte array [^1][^3]|
|B_|const pointer or reference|an input buffer [^1][^3]|
|SF_|non-const char pointer pointer or reference [^2]|an output C string that needs to be freed [^3]|
|ANY|const char pointer [^2]|a C string|
|IO_|ANY|a parameter that act as both input and output [^4]|
|ANY|any non-const pointer or reference|an output parameter [^4]|
|ANY|any const pointer or reference|an input parameter [^4]|
|ANY|ANY|no action is taken|

[^1]: arrays and buffers also consume the next parameter as input.
[^2]: wherever char is used, wchar_t is accepted as well. (see quirk below).
[^3]: requires special pool
[^4]: requires the type to be imported to swimport, see below

#### Importing Types to Swimport
Advanced swimport features (like input and output parameters, but also the ones listed below), requires that swimport will know the type involved, including standard conversion functions and other info. This is called swimporting, and there are multiple ways to do it for different types:
##### TypeSwimporting
This is the canonical, most basic method of importing a type (almost all other importing methods wrap a TypeSwimporting).
##### Container, Enumeration, and Typedef Behaviours
Most common Behaviours automatically import both the container type, and its pointer type. Note that some behaviours like typedefs and basic enums only import the type if the original type was imported.
##### Pools
For most commonly used types, there are pools to import it with very little effort.
###### Primitives
The `pools.primitive` map imports all primitive types (including `bool`, `size_t`, and `wchar_t`).
###### void*
`pools.void_ptr` imports void*.
###### c string
`pools.c_string` imports C strings (null-terminated char and wchar_t pointers). This also allows specifying a C string that needs to be freed by the caller with the SF\_ prefix. Note that non-const pointers cannot be accepted as input to c++ functions.
###### std::string
`pools.std_string` imports both `std::string` and `std::wstring`.
###### PyObject*
`pools.pyObject` imports raw PyObject* objects.
###### bool
`pools.bool` imports bool types, allowing them to accept any python object, converting it to its truthfulness value. Note that if this and the `primitive` pools are used in conjunction, bool must be excluded from the primitive imports with `pools.primitive(blacklist='bool')`.
###### None, Ellipsis, and NotImplemented
`pools.singletons` imports the special c++ types `ellipsis`, `NoneType`, `NotImplemented`, and `PySingleton` defined in py_singletons.h.
###### slices
`pools.slice` imports the `slice<...>` structs defined in py_slice.h.
###### complex
`pools.complex` imports the `std::complex<double>` type.
###### tuple
`pools.tuple` imports the `std::tuple<...>` type. It requires that all its sub-types be properly imported.
###### input iterable
`pools.input_iterable` imports a special template `py_iterable<T>` defined in `py_iterable.h`. Accepting this type as an argument allows the function to iterate over a python object. The inner type must be imported. This pool is automatically applied to all imported types (unless explicitly disabled).
###### iterables
`pools.iter` imports an iterable type. See its documentation for details. This pool is automatically applied to all imported types (unless explicitly disabled). There are also specialisations of this pool named `pools.list`, `pools.set`, `pools.frozenset`, and `pools.array` (that also requires an array length), for issuing the default output type. 
###### map
`pools.map` imports a mapping type (`std::unordered_map` by default). See its documentation for details.
###### callable
`pools.callable` imports the `std::function<...>` type for input to c++. It requires that all its sub-types be properly imported.

Note: Some imported types (most notably wide C strings) have special functions that must be called after they are converted from a python object to a C++ object (programmatically called `to_cpp_post`). Since the `std::function` caller does not know this, using these types will result in undisposed resources. By default, usage of such types as `pools.callable` return types will raise an error. 
###### buffers
`pools.buffer` imports buffer types of the parameter signature `unsigned char *, size_t`. Note that buffer parameter names must either begin with a "B\_" or "BF\_"
###### numpy arrays
`pools.numpy_arrays` imports numpy array types of the parameter signature `T *, size_t` where T is a primitive type. Note that nparray parameter names must either begin with a "A\_", "AIO\_", or "AF\_" (to indicate that an array is newly allocated and should be freed by the numpy array).

#### Rule construction syntax
Triggers can be joined into a rule with the >> operator
```
from swimport import MethodBehaviour, MethodNameTrigger, TriggerBehaviourSwimRule

trigger = MethodNameTrigger('foo')
behaviour = MethodBehaviour()

assert (trigger >> behaviour) == TriggerBehaviourSwimRule(trigger, behaviour)
```

#### Default Triggers and Behaviors
Many C++ types also have default behaviours and triggers to make rule construction easier. In most cases, the default trigger accepts only objects whose names fully match the pattern input
```
from swimport import MethodBehaviour, MethodNameTrigger, Method

assert MethodNameTrigger('foo') == Method.Trigger('foo')
assert MethodBehaviour() == Method.Behaviour()
```

The default triggers can even be automatically constructed from arguments
```
from swimport import Method

behaviour = Method.Behaviour()
assert ('foo' >> behaviour) == (Method.Triggers('foo') >> behaviour)
```

Using `...`, a trigger is constructed that accepts every object that the behaviour can handle.
```
rule = ... >> behaviour
```

Note that behaviours can be used in the exact same way by themselves. (behaviours are rules that accept any object of the appropriate category). Using the `... >> behaviour` syntax is useful to give rules specific names for the output file.
```
rule = (... >> behaviour).replace(name="my special rule")
```
#### Compound Triggers
Triggers can be used in binary logical operators: `| & ^` to create a trigger that accepts objects if the individual triggers accept the objects appropriately (example: `(a|b).is_valid(...) == a.is_valid(...) or b.is_valid(...)`)

Similarly, triggers can be inverted to create a negation (`(~a).is_valid(...) == not a.is_valid(...)`).

Triggers can also be compounded into a not-implies relation (`(a > b) == a & (~b)`).
### Examples
Many usage examples can be found in the `tests\examples` directory. examples are usually comprised of:
* `main.py`: A file that calls the swimport library and builds the .i file
* `src.cpp`/`src.h`: cpp source files to be processed, compiled, and linked
* `usage.py`: a file showing usage of the resulting cpp/python library

Note that some examples might require additional libraries to run.

## Known Issues/Quirks
* When importing dll, the function name must not be mangled (extern "C" must be used)
  * When using extern "C", it must be scoped. 
* There is a bug in CppHeaderParser where it will crash if the header file ends in a singleline comment
* A quirk in SWIG to python conversion is that functions that return void return None in python. and that functions with output parameters are merely appended to the original output. meaning that a function with a pointer as a return and an output parameter will ignore the return value if it is null. This behaviour is consistent with standard SWIG. The solution is to simply ensure that if a function returns a pointer and has output parameters, ensure that the return value is never null.
* A bug in both SWIG and CppHeaderParser prevents enums from being non-int
* When entering strings, note that SWIG accepts strings with the null char `\0` inside them, these will be converted wholesale, but might be mistaken for the string terminator in most C code.
* CppHeaderParser cannot parse using alias commands: `using alias = oldname;` 

    ### Arrays
    Yes, arrays have so many notes that they deserve their own section
    * functions that accept arrays cast aggressively to the type they require, including downcasting and truncating. So that a C function that expects an array of ints will accept a list of python floats, truncating each value individually. See example 14 to see this in action.
    * arrays of type char are not enabled by default, although they can be used with an optional argument to the numpy_arrays pool. Although note, that the dtype of arrays accepted is "S1", not "U1", as is default for char arrays made in np. use 'signed char' or 'unsigned char' for byte arrays. see example 15 to see this in action. 
    * When an array is used as an output variable with the AF\_ prefix, it takes ownership of the variable, meaning it will be freed when the array is deleted. As a direct consequence of this, **the pointer of the array must be one that has been specifically allocated and unique, as the array takes ownership of it.** This means, among other things, that you cannot use `std::vector::data` as the pointer.
    ### Containers
    * Due to the way python handles descriptors, it is impossible to easily create class properties. Meaning that mutable static class members must be accessed through swig's `cvar` attribute, as a property of an arbitrary member of the class, or using getset methods.
    * Due to a bug in CppHeaderParser, all member and inheritance, even in structs, must be access-qualified.
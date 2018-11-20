# -*- coding: utf-8 -*-

'''
Provide mock functions for testing.
'''

__author__ = "Hans Ekkehard Plesser"
__email__ = "hans.ekkehard.plesser@nmbu.no"


class MockFunction(object):
    """
    Base class for mock function classes.

    Handles call count and argument recording.
    """

    def __init__(self):

        self._call_count = 0
        self._call_args = []

    def record_args(self, *args):
        self._call_count += 1
        self._call_args.append(args)

    def num_calls(self):
        """Returns number of times function has been called."""

        return self._call_count

    def args(self):
        """
        Returns list of arguments given on each call.

        Each list element is a tuple of args and kwargs.
        """

        return self._call_args


class FuncReturningFixedValue(MockFunction):
    """
    Provides mock function returning the same value on each call.
    """

    def __init__(self, retval=None):
        """
        :param retvals: Return value (default: None).
        """

        super(FuncReturningFixedValue, self).__init__()
        self._retval = retval

    def __call__(self, *args, **kwargs):
        self.record_args(args, kwargs)
        return self._retval


class FuncReturningValueSequence(MockFunction):
    """
    Provides mock function returning one item from sequence per call.
    """

    def __init__(self, retvals=None):
        """
        :param retvals: Iterable providing values to return (default: []).
        """

        super(FuncReturningValueSequence, self).__init__()
        self._retvals = retvals if retvals is not None else []

    def __call__(self, *args, **kwargs):
        self.record_args(args, kwargs)
        return self._retvals[self._call_count - 1]


class MethodMocker(MockFunction):
    """
    Base class for mockers providing and managing mock methods.

    For methods, mocking is slightly more complicated than for plain
    functions, as we need a function that can be inserted into a
    class as unbound method and at the same time provide an interface
    to read out call data after the method has been used.

    This results in the following usage pattern:

    class A(object):
        pass

        mocker = FixedValueMethodMocker(123)
        A.meth = mocker.get_method()
        a = A()
        a.meth()
        print mocker.num_calls()
     """

    def __init__(self):
        super(MethodMocker, self).__init__()

    def callers(self):
        """Returns list of objects on which method as called."""

        return [caller for caller, _, _ in self.args()]

    def caller_ids(self):
        """Returns ids of objects on which method was called."""

        return [id(caller) for caller in self.callers()]

    def caller_types(self):
        """Returns types of objects on which method was called."""

        return [type(caller) for caller in self.callers()]

    def multiple_calls_per_caller(self):
        """
        True if method was called more than once on any object.

        The result is True unless the method was called at most once
        per object.
        """

        caller_ids = self.caller_ids()
        return len(set(caller_ids)) < len(caller_ids)


class FixedValueMethodMocker(MethodMocker):
    """
    Provides mock method returning the same value on each call.
    """

    def __init__(self, retval=None):
        """
        :param retvals: Return value (default: None).
        """

        super(FixedValueMethodMocker, self).__init__()
        self._retval = retval

    def get_method(self):
        """Returns actual mock method."""

        def mockmethod(mmself, *args, **kwargs):
            self.record_args(mmself, args, kwargs)
            return self._retval

        return mockmethod


class ValueSequenceMethodMocker(MethodMocker):
    """
    Provides mock method returning a sequence of values.

    Note: All objects share the sequence of values, i.e., the n-th
          call to the method will return the n-th value, independent
          of on which object the method is called.    """

    def __init__(self, retvals):
        """
        :param retvals: Return value (default: []).
        """

        super(ValueSequenceMethodMocker, self).__init__()
        self._retvals = retvals if retvals is not None else []

    def get_method(self):
        """Returns actual mock method."""

        def mockmethod(mmself, *args, **kwargs):
            self.record_args(mmself, args, kwargs)
            return self._retvals[self._call_count - 1]

        return mockmethod

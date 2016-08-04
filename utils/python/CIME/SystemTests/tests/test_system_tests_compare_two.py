#!/usr/bin/env python

"""
This module contains unit tests of SystemTestsCompareTwo.

This tests the logic implemented in SystemTestsCompareTwo itself, but does NOT
test the logic in the base class, SystemTestsCommon: most of the base class is
stubbed out in these tests.
"""

import unittest
from collections import namedtuple
from CIME.SystemTests.system_tests_compare_two import SystemTestsCompareTwo

# ========================================================================
# Stub version of Case object that provides the functionality needed by the
# SystemTestsCommon __init__ method.
# ========================================================================

class CaseStub(object):
    def get_value(self, varname):
        return " "

# ========================================================================
# Structure for storing information about calls made to methods
# ========================================================================

"""
You can create a Call object to record a single call made to a method:

Call(method, arguments)
    method (str): name of method
    arguments (dict): dictionary mapping argument names to values

Example:
    If you want to record a call to foo(bar = 1, baz = 2):
        somecall = Call(method = 'foo', arguments = {'bar': 1, 'baz': 2})
    Or simply:
        somecall = Call('foo', {'bar': 1, 'baz': 2})
"""
Call = namedtuple('Call', ['method', 'arguments'])

def get_call_methods(calls):
    """
    Given a list of calls, return a list of just the methods.

    Args:
        calls (list of Call objects)

    >>> mycalls = [Call('hello', {'x': 3}), Call('goodbye', {'y': 4})]
    >>> get_call_methods(mycalls)
    ['hello', 'goodbye']
    """
    return [onecall.method for onecall in calls]



# ========================================================================
# Names of methods for which we want to record calls
# ========================================================================

# We use constants for these method names because, in some cases, a typo in a
# hard-coded string could cause a test to always pass, which would be a Bad
# Thing.
#
# For now the names of the constants match the strings they equate to, which
# match the actual method names. But it's fine if this doesn't remain the case
# moving forward (which is another reason to use constants rather than
# hard-coded strings in the tests).

METHOD_run = "_run"
METHOD_component_compare_test = "_component_compare_test"
METHOD_stage_saved_pes_file = "_stage_saved_pes_file"
METHOD_stage_saved_build_files = "_stage_saved_build_files"
METHOD_load_staged_xml_files = "_load_staged_xml_files"
METHOD_run_common_setup = "_run_common_setup"
METHOD_run_one_setup = "_run_one_setup"
METHOD_run_two_setup = "_run_two_setup"

# ========================================================================
# Fake version of SystemTestsCompareTwo that overrides some functionality for
# the sake of unit testing.
# ========================================================================

# A SystemTestsCompareTwoFake object can be controlled to fail at a given
# point. See the documentation in its __init__ method for details.
#
# It logs what methods have been called in its log attribute; this is a list of
# Call objects (see above for their definition). For example, if the call
# sequence was:
#     self._run_one_setup()
#     self._run(suffix = 'base')
#     self._run(suffix = 'test')
#     self._component_compare_test(suffix1 = 'base', suffix2 = 'test')
#
# Then mytest.log would be:
# [Call(METHOD_run_one_setup, {}),
#  Call(METHOD_run, {'suffix': 'base'})
#  Call(METHOD_run, {'suffix': 'test'}),
#  Call(METHOD_component_compare_test, {'suffix1': 'base', 'suffix2': 'test'})]

class SystemTestsCompareTwoFake(SystemTestsCompareTwo):
    def __init__(self,
                 two_builds_for_sharedlib = False,
                 two_builds_for_model = False,
                 runs_have_different_pe_settings = False,
                 run_one_suffix = "base",
                 run_two_suffix = "test",
                 run_one_should_pass = True,
                 run_two_should_pass = True,
                 compare_should_pass = True):
        """
        Initialize a SystemTestsCompareTwoFake object

        This object can be controlled to fail at a given point via the arguments
        to this method:

        Args:
            two_builds_for_sharedlib (bool, optional): Option passed to
                SystemTestsCompareTwo.__init__. Defaults to False.
            two_builds_for_model (bool, optional): Option passed to
                SystemTestsCompareTwo.__init__. Defaults to False.
            runs_have_different_pe_settings (bool, optional): Option passed to
                SystemTestsCompareTwo.__init__. Defaults to False.
            run_one_suffix (str, optional): Suffix used for the first run. Defaults to 'base'.
            run_two_suffix (str, optional): Suffix used for the second run. Defaults to 'test'.
            run_one_should_pass (bool, optional): Whether the _run method should
                pass for the first run. Default is True, meaning it will pass.
            run_two_should_pass (bool, optional): Whether the _run method should
                pass for the second run. Default is True, meaning it will pass.
            compare_should_pass (bool, optional): Whether
                _component_compare_test should pass. Default is True, meaning it
                will pass.
        """

        # NOTE(wjs, 2016-08-03) Currently, due to limitations in the test
        # infrastructure, run_one_suffix MUST be 'base'. However, I'm keeping it
        # as an explicit argument to the constructor so that it's easy to relax
        # this requirement later: To relax this assumption, remove the following
        # assertion and add run_one_suffix as an argument to
        # SystemTestsCompareTwo.__init__
        assert(run_one_suffix == 'base')

        case = CaseStub()
        SystemTestsCompareTwo.__init__(
            self,
            case,
            two_builds_for_sharedlib = two_builds_for_sharedlib,
            two_builds_for_model = two_builds_for_model,
            runs_have_different_pe_settings = runs_have_different_pe_settings,
            run_two_suffix = run_two_suffix)

        self._run_pass_suffixes = []
        if (run_one_should_pass):
            self._run_pass_suffixes.append(run_one_suffix)
        if (run_two_should_pass):
            self._run_pass_suffixes.append(run_two_suffix)

        self._compare_should_pass = compare_should_pass

        self.log = []

    # ------------------------------------------------------------------------
    # Stubs of methods called by SystemTestsCommon.__init__ that interact with
    # the system or case object in ways we want to avoid here
    # ------------------------------------------------------------------------

    def _init_environment(self, caseroot):
        pass

    def _init_locked_files(self, caseroot, expected):
        pass

    def _init_case_setup(self):
        pass

    # ------------------------------------------------------------------------
    # Fake implementations of methods that are typically provided by SystemTestsCommon
    # ------------------------------------------------------------------------

    def _run(self, suffix = "base"):
        """
        Fake _run method. Whether this passes or fails depends on whether suffix is
        a member of self._run_passes_suffixes
        """

        self.log.append(Call(METHOD_run, {'suffix': suffix}))

        if suffix in self._run_pass_suffixes:
            success = True
        else:
            success = False

        return success

    def _component_compare_test(self, suffix1, suffix2):
        """
        Fake _component_compare_test method. Whether this passes or fails
        depends on self._compare_should_pass (and is independent of suffix1 and
        suffix2).
        """

        self.log.append(Call(METHOD_component_compare_test,
                             {'suffix1': suffix1, 'suffix2': suffix2}))

        if (self._compare_should_pass):
            success = True
        else:
            success = False

        return success

    def _stage_saved_pes_file(self, suffix):
        self.log.append(Call(METHOD_stage_saved_pes_file, {'suffix': suffix}))

    def _stage_saved_build_files(self, suffix):
        self.log.append(Call(METHOD_stage_saved_build_files, {'suffix': suffix}))

    def _load_staged_xml_files(self, modified_pes):
        self.log.append(Call(METHOD_load_staged_xml_files, {'modified_pes': modified_pes}))

    # ------------------------------------------------------------------------
    # Fake implementations of methods that are typically provided by the
    # individual test
    # ------------------------------------------------------------------------

    def _run_common_setup(self):
        self.log.append(Call(METHOD_run_common_setup, {}))

    def _run_one_setup(self):
        self.log.append(Call(METHOD_run_one_setup, {}))

    def _run_two_setup(self):
        self.log.append(Call(METHOD_run_two_setup, {}))


# ========================================================================
# Test class itself
# ========================================================================

class TestSystemTestsCompareTwo(unittest.TestCase):

    # ------------------------------------------------------------------------
    # Tests of passing test cases
    # ------------------------------------------------------------------------

    def test_no_failures_one_build_call_sequence(self):
        # Ensure that the sequencing of calls to internal methods is correct
        # when a single-build test (with only a single PE layout) is run with no
        # failures

        # Setup
        run_one_suffix = 'base'
        run_two_suffix = 'run2'
        mytest = SystemTestsCompareTwoFake(
            run_one_suffix = run_one_suffix,
            run_two_suffix = run_two_suffix)

        # Exercise
        mytest.run()

        # Verify
        expected_calls = [
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_one_setup, {}),
            Call(METHOD_run, {'suffix': run_one_suffix}),
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_two_setup, {}),
            Call(METHOD_run, {'suffix': run_two_suffix}),
            Call(METHOD_component_compare_test,
                 {'suffix1': run_one_suffix, 'suffix2': run_two_suffix})]
        self.assertEqual(expected_calls, mytest.log)


    def test_no_failures_two_builds_call_sequence(self):
        # Ensure that the sequencing of calls to internal methods is correct
        # when a two-build test is run with no failures

        # Setup
        run_one_suffix = 'base'
        run_two_suffix = 'run2'
        mytest = SystemTestsCompareTwoFake(
            two_builds_for_model = True,
            run_one_suffix = run_one_suffix,
            run_two_suffix = run_two_suffix)

        # Exercise
        mytest.run()

        # Verify
        expected_calls = [
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_one_setup, {}),
            Call(METHOD_stage_saved_build_files, {'suffix': run_one_suffix}),
            Call(METHOD_load_staged_xml_files, {'modified_pes': False}),
            Call(METHOD_run, {'suffix': run_one_suffix}),
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_two_setup, {}),
            Call(METHOD_stage_saved_build_files, {'suffix': run_two_suffix}),
            Call(METHOD_load_staged_xml_files, {'modified_pes': False}),
            Call(METHOD_run, {'suffix': run_two_suffix}),
            Call(METHOD_component_compare_test,
                 {'suffix1': run_one_suffix, 'suffix2': run_two_suffix})]
        self.assertEqual(expected_calls, mytest.log)

    def test_no_failures_different_pes_call_sequence(self):
        # Ensure that the sequencing of calls to internal methods is correct
        # when a test with different PE layouts is run with no failures

        # Setup
        run_one_suffix = 'base'
        run_two_suffix = 'run2'
        mytest = SystemTestsCompareTwoFake(
            runs_have_different_pe_settings = True,
            run_one_suffix = run_one_suffix,
            run_two_suffix = run_two_suffix)

        # Exercise
        mytest.run()

        # Verify
        expected_calls = [
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_one_setup, {}),
            Call(METHOD_stage_saved_pes_file, {'suffix': run_one_suffix}),
            Call(METHOD_load_staged_xml_files, {'modified_pes': True}),
            Call(METHOD_run, {'suffix': run_one_suffix}),
            Call(METHOD_run_common_setup, {}),
            Call(METHOD_run_two_setup, {}),
            Call(METHOD_stage_saved_pes_file, {'suffix': run_two_suffix}),
            Call(METHOD_load_staged_xml_files, {'modified_pes': True}),
            Call(METHOD_run, {'suffix': run_two_suffix}),
            Call(METHOD_component_compare_test,
                 {'suffix1': run_one_suffix, 'suffix2': run_two_suffix})]
        self.assertEqual(expected_calls, mytest.log)


    def test_no_failures_status(self):
        # Ensure that the return value and individual pieces of the test status
        # are correct when a test is run with no failures

        # Setup
        mytest = SystemTestsCompareTwoFake()

        # Exercise
        result = mytest.run()

        # Verify
        self.assertTrue(result)
        self.assertEqual('PASS', mytest.get_run_one_status())
        self.assertEqual('PASS', mytest.get_run_two_status())
        self.assertEqual('PASS', mytest.get_compare_status())

    # ------------------------------------------------------------------------
    # Tests of failures in run 1
    # ------------------------------------------------------------------------

    def test_run1fail_run2_and_compare_not_done(self):
        # If run 1 fails, then run 2 and the comparison should NOT be done

        # Setup
        run_one_suffix = 'base'
        run_two_suffix = 'run2'
        mytest = SystemTestsCompareTwoFake(
            run_one_suffix = run_one_suffix,
            run_two_suffix = run_two_suffix,
            run_one_should_pass = False)

        # Exercise
        mytest.run()

        # Verify
        #
        # This verification is designed to:
        # (1) Be robust to inconsequential variations in the system under test
        #     (so we don't hard-code the entire run sequence here)
        # (2) Be unlikely to pass when it shouldn't (so, for example, we check
        #     that METHOD_run was called exactly once, rather than checking:
        #         assertNotIn(Call(METHOD_run, {'suffix': run_two_suffix}), mytest.log)
        #     because the latter would pass if there was a call to METHOD_run
        #     with run_two_suffix but also with some other arguments.

        method_calls = get_call_methods(mytest.log)

        # Verify that there was only one call to METHOD_run, and it was for run1
        # (in that case, we know we don't have a call to run2)
        self.assertEqual(1, method_calls.count(METHOD_run))
        self.assertIn(Call(METHOD_run, {'suffix': run_one_suffix}), mytest.log)

        # Verify that there was NOT a call to METHOD_component_compare_test
        self.assertNotIn(METHOD_component_compare_test, method_calls)

    def test_run1fail_status(self):
        # Ensure that the return value and individual pieces of the test status
        # are correct when run 1 fails

        # Setup
        mytest = SystemTestsCompareTwoFake(run_one_should_pass = False)

        # Exercise
        result = mytest.run()

        # Verify
        self.assertFalse(result)
        self.assertEqual('FAIL', mytest.get_run_one_status())
        self.assertEqual('NOT RUN', mytest.get_run_two_status())
        self.assertEqual('NOT RUN', mytest.get_compare_status())

    # ------------------------------------------------------------------------
    # Tests of failures in run 2
    # ------------------------------------------------------------------------

    def test_run2fail_compare_not_done(self):
        # If run 2 fails, then the comparison should NOT be done

        # Setup
        mytest = SystemTestsCompareTwoFake(run_two_should_pass = False)

        # Exercise
        mytest.run()

        # Verify
        method_calls = get_call_methods(mytest.log)
        # Verify that there was NOT a call to METHOD_component_compare_test
        self.assertNotIn(METHOD_component_compare_test, method_calls)

    def test_run2fail_status(self):
        # Ensure that the return value and individual pieces of the test status
        # are correct when run 2 fails

        # Setup
        mytest = SystemTestsCompareTwoFake(run_two_should_pass = False)

        # Exercise
        result = mytest.run()

        # Verify
        self.assertFalse(result)
        self.assertEqual('PASS', mytest.get_run_one_status())
        self.assertEqual('FAIL', mytest.get_run_two_status())
        self.assertEqual('NOT RUN', mytest.get_compare_status())

    # ------------------------------------------------------------------------
    # Tests of failures in the comparison
    # ------------------------------------------------------------------------

    def test_compare_fails_status(self):
        # Ensure that the return value and individual pieces of the test status
        # are correct when the comparison between runs 1 and 2 fails

        # Setup
        mytest = SystemTestsCompareTwoFake(compare_should_pass = False)

        # Exercise
        result = mytest.run()

        # Verify
        self.assertFalse(result)
        self.assertEqual('PASS', mytest.get_run_one_status())
        self.assertEqual('PASS', mytest.get_run_two_status())
        self.assertEqual('FAIL', mytest.get_compare_status())

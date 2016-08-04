"""
Base class for CIME system tests that involve doing two runs and comparing their
output.

In the __init__ method for your test, you MUST call
    SystemTestsCompareTwo.__init__
See the documentation of that method for details.

Classes that inherit from this are REQUIRED to implement the following methods:

(1) _run_common_setup
    This method will be called before both the first and second phase of the
    two-phase test, before either _run_one_setup or
    _run_two_setup. This should contain settings needed for both phases of
    the run, such as setting CONTINUE_RUN to False. In principle, these settings
    could just be made once, but for robustness and communication purposes, this
    is executed before both run phases.

(2) _run_one_setup
    This method will be called to set up the run for the first phase of the
    two-phase test

(3) _run_two_setup
    This method will be called to set up the run for the second phase of the
    two-phase test

Classes that inherit from this MAY implement the following methods, if they have
any work to be done in these phases:

(1) _pre_build
    This method will be called immediately before the build. This can contain
    work like copying user_nl files to some saved location

(2) _adjust_pes_for_run_one

(3) _adjust_pes_for_run_two

(4) _build_one_setup
    This method is used for tests that have either two_builds_for_sharedlib
    and/or two_builds_for_model True. This method will be called immediately
    before the first build.

(5) _build_two_setup
    This method is used for tests that have either two_builds_for_sharedlib
    and/or two_builds_for_model True. This method will be called immediately
    before the second build.
"""

from CIME.XML.standard_module_setup import *
from CIME.case_setup import case_setup
from CIME.SystemTests.system_tests_common import SystemTestsCommon

logger = logging.getLogger(__name__)

class SystemTestsCompareTwo(SystemTestsCommon):

    # suffix used for saving original versions of files
    ORIGINAL_SUFFIX = "original"

    def __init__(self,
                 case,
                 two_builds_for_sharedlib,
                 two_builds_for_model,
                 runs_have_different_pe_settings,
                 run_two_suffix = 'test',
                 run_one_description = '',
                 run_two_description = ''):
        """
        Initialize a SystemTestsCompareTwo object. Individual test cases that
        inherit from SystemTestsCompareTwo MUST call this __init__ method.

        Args:
            case: case object passsed to __init__ method of individual test
            two_builds_for_sharedlib (bool): Whether two separate builds are
                needed for the sharedlib build (this should be False for tests
                that only change runtime options)
            two_builds_for_model (bool): Whether two separate builds are needed
                for the model build (this should be False for tests that only
                change runtime options)
            runs_have_different_pe_settings (bool): Whether the two runs have
                different PE settings. Typically, this will imply
                two_builds_for_sharedlib and/or two_builds_for_model, but that
                is not necessarily the case. If runs_have_different_pe_settings
                is True, then the test is responsible for saving copies of the
                env_mach_pes.xml file for each run, via save_xml_file, sometime
                in the build phase. This will typically be done in
                _build_one_setup and _build_two_setup, but in principle both
                versions could be created and saved in _pre_build.
            run_two_suffix (str, optional): Suffix appended to files output by
                the second run. Defaults to 'test'. This can be anything other
                than 'base' (which is the suffix used for the first run).
            run_one_description (str, optional): Description printed to log file
                when starting the first run. Defaults to ''.
            run_two_description (str, optional): Description printed to log file
                when starting the second run. Defaults to ''.
        """
        SystemTestsCommon.__init__(self, case)

        self._runs_have_different_pe_settings = runs_have_different_pe_settings
        self._two_builds_for_sharedlib = two_builds_for_sharedlib
        self._two_builds_for_model = two_builds_for_model

        # NOTE(wjs, 2016-08-03) It is currently CRITICAL for run_one_suffix to
        # be 'base', because this is assumed for baseline comparison and
        # generation. Once that assumption is relaxed, then run_one_suffix can
        # be set in the call to the constructor just like run_two_suffix
        # currently is.
        self._run_one_suffix = 'base'
        self._run_two_suffix = run_two_suffix.rstrip()
        expect(self._run_two_suffix != self._run_one_suffix,
               "ERROR: Must have different suffixes for run one and run two")
        expect(self._run_one_suffix != self.ORIGINAL_SUFFIX,
               "ERROR: Run one suffix cannot be '%s'"%(self.ORIGINAL_SUFFIX))
        expect(self._run_two_suffix != self.ORIGINAL_SUFFIX,
               "ERROR: Run two suffix cannot be '%s'"%(self.ORIGINAL_SUFFIX))

        self._run_one_description = run_one_description
        self._run_two_description = run_two_description

        # Initialize results
        # TODO(wjs, 2016-07-27) Currently these results of the individual pieces
        # aren't used anywhere, but I'm storing them because I think it would be
        # helpful to use them in the test reporting
        self._status_run1 = "NOT RUN"
        self._status_run2 = "NOT RUN"
        self._status_compare = "NOT RUN"


    # ========================================================================
    # Methods that MUST be implemented by specific tests that inherit from this
    # base class
    # ========================================================================

    def _run_common_setup(self):
        """
        This method will be called before both the first and second phase of the
        two-phase test, before either _run_one_setup or
        _run_two_setup. This should contain settings needed for both phases of
        the run, such as setting CONTINUE_RUN to False. In principle, these settings
        could just be made once, but for robustness and communication purposes, this
        is executed before both run phases.

        For tests with two separate builds, this does NOT need to move the
        proper executable into place: that is done automatically by this base class.
        """
        raise NotImplementedError


    def _run_one_setup(self):
        """
        Sets up the run for the first phase of the two-phase test.

        All tests inheriting from this base class MUST implement this method.

        For tests with two separate builds, this does NOT need to move the
        proper executable into place: that is done automatically by this base
        class. Similarly, staging the proper env_build and env_mach_pes files
        are done automatically and do not need to be done in _run_one_setup.
        """
        raise NotImplementedError

    def _run_two_setup(self):
        """
        Sets up the run for the second phase of the two-phase test.

        All tests inheriting from this base class MUST implement this method.

        For tests with two separate builds, this does NOT need to move the
        proper executable into place: that is done automatically by this base
        class. Similarly, staging the proper env_build and env_mach_pes files
        are done automatically and do not need to be done in _run_two_setup.
        """
        raise NotImplementedError

    # ========================================================================
    # Methods that MAY be implemented by specific tests that inherit from this
    # base class, if they have any work that needs to be done during these
    # phases
    # ========================================================================

    def _pre_build(self):
        """
        This method will be called immediately before the build. This can
        contain work like copying user_nl files to some saved location.

        Note that this may be called multiple times: once for the sharedlib
        build, once for the model build, and potentially more times if the case
        is rebuilt. Thus, anything that is done in this method must be written
        so that it is robust to being called multiple times.

        For a test with two_builds_for_sharedlib and/or two_builds_for_model
        True, this is called once before both builds are done (NOT once for
        build1 and once for build2).
        """
        pass

    def _adjust_pes_for_run_one(self):
        raise NotImplementedError(
            "_adjust_pes_for_run_one must be implemented by tests with two PE layouts")

    def _adjust_pes_for_run_two(self):
        raise NotImplementedError(
            "_adjust_pes_for_run_two must be implemented by tests with two PE layouts")

    def _build_one_setup(self):
        """
        This method is used for tests that have either two_builds_for_sharedlib
        and/or two_builds_for_model True. This method will be called immediately
        before the first build.

        This MUST be implemented by tests with two builds.

        For a test that has (e.g.) two_builds_for_sharedlib True but
        two_builds_for_model False, this is called before the first build for
        the sharedlib, but NOT before the (common) model build.
        """
        raise NotImplementedError(
            "_build_one_setup must be implemented by tests with two builds")

    def _build_two_setup(self):
        """
        This method is used for tests that have either two_builds_for_sharedlib
        and/or two_builds_for_model True. This method will be called immediately
        before the second build.

        This MUST be implemented by tests with two builds.

        For a test that has (e.g.) two_builds_for_sharedlib True but
        two_builds_for_model False, this is called before the second build for
        the sharedlib, but NOT before the (common) model build.
        """
        raise NotImplementedError(
            "_build_one_setup must be implemented by tests with two builds")

    # ========================================================================
    # Main public methods
    # ========================================================================

    def build(self, sharedlib_only=False, model_only=False):
        self._pre_build_restore_or_save_xml_files()
        if self._runs_have_different_pe_settings:
            self._create_pe_files()
        self._pre_build()

        if self._needs_two_builds(sharedlib_only = sharedlib_only,
                                  model_only = model_only):
            self._do_two_builds(sharedlib_only=sharedlib_only, model_only=model_only)
        else:
            if self._runs_have_different_pe_settings:
                # Two different PE settings, yet only one build.
                #
                # Arbitrarily use the first run's PE settings for the build
                self._stage_saved_pes_file(suffix=self._run_one_suffix)
                self._load_staged_xml_files(modified_pes=True)
            SystemTestsCommon.build(self, sharedlib_only=sharedlib_only, model_only=model_only)

    def run(self):
        """
        Runs both phases of the two-phase test and compares their results
        """

        # First run
        self._run_common_setup()
        self._run_one_setup()
        if (self._runs_have_different_pe_settings):
            self._stage_saved_pes_file(self._run_one_suffix)
        if (self._has_two_executables()):
            self._stage_saved_build_files(self._run_one_suffix)
        if (self._runs_have_different_pe_settings or self._has_two_executables()):
            self._load_staged_xml_files(modified_pes=self._runs_have_different_pe_settings)
        logger.info('Doing first run: ' + self._run_one_description)
        success = self._run(self._run_one_suffix)
        if success:
            self._status_run1 = "PASS"
        else:
            self._status_run1 = "FAIL"
            return False

        # Second run
        self._run_common_setup()
        self._run_two_setup()
        if (self._runs_have_different_pe_settings):
            self._stage_saved_pes_file(self._run_two_suffix)
        if (self._has_two_executables()):
            self._stage_saved_build_files(self._run_two_suffix)
        if (self._runs_have_different_pe_settings or self._has_two_executables()):
            self._load_staged_xml_files(modified_pes=self._runs_have_different_pe_settings)
        logger.info('Doing second run: ' + self._run_two_description)
        success = self._run(self._run_two_suffix)
        if success:
            self._status_run2 = "PASS"
        else:
            self._status_run2 = "FAIL"
            return False

        # Compare results
        success = self._component_compare_test(self._run_one_suffix, self._run_two_suffix)
        if success:
            self._status_compare = "PASS"
        else:
            self._status_compare = "FAIL"
            return False

        return success

    def get_run_one_status(self):
        """
        Returns a string specifying the status of run 1
        """
        return self._status_run1

    def get_run_two_status(self):
        """
        Returns a string specifying the status of run 2
        """
        return self._status_run2

    def get_compare_status(self):
        """
        Returns a string specifying the status of the comparison between run 1
        and run 2
        """
        return self._status_compare

    # ========================================================================
    # Private methods
    # ========================================================================

    def _needs_two_builds(self, sharedlib_only, model_only):
        if (not sharedlib_only and not model_only):
            # building both at once
            two_builds_needed = (self._two_builds_for_sharedlib or self._two_builds_for_model)
        elif sharedlib_only:
            two_builds_needed = self._two_builds_for_sharedlib
        elif model_only:
            two_builds_needed = self._two_builds_for_model
        else:
            raise ValueError('Invalid for both sharedlib_only and model_only to be set')

        return two_builds_needed

    def _has_two_executables(self):
        if (self._two_builds_for_sharedlib or
            self._two_builds_for_model):
            two_executables = True
        else:
            two_executables = False

        return two_executables

    def _pre_build_restore_or_save_xml_files(self):
        """
        For tests that change either env_build or env_mach_pes: At the start of
        each call to the build method, we restore the original versions of these
        files, so that we're sure to start with the correct version even if we
        are rebuilding a test that was killed part-way through the last build or
        run.

        If there are no saved files to restore, then we assume that the current
        files in the case directory are the originals, and save them here
        """

        if self._runs_have_different_pe_settings:
            env_mach_pes_restored = restore_or_save_xml_file(
                caseroot = self._caseroot,
                xml_file = 'env_mach_pes',
                suffix = self.ORIGINAL_SUFFIX)
        else:
            env_mach_pes_restored = False

        if self._has_two_executables():
            env_build_restored = restore_or_save_xml_file(
                caseroot = self._caseroot,
                xml_file = 'env_build',
                suffix = self.ORIGINAL_SUFFIX)
        else:
            env_build_restored = False

        if (env_mach_pes_restored or env_build_restored):
            # Here we do not run case_setup, even if we restored env_mach_pes:
            # we'll end up doing that later for cases that use two different
            # env_mach_pes files
            self._case.read_xml()

    def _create_pe_files(self):
        # I'm doing the creation of pe files in its own step, rather than
        # folding it in with the build1 and build2 setups, because (a) it makes
        # it easier to think about how the different-pe-setting option plays
        # together with the needs_two_builds option (specifically, if the former
        # is True but the latter is False); (b) by doing this in its own step,
        # we allow this shared infrastructure to handle the timing of saving the
        # env_mach_pes files (and making sure that case.flush is called first),
        # rather than requiring individual tests to do that.

        if not saved_xml_file_exists(
                caseroot = self._caseroot,
                xml_file = 'env_mach_pes',
                suffix = self._run_one_suffix):

            self._adjust_pes_for_run_one()

            # I think this flush is needed so that the changes in PEs are
            # reflected on disk
            self._case.flush()
            save_xml_file(
                caseroot = self._caseroot,
                xml_file = 'env_mach_pes',
                suffix = self._run_one_suffix)

        if not saved_xml_file_exists(
                caseroot = self._caseroot,
                xml_file = 'env_mach_pes',
                suffix = self._run_two_suffix):

            self._adjust_pes_for_run_two()

            # I think this flush is needed so that the changes in PEs are
            # reflected on disk
            self._case.flush()
            save_xml_file(
                caseroot = self._caseroot,
                xml_file = 'env_mach_pes',
                suffix = self._run_two_suffix)

    def _do_two_builds(self, sharedlib_only, model_only):
        # First build
        if self._runs_have_different_pe_settings:
            self._stage_saved_pes_file(suffix=self._run_one_suffix)
            self._load_staged_xml_files(modified_pes=True)
        self._build_one_setup()
        SystemTestsCommon.build(self, sharedlib_only=sharedlib_only, model_only=model_only)
        # FIXME(wjs, 2016-08-04) I'm not sure if it will work to save the build
        # files at this point. e.g., if we're just in the sharedlib_only phase,
        # then we wouldn't have an executable to save at the end of the
        # build. And I'm not sure when is the right time to save the env_build
        # file, given that we call the build twice (once with sharedlib_only and
        # once with model_only).
        self._save_build_files(suffix=self._run_one_suffix)

        # Second build
        if self._runs_have_different_pe_settings:
            self._stage_saved_pes_file(suffix=self._run_two_suffix)
            self._load_staged_xml_files(modified_pes=True)
        self._build_two_setup()
        SystemTestsCommon.build(self, sharedlib_only=sharedlib_only, model_only=model_only)
        # FIXME(wjs, 2016-08-04) See fixme note above for first build: that
        # applies here, too.
        self._save_build_files(suffix=self._run_two_suffix)


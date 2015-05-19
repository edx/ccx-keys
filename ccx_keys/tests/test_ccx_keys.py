import ddt
from bson.objectid import ObjectId
from itertools import product
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import CourseLocator
from opaque_keys.edx.tests import LocatorBaseTest, TestDeprecated

from ccx_keys.locator import CCXLocator
from ccx_keys.locator import CCXBlockUsageLocator


@ddt.ddt
class TestCCXKeys(LocatorBaseTest, TestDeprecated):
    """
    Tests of :class:`.CCXKey` and :class:`.CCXLocator`
    """

    def test_ccx_constructor_package_id(self):
        """Verify a locator constructed without branch or version is correct"""
        org = 'mit.eecs'
        course = '6002x'
        run = '2014_T2'
        ccx = '1'
        testurn = '{}+{}+{}+{}@{}'.format(
            org, course, run, CCXLocator.CCX_PREFIX, ccx
        )
        testobj = CCXLocator(org=org, course=course, run=run, ccx=ccx)

        self.check_course_locn_fields(
            testobj, org=org, course=course, run=run
        )
        self.assertEqual(testobj.ccx, ccx)
        # Allow access to _to_string
        # pylint: disable=protected-access
        self.assertEqual(testobj._to_string(), testurn)

    def test_ccx_constructor_version_guid(self):
        """Verify a locator constructed with only version_guid is correct"""
        test_id_loc = '519665f6223ebd6980884f2b'
        ccx = '1'
        expected_urn = '{}@{}+{}@{}'.format(
            CCXLocator.VERSION_PREFIX, test_id_loc,
            CCXLocator.CCX_PREFIX, ccx
        )
        testobj = CCXLocator(version_guid=test_id_loc, ccx=ccx)

        self.check_course_locn_fields(
            testobj,
            version_guid=ObjectId(test_id_loc),
        )
        self.assertEqual(testobj.ccx, ccx)
        # Allow access to _to_string
        # pylint: disable=protected-access
        self.assertEqual(testobj._to_string(), expected_urn)

    def test_ccx_constructor_package_id_separate_branch(self):
        """Verify a locator constructed with branch is correct"""
        org = 'mit.eecs'
        course = '6002x'
        run = '2014_T2'
        test_branch = 'published'
        ccx = '1'
        expected_urn = '{}+{}+{}+{}@{}+{}@{}'.format(
            org, course, run,
            CCXLocator.BRANCH_PREFIX, test_branch,
            CCXLocator.CCX_PREFIX, ccx
        )
        testobj = CCXLocator(
            org=org, course=course, run=run, branch=test_branch, ccx=ccx
        )

        self.check_course_locn_fields(
            testobj,
            org=org,
            course=course,
            run=run,
            branch=test_branch,
        )
        self.assertEqual(testobj.ccx, ccx)
        # Allow access to _to_string
        # pylint: disable=protected-access
        self.assertEqual(testobj._to_string(), expected_urn)

    def test_ccx_constructor_package_id_branch_and_version_guid(self):
        """Verify a locator constructed with branch and version is correct"""
        test_id_loc = '519665f6223ebd6980884f2b'
        org = 'mit.eecs'
        course = '~6002x'
        run = '2014_T2'
        branch = 'draft-1'
        ccx = '1'
        expected_urn = '{}+{}+{}+{}@{}+{}@{}+{}@{}'.format(
            org, course, run,
            CCXLocator.BRANCH_PREFIX, branch,
            CCXLocator.VERSION_PREFIX, test_id_loc,
            CCXLocator.CCX_PREFIX, ccx
        )
        testobj = CCXLocator(
            org=org,
            course=course,
            run=run,
            branch=branch,
            version_guid=test_id_loc,
            ccx=ccx
        )

        self.check_course_locn_fields(
            testobj,
            org=org,
            course=course,
            run=run,
            branch=branch,
            version_guid=ObjectId(test_id_loc)
        )
        self.assertEqual(testobj.ccx, ccx)
        # Allow access to _to_string
        # pylint: disable=protected-access
        self.assertEqual(testobj._to_string(), expected_urn)

    @ddt.data(
        ('version_guid'),
        ('org', 'course', 'run'),
        ('org', 'course', 'run', 'branch'),
        ('org', 'course', 'run', 'version_guid'),
        ('org', 'course', 'run', 'branch', 'version_guid'),
    )
    def test_missing_ccx_id(self, fields):
        """Verify that otherwise valid arguments fail without ccx"""
        available_fields = {
            'version_guid': '519665f6223ebd6980884f2b',
            'org': 'mit.eecs',
            'course': '6002x',
            'run': '2014_T2',
            'branch': 'draft-1',
        }
        use_fields = dict(
            (k, v) for k, v in available_fields.items() if k in fields
        )
        with self.assertRaises(InvalidKeyError) as cm:
            CCXLocator(**use_fields)

        self.assertTrue(str(CCXLocator) in str(cm.exception))

    @ddt.unpack
    @ddt.data(
        {'fields': ('version_guid',),
         'url_template': '{CANONICAL_NAMESPACE}:{VERSION_PREFIX}@{version_guid}+{CCX_PREFIX}@{ccx}',
         },
        {'fields': ('org', 'course', 'run'),
         'url_template': '{CANONICAL_NAMESPACE}:{org}+{course}+{run}+{CCX_PREFIX}@{ccx}',
         },
        {'fields': ('org', 'course', 'run', 'branch'),
         'url_template': '{CANONICAL_NAMESPACE}:{org}+{course}+{run}+{BRANCH_PREFIX}@{branch}+{CCX_PREFIX}@{ccx}',
         },
        {'fields': ('org', 'course', 'run', 'version_guid'),
         'url_template': '{CANONICAL_NAMESPACE}:{org}+{course}+{run}+{VERSION_PREFIX}@{version_guid}+{CCX_PREFIX}@{ccx}',
         },
        {'fields': ('org', 'course', 'run', 'branch', 'version_guid'),
         'url_template': '{CANONICAL_NAMESPACE}:{org}+{course}+{run}+{BRANCH_PREFIX}@{branch}+{VERSION_PREFIX}@{version_guid}+{CCX_PREFIX}@{ccx}',},
    )
    def test_locator_from_good_url(self, fields, url_template):
        available_fields = {
            'version_guid': '519665f6223ebd6980884f2b',
            'org': 'mit.eecs',
            'course': '6002x',
            'run': '2014_T2',
            'branch': 'draft-1',
            'ccx': '1',
            'CANONICAL_NAMESPACE': CCXLocator.CANONICAL_NAMESPACE,
            'VERSION_PREFIX': CCXLocator.VERSION_PREFIX,
            'BRANCH_PREFIX': CCXLocator.BRANCH_PREFIX,
            'CCX_PREFIX': CCXLocator.CCX_PREFIX,
        }
        this_url = url_template.format(**available_fields)
        testobj = CourseKey.from_string(this_url)
        use_keys = dict(
            (k, v) for k, v in available_fields.items() if k in fields
        )

        if 'version_guid' in use_keys:
            use_keys['version_guid'] = ObjectId(use_keys['version_guid'])
        self.check_course_locn_fields(testobj, **use_keys)
        self.assertEqual(testobj.ccx, available_fields['ccx'])

    @ddt.data(
        ('version_guid'),
        ('org', 'course', 'run'),
        ('org', 'course', 'run', 'branch'),
        ('org', 'course', 'run', 'version_guid'),
        ('org', 'course', 'run', 'branch', 'version_guid'),
    )
    def test_from_course_locator_constructor(self, fields):
        available_fields = {
            'version_guid': '519665f6223ebd6980884f2b',
            'org': 'mit.eecs',
            'course': '6002x',
            'run': '2014_T2',
            'branch': 'draft-1',
        }
        ccx = '1'
        use_fields = dict((k, v) for k, v in available_fields.items() if k in fields)
        course_id = CourseLocator(**use_fields)
        testobj = CCXLocator.from_course_locator(course_id, ccx)

        if 'version_guid' in use_fields:
            use_fields['version_guid'] = ObjectId(use_fields['version_guid'])
        self.check_course_locn_fields(testobj, **use_fields)
        self.assertEqual(testobj.ccx, ccx)


@ddt.ddt
class TestCCXBlockUsageLocator(LocatorBaseTest):
    """
    Tests of :class:`.CCXBlockUsageLocator`
    """
    @ddt.data(
        # do we need or even want to support deprecated forms of urls?
        "ccx-block-v1:org+course+run+ccx@1+{}@category+{}@name".format(CCXBlockUsageLocator.BLOCK_TYPE_PREFIX, CCXBlockUsageLocator.BLOCK_PREFIX),
        "ccx-block-v1:org+course+run+{}@revision+ccx@1+{}@category+{}@name".format(CourseLocator.BRANCH_PREFIX, CCXBlockUsageLocator.BLOCK_TYPE_PREFIX, CCXBlockUsageLocator.BLOCK_PREFIX),
        "i4x://org/course/category/name@revision",
        # now try the extended char sets - we expect that "%" should be OK in deprecated-style ids,
        # but should not be valid in new-style ids
        "ccx-block-v1:org.dept.sub-prof+course.num.section-4+run.hour.min-99+ccx@1+{}@category+{}@name:12.33-44".format(CCXBlockUsageLocator.BLOCK_TYPE_PREFIX, CCXBlockUsageLocator.BLOCK_PREFIX),
        "i4x://org.dept%sub-prof/course.num%section-4/category/name:12%33-44",
    )
    def test_string_roundtrip(self, url):
        actual = unicode(UsageKey.from_string(url))
        self.assertEquals(
            url,
            actual
        )

    @ddt.data(
        "ccx-block-v1:org+course+run+ccx@1+{}@category".format(CCXBlockUsageLocator.BLOCK_TYPE_PREFIX),
        "ccx-block-v1:org+course+run+{}@revision+ccx@1+{}@category".format(CourseLocator.BRANCH_PREFIX, CCXBlockUsageLocator.BLOCK_TYPE_PREFIX),
    )
    def test_missing_block_id(self, url):
        with self.assertRaises(InvalidKeyError):
            UsageKey.from_string(url)

    @ddt.data(
        ((), {
            'org': 'org',
            'course': 'course',
            'run': 'run',
            'ccx': '1',
            'category': 'category',
            'name': 'name',
        }, 'org', 'course', 'run', '1', 'category', 'name', None),
        ((), {
            'org': 'org',
            'course': 'course',
            'run': 'run',
            'ccx': '1',
            'category': 'category',
            'name': 'name:more_name',
        }, 'org', 'course', 'run', '1', 'category', 'name:more_name', None),
        ([], {}, 'org', 'course', 'run', '1', 'category', 'name', None),
    )
    @ddt.unpack
    def test_valid_locations(self, args, kwargs, org, course, run, ccx, category, name, revision):  # pylint: disable=unused-argument
        course_key = CCXLocator(org=org, course=course, run=run, branch=revision, ccx=ccx)
        locator = CCXBlockUsageLocator(course_key, block_type=category, block_id=name, )
        self.assertEquals(org, locator.org)
        self.assertEquals(course, locator.course)
        self.assertEquals(run, locator.run)
        self.assertEquals(ccx, locator.ccx)
        self.assertEquals(category, locator.block_type)
        self.assertEquals(name, locator.block_id)
        self.assertEquals(revision, locator.branch)

    @ddt.data(
        (("foo",), {}),
        (["foo", "bar"], {}),
        (["foo", "bar", "baz", "blat/blat", "foo"], {}),
        (["foo", "bar", "baz", "blat", "foo/bar"], {}),
        (["foo", "bar", "baz", "blat:blat", "foo:bar"], {}),  # ':' ok in name, not in category
        (('org', 'course', 'run', 'category', 'name with spaces', 'revision'), {}),
        (('org', 'course', 'run', 'category', 'name/with/slashes', 'revision'), {}),
        (('org', 'course', 'run', 'category', 'name', u'\xae'), {}),
        (('org', 'course', 'run', 'category', u'\xae', 'revision'), {}),
        ((), {
            'tag': 'tag',
            'course': 'course',
            'category': 'category',
            'name': 'name@more_name',
            'org': 'org'
        }),
        ((), {
            'tag': 'tag',
            'course': 'course',
            'category': 'category',
            'name': 'name ',   # extra space
            'org': 'org'
        }),
    )
    @ddt.unpack
    def test_invalid_locations(self, *args, **kwargs):
        with self.assertRaises(TypeError):
            CCXBlockUsageLocator(*args, **kwargs)



    @ddt.data(
        ('course', 'newvalue'),
        ('org', 'newvalue'),
        ('run', 'newvalue'),
        ('branch', 'newvalue'),
        ('version_guid', ObjectId('519665f6223ebd6980884f2b')),
        ('block_id', 'newvalue'),
        ('block_type', 'newvalue'),
        ('ccx', '2'),
    )
    @ddt.unpack
    def test_replacement(self, key, newvalue):
        course_key = CCXLocator('org', 'course', 'run', 'rev', ccx='1', deprecated=False)
        kwargs = {key: newvalue}
        self.assertEquals(
            getattr(CCXBlockUsageLocator(course_key, 'c', 'n', deprecated=False).replace(**kwargs), key),
            newvalue
        )

        with self.assertRaises(InvalidKeyError):
            CCXBlockUsageLocator(course_key, 'c', 'n', deprecated=True).replace(block_id=u'name\xae')

    @ddt.data(*product((True, False), repeat=2))
    @ddt.unpack
    def test_map_into_course_location(self, deprecated_source, deprecated_dest):
        original_course = CCXLocator('org', 'course', 'run', ccx='1', deprecated=deprecated_source)
        new_course = CCXLocator('edX', 'toy', '2012_Fall', ccx='1', deprecated=deprecated_dest)
        loc = CCXBlockUsageLocator(original_course, 'cat', 'name:more_name', deprecated=deprecated_source)
        expected = CCXBlockUsageLocator(new_course, 'cat', 'name:more_name', deprecated=deprecated_dest)
        actual = loc.map_into_course(new_course)

        self.assertEquals(expected, actual)

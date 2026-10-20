import copy
import unittest
from pack_metadata import validate_metadata


class MetadataTest(unittest.TestCase):
    def setUp(self):
        self.good = {"pack": {"pack_format": 75, "min_format": 75, "max_format": 75,
                              "description": "SPRMine"}}

    def test_valid_candidate(self):
        validate_metadata(self.good)

    def test_original_broken_metadata(self):
        with self.assertRaisesRegex(AssertionError, "min_format"):
            validate_metadata({"pack": {"pack_format": 75, "description": "SPRMine"}})

    def test_each_required_bound(self):
        for key in ("min_format", "max_format"):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.good)
                del bad["pack"][key]
                with self.assertRaises(AssertionError):
                    validate_metadata(bad)

    def test_bad_types_ranges_and_versions(self):
        for fields in ({"min_format": True}, {"max_format": "75"},
                       {"min_format": 76}, {"max_format": 74},
                       {"min_format": 74}, {"pack_format": 74}):
            with self.subTest(fields=fields):
                bad = copy.deepcopy(self.good)
                bad["pack"].update(fields)
                with self.assertRaises(AssertionError):
                    validate_metadata(bad)

    def test_optional_legacy_field(self):
        del self.good["pack"]["pack_format"]
        validate_metadata(self.good)


if __name__ == "__main__":
    unittest.main()

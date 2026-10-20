"""Metadata contract for the Java 1.21.11 resource-pack candidate."""


def validate_metadata(metadata):
    pack = metadata["pack"]
    # Since resource format 65 the range is mandatory, even if pack_format exists.
    for key in ("min_format", "max_format"):
        value = pack.get(key)
        assert type(value) is int, f"{key}: mandatory integer for this candidate"
    assert pack["min_format"] <= pack["max_format"], "reversed format range"
    assert pack["min_format"] == pack["max_format"] == 75, "candidate targets format 75 only"
    assert pack.get("pack_format", 75) == 75, "legacy pack_format conflicts with target"
    assert isinstance(pack.get("description"), str) and pack["description"], "missing description"


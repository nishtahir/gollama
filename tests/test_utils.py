from syrupy.assertion import SnapshotAssertion

from gollama.utils import human_readable_size


def test_human_readable_size(snapshot: SnapshotAssertion):
    snapshot.assert_match(human_readable_size(1024))
    snapshot.assert_match(human_readable_size(1024 * 1024))
    snapshot.assert_match(human_readable_size(1024 * 1024 * 1024))
    snapshot.assert_match(human_readable_size(1024 * 1024 * 1024 * 1024))


import pytest
from ..helpers import *

# Test for is_valid_link
@pytest.mark.parametrize("link, expected", [
    # insights.gg
    ("https://insights.gg/video/69kJcnA5XkmYDeE2teUPC3/replay", False),
    ("https://insights.gg/dashboard/69kJcnA5XkmYDeE2teUPC3/replay", False),
    ("https://insights.gg/dashboard/69kJcnA5XkmYDeE2teUPC3", False),
    ("https://insights.gg/dashboard/video/69kJcnA5XkmYDeE2teUPC3/replay", True),
    ("https://insights.gg/dashboard/video/69kJcnA5XkmYDeE2teUPC3", True),

    # twitch.tv
    ("https://www.twitch.tv/1912936673", False),
    ("https://www.twitch.tv/videos/1912936673", True),
    ("https://twitch.tv/videos/1912936673", True),
    ("https://www.twitch.tv/videos/1930381469?t=0h14m43s",True),

    # youtu.be
    ("https://www.youtu.be/sKpP5STqZXY", False),
    ("https://youtu.be/v=sKpP5STqZXY", False),
    ("https://www.youtu.be/watch?v=sKpP5STqZXY", False),
    ("https://youtu.be/sKpP5STqZXY", True),
    ("https://youtu.be/watch?v=sKpP5STqZXY", True),
    ("https://youtu.be/Gc6gtCvWUAA?si=SZ6fKP8NI3B9uvqk", True),

    # youtube.com
    ("https://www.youtube.com/v=--fwVoTCX84", False),
    ("https://www.youtube.com/--fwVoTCX84", False),
    ("https://www.youtube.com/watch?v=sKpP5STqZXY", True),
    ("https://youtube.com/watch?v=sKpP5STqZXY", True),
    ("https://www.youtube.com/live/--fwVoTCX84", True),
    ("https://youtube.com/live/--fwVoTCX84", True),
    ("https://www.youtube.com/watch?v=iiBxnC9d9ds&ab", True),
    ("https://www.youtube.com/watch?v=iiBxnC9d9ds&ab_channel=Tr%E1%BA%A7nQuangAnh", True)
])


def test_is_valid_link(link, expected):
    assert is_valid_link(link) == expected

# Test for is_valid_town
@pytest.mark.parametrize("town, expected", [
    ("brightwood", True),
    ("brimstone sands", True),
    ("cutlass keys", True),
    ("ebonscale reach", True),
    ("everfall", True),
    ("monarch’s bluffs", True),
    ("mourningdale", True),
    ("reekwater", True),
    ("restless shore", True),
    ("weaver’s fen", True),
    ("windsward", True),
    ("bw", True),
    ("bs", True),
    ("brim", True),
    ("ck", True),
    ("cutless", True),
    ("ebon", True),
    ("ef", True),
    ("mb", True),
    ("monarchs", True),
    ("md", True),
    ("rw", True),
    ("reek", True),
    ("rs", True),
    ("restless", True),
    ("wf", True),
    ("weavers", True),
    ("ww", True),
    ("winny", True),
    ("winnie", True),
    ("12345", False),
    ("",False)
])

def test_is_valid_town(town, expected):
    assert is_valid_town(town) == expected

# Test for is_valid_role
@pytest.mark.parametrize("role, expected", [
    ("Bruiser", True),
    ("mage", True),
    ("", False),
])
def test_is_valid_role(role, expected):
    assert is_valid_role(role) == expected

# Test for parse_date
@pytest.mark.parametrize("date_str, expected", [
    ("2023-08-16", "2023-08-16T00:00:00.000000Z"),
    ("2023/08/16", "2023-08-16T00:00:00.000000Z"),
    ("2023-08-16 14:30", "2023-08-16T14:30:00.000000Z"),
    ("2023/08/16 14:30", "2023-08-16T14:30:00.000000Z"),
    ("", ""),
])
def test_parse_date(date_str, expected):
    assert parse_date(date_str) == expected

# Test for split_into_chunks
@pytest.mark.parametrize("text, chunk_size, expected", [
    ("abcdef", 2, ["ab", "cd", "ef"]),
    ("", 2, []),
])
def test_split_into_chunks(text, chunk_size, expected):
    assert split_into_chunks(text, chunk_size) == expected

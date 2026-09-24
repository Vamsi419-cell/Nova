from nova.tools.caliculator import caliculator
def test_caliculator():
    result = caliculator("10 *900")
    assert result == 9000


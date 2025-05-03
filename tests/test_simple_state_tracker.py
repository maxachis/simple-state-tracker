import pytest

from simple_state_tracker.data_model import DataModel
from simple_state_tracker.key_model import KeyModel
from simple_state_tracker.simple_state_tracker import SimpleStateTracker


class MyKey(KeyModel):
    a: str
    b: int

class MyState(DataModel):
    value: str = ""
    flag: bool = False

@pytest.fixture
def tmp_tracker(tmp_path) -> SimpleStateTracker[MyKey, MyState]:
    path = tmp_path / "tracker.json"
    return SimpleStateTracker(MyKey, MyState, path=str(path))

def test_set_and_get(tmp_tracker):
    key = MyKey(a="foo", b=1)
    state = MyState(value="bar", flag=True)

    tmp_tracker.set(key, state)
    retrieved = tmp_tracker.get(key)

    assert retrieved == state

def test_edit_context_manager(tmp_tracker):
    key = MyKey(a="edit", b=2)

    with tmp_tracker.edit(key) as state:
        state.value = "changed"
        state.flag = True

    assert tmp_tracker.get(key) == MyState(value="changed", flag=True)

def test_save_and_load(tmp_tracker):
    key = MyKey(a="save", b=3)
    state = MyState(value="persist", flag=True)
    tmp_tracker.set(key, state)

    tmp_tracker.save()

    # Create a new tracker that loads from the same file
    new_tracker = SimpleStateTracker(MyKey, MyState, path=str(tmp_tracker.path))
    assert new_tracker.get(key) == state

def test_key_str_and_from_str():
    key = MyKey(a="foo", b=10)
    s = str(key)
    parsed = MyKey.from_str(s)

    assert parsed == key

def test_all_returns_copy(tmp_tracker):  #
    key = MyKey(a="copy", b=99)
    tmp_tracker.set(key, MyState(value="x"))
    all_data = tmp_tracker.all()

    assert isinstance(all_data, dict)
    assert key in all_data
    assert all_data[key].value == "x"

    all_data[key].value = "changed"
    # Ensure internal state is unchanged
    assert tmp_tracker.get(key).value == "x"

def test_invalid_key_model_type():
    with pytest.raises(TypeError):
        SimpleStateTracker(MyKey(a="foo", b=10), MyState, "fake_path.json")  # Instance, not class

class NotADataModel:
    ...

def test_invalid_data_model_class():
    with pytest.raises(TypeError):
        SimpleStateTracker(MyKey, NotADataModel, "fake_path.json")


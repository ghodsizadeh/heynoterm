import json
from pathlib import Path
import pytest
from heynoterm.state import Block, AppState, DataManager


@pytest.fixture(scope="function")
def data_path() -> Path:
    # create a data.json file and delete it after the test
    path = Path(__file__).parent / "data.json"
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def data_manager(data_path) -> DataManager:
    return DataManager(path=data_path)


def test_block_to_json(data_manager):
    block = Block(text="Hello", language="python")
    assert block.text == "Hello"
    assert block.language == "python"


def test_app_state_to_json():
    app_state = AppState(blocks=[Block(text="Hello", language="python")])
    # convert to json
    json_data = app_state.to_json()
    # expected json
    expected_dict = {"blocks": [{"text": "Hello", "language": "python"}]}
    # convert expected json to string
    expected_json = json.dumps(expected_dict, indent=4)
    # assert json data is equal to expected json
    assert json_data == expected_json


def test_app_state_from_json():
    app_state = AppState.from_json(
        '{"blocks": [{"text": "Hello", "language": "python"}]}'
    )
    assert len(app_state.blocks) == 1
    assert app_state.blocks[0].text == "Hello"
    assert app_state.blocks[0].language == "python"


def test_data_manager_load(data_manager: DataManager, data_path: Path):
    data_path.write_text('{"blocks": [{"text": "Hello", "language": "python"}]}')
    data_manager.load()
    state = data_manager.state
    assert len(state.blocks) == 1
    assert state.blocks[0].text == "Hello"
    assert state.blocks[0].language == "python"


def test_data_manager_save(data_manager: DataManager, data_path: Path):
    data_manager.add_block(Block(text="Hello", language="python"))
    data_manager.save()
    assert data_path.exists()
    assert json.loads(data_path.read_text()) == {
        "blocks": [{"text": "Hello", "language": "python"}]
    }


def test_data_manager_add_block(data_manager: DataManager):
    block = Block(text="Hello", language="python")
    data_manager.add_block(block)
    assert len(data_manager.state.blocks) == 1
    assert data_manager.state.blocks[0] == block


def test_data_manager_remove_block(data_manager: DataManager):
    block = Block(text="Hello", language="python")
    data_manager.add_block(block)
    data_manager.remove_block(0)
    assert len(data_manager.state.blocks) == 0


def test_data_manager_update_block(data_manager: DataManager):
    block = Block(text="Hello", language="python")
    data_manager.add_block(block)
    updated_block = Block(text="Hi", language="python")
    data_manager.update_block(0, updated_block)
    assert len(data_manager.state.blocks) == 1
    assert data_manager.state.blocks[0] == updated_block

import tempfile
import json
from pathlib import Path
import pytest
from number_guessing_game.score import TopScoreList
from number_guessing_game.config import DIFFICULTY


@pytest.fixture
def temp_score_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        file = Path(tmpdir) / "scores.json"
        # 初始化空分数文件
        file.write_text(json.dumps({level: [] for level, _ in DIFFICULTY}), encoding="utf-8")
        yield file


def test_init_and_load_scores(temp_score_file):
    top_list = TopScoreList(5, temp_score_file)
    top_list.load_scores()
    for level, _ in DIFFICULTY:
        assert level in top_list._TopScoreList__scores
        assert isinstance(top_list._TopScoreList__scores[level], type(top_list._TopScoreList__scores[level]))


def test_save_and_load_scores(temp_score_file):
    top_list = TopScoreList(3, temp_score_file)
    top_list.load_scores()
    top_list._TopScoreList__scores[DIFFICULTY[0][0]].append((1, 1.23, "Alice"))
    top_list.save_scores()
    # 重新加载
    top_list2 = TopScoreList(3, temp_score_file)
    top_list2.load_scores()
    assert top_list2._TopScoreList__scores[DIFFICULTY[0][0]][0] == (1, 1.23, "Alice")


def test_ranking_empty(temp_score_file):
    top_list = TopScoreList(2, temp_score_file)
    top_list.load_scores()
    rank = top_list.ranking((1, 1.0), DIFFICULTY[0][0])
    assert rank == 1


def test_ranking_full_and_not_qualified(temp_score_file):
    top_list = TopScoreList(2, temp_score_file)
    top_list.load_scores()
    level = DIFFICULTY[0][0]
    top_list._TopScoreList__scores[level].extend([(1, 1.0, "A"), (2, 2.0, "B")])
    # 分数比最后一个还差
    assert top_list.ranking((2, 2.0), level) is None


def test_ranking_insert_middle(temp_score_file):
    top_list = TopScoreList(3, temp_score_file)
    top_list.load_scores()
    level = DIFFICULTY[0][0]
    top_list._TopScoreList__scores[level].extend([(1, 1.0, "A"), (3, 3.0, "B")])
    # 新分数介于两者之间
    assert top_list.ranking((2, 2.0), level) == 2


def test_update_scores(temp_score_file):
    top_list = TopScoreList(3, temp_score_file)
    top_list.load_scores()
    level = DIFFICULTY[0][0]
    top_list.update_scores(1, (1, 1.0), "Alice", level)
    assert top_list._TopScoreList__scores[level][0] == (1, 1.0, "Alice")


def test_clear(temp_score_file):
    top_list = TopScoreList(3, temp_score_file)
    top_list.load_scores()
    level = DIFFICULTY[0][0]
    top_list._TopScoreList__scores[level].append((1, 1.0, "A"))
    top_list.clear()
    assert len(top_list._TopScoreList__scores[level]) == 0


def test_context_manager(temp_score_file):
    with TopScoreList(3, temp_score_file) as top_list:
        level = DIFFICULTY[0][0]
        top_list.update_scores(1, (1, 1.0), "Alice", level)
    # 检查文件已保存
    with open(temp_score_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data[level][0][:2] == [1, 1.0]

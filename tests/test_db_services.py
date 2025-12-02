def test_start_finish_and_get_quiz_session(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    user_id = db.create_user("session_user", "pwd")

    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=2)
    assert session_id

    session = db_services.get_quiz_session(session_id)
    assert session["total_questions"] == 2

    db_services.finish_quiz_session(session_id, 75, 2)
    finished = db_services.get_quiz_session(session_id)
    assert finished["score"] == 75


def test_start_quiz_session_requires_ids(test_env):
    db_services = test_env["db_services"]
    try:
        db_services.start_quiz_session(0, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for missing user id")

    try:
        db_services.start_quiz_session(1, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for missing skill test id")


def test_record_user_answer_and_queries(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    user_id = db.create_user("answer_user", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=2)
    first_q, second_q = test_env["question_ids"]

    db_services.record_user_answer(session_id, first_q, "A", True)
    db_services.record_user_answer(session_id, second_q, "no", False)

    correct = db_services.get_correct_answers(session_id)
    incorrect = db_services.get_incorrect_answers(session_id)
    assert len(correct) == 1 and correct[0]["question_id"] == first_q
    assert len(incorrect) == 1 and incorrect[0]["question_id"] == second_q

    all_answers = db_services.get_all_answers_with_questions(session_id)
    assert {answer["question_id"] for answer in all_answers} == {first_q, second_q}
    assert all_answers[0]["prompt"]


def test_get_skill_tests_questions_and_study_guides(test_env):
    db_services = test_env["db_services"]

    skill_tests = db_services.list_skill_tests()
    assert any(test["id"] == test_env["skill_test_id"] for test in skill_tests)

    questions = db_services.get_skill_test_questions(test_env["skill_test_id"], limit=5)
    assert len(questions) >= 2

    guides = db_services.get_study_guide_by_skill_test(test_env["skill_test_id"])
    assert len(guides) >= 2


def test_get_leaderboard_by_skill_test(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    user_id = db.create_user("leader_user", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=1)

    with db.get_db_connection() as conn:
        conn.execute("UPDATE quiz_results SET start_time = DATETIME('now', '-1 day') WHERE id = ?", (session_id,))
        conn.commit()

    db_services.finish_quiz_session(session_id, 100, 1)

    leaderboard = db_services.get_leaderboard_by_skill_test(test_env["skill_test_id"], limit=5)
    assert leaderboard
    assert leaderboard[0]["username"] == "leader_user"
    assert leaderboard[0]["score"] == 100


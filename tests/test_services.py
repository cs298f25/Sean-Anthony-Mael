def test_start_quiz_service_parses_choices(test_env):
    services = test_env["services"]
    db = test_env["db"]
    db.create_user("quiz_user", "pwd")
    result = services.start_quiz_service("quiz_user", test_env["skill_test_id"])

    assert result["session_id"]
    mc_question = next(q for q in result["questions"] if q["question_type"] == "multiple_choice")
    assert isinstance(mc_question["choices"], list)
    assert mc_question["choices"] == ["A", "B"]


def test_submit_answer_service_updates_stats(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    services = test_env["services"]
    user_id = db.create_user("answer_user", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=2)
    question_id = test_env["question_ids"][0]

    assert services.submit_answer_service(session_id, question_id, " a ", "A", "multiple_choice")

    with db.get_db_connection() as conn:
        row = conn.execute(
            "SELECT correct_answers, incorrect_answers FROM questions WHERE id = ?", (question_id,)
        ).fetchone()
    assert row["correct_answers"] == 1
    assert row["incorrect_answers"] == 0


def test_finish_quiz_service_scores_results(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    services = test_env["services"]
    user_id = db.create_user("finisher", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=2)
    first_q, second_q = test_env["question_ids"]

    db_services.record_user_answer(session_id, first_q, "A", True)
    db_services.record_user_answer(session_id, second_q, "no", False)

    result = services.finish_quiz_service(session_id)
    assert result["correct_count"] == 1
    assert result["incorrect_count"] == 1
    assert result["score"] == 50

    persisted = db_services.get_quiz_session(session_id)
    assert persisted["score"] == 50


def test_finish_quiz_service_handles_no_answers(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    services = test_env["services"]
    user_id = db.create_user("empty", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=1)

    assert services.finish_quiz_service(session_id) is None


def test_get_quiz_data_and_answers_services(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    services = test_env["services"]
    user_id = db.create_user("viewer", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=2)
    first_q = test_env["question_ids"][0]
    db_services.record_user_answer(session_id, first_q, "A", True)

    quiz_data = services.get_quiz_data_service(session_id)
    assert quiz_data["id"] == session_id

    answers = services.get_all_answers_with_questions_service(session_id)
    assert answers[0]["question_id"] == first_q
    assert answers[0]["is_correct"] == 1


def test_study_guide_and_leaderboard_services(test_env):
    db = test_env["db"]
    db_services = test_env["db_services"]
    services = test_env["services"]
    user_id = db.create_user("boarduser", "pwd")
    session_id = db_services.start_quiz_session(user_id, test_env["skill_test_id"], total_questions=1)

    with db.get_db_connection() as conn:
        conn.execute("UPDATE quiz_results SET start_time = DATETIME('now', '-1 day') WHERE id = ?", (session_id,))
        conn.commit()

    db_services.finish_quiz_session(session_id, 100, 1)

    study_guides = services.get_study_guide_service(test_env["skill_test_id"])
    assert len(study_guides) >= 2

    leaderboard = services.get_leaderboard_service(test_env["skill_test_id"])
    assert leaderboard[0]["username"] == "boarduser"

import psycopg2


def connection_to_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="yfhmzy03",
        dbname="oprosy"
    )
    return conn


def create_tables() -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
    	    user_id BIGINT PRIMARY KEY,
    	    user_name VARCHAR
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
    	    id BIGSERIAL PRIMARY KEY,
    	    question_text VARCHAR,
    	    publish_date TIME WITHOUT TIME ZONE,
    	    admin_id BIGINT,
    	    FOREIGN KEY (admin_id) REFERENCES admins (user_id)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS choices (
    	    id BIGSERIAL PRIMARY KEY,
    	    text VARCHAR,
    	    votes BIGINT,
    	    question_id BIGINT,
    	    FOREIGN KEY (question_id) REFERENCES questions (id)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_statistic (
    	    id BIGSERIAL PRIMARY KEY,
    	    user_id BIGINT,
    	    question_id BIGINT,
    	    choice_id BIGINT,
    	    FOREIGN KEY (question_id) REFERENCES questions (id),
    	    FOREIGN KEY (choice_id) REFERENCES choices (id)
        );""")
    conn.commit()
    conn.close()


def poisk_quest(id) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM questions WHERE id = (%s)", (id, ))
        result = cursor.fetchall()
    return result


def prov_admin(user_id: int) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM admins WHERE user_id = (%s);", (user_id, ))
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def save_question(s: str, admin_id, date) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO questions (question_text, admin_id, publish_date) "
                       "VALUES ((%s), (%s), (%s));", (s, admin_id, date))
    conn.commit()
    conn.close()


def save_variants(s: str, admin_id) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT max(id) from questions WHERE admin_id = (%s);", (admin_id, ))
        result = cursor.fetchone()
    question_id = result[0]
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO choices (text, votes, question_id) VALUES ((%s), (%s), (%s))", (s, 0, question_id))
    conn.commit()
    conn.close()


def delete_question(question_id) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM total_statistic WHERE question_id = (%s)", (question_id, ))
        cursor.execute("DELETE FROM choices WHERE question_id = (%s)", (question_id, ))
        cursor.execute("DELETE FROM questions WHERE id = (%s)", (question_id, ))
    conn.commit()
    conn.close()


def get_my_statistic(user_id):
    conn = connection_to_db()
    res, res1 = [], []
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_id, choice_id FROM total_statistic WHERE user_id = (%s)", (user_id, ))
        result = cursor.fetchall()
    with conn.cursor() as cursor:
        for x in result:
            cursor.execute("SELECT question_text FROM questions WHERE id = (%s)", (x[0], ))
            res.extend(cursor.fetchall())
    with conn.cursor() as cursor:
        for x in result:
            cursor.execute("SELECT text FROM choices WHERE id = (%s)", (x[1], ))
            res1.extend(cursor.fetchall())
    conn.commit()
    conn.close()
    return res, res1


def total_statistic():
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, question_text FROM questions")
        all_questions = cursor.fetchall()
    with conn.cursor() as cursor:
        cursor.execute("SELECT questions.id, choices.text, choices.votes FROM choices "
                       "Inner JOIN questions ON choices.question_id = questions.id;")
        votes = cursor.fetchall()
    conn.commit()
    conn.close()
    return all_questions, votes


def get_questions(user_id) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM questions")
        all_questions = cursor.fetchall()
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_id FROM total_statistic WHERE user_id = (%s)", (user_id, ))
        answer_q = cursor.fetchall()
    result = set(all_questions) - set(answer_q)
    result = list(result)
    conn.commit()
    conn.close()
    return result


def get_question(question_id) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_text FROM questions WHERE id = (%s)", (question_id, ))
        result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def get_variants(question_id) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT text, id FROM choices WHERE question_id = (%s);", (question_id, ))
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def update_votes(choice_id) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE choices SET votes = votes + 1 WHERE id = (%s)", (choice_id, ))
    conn.commit()
    conn.close()


def update_statistic(choice_id, user_id) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_id FROM choices WHERE id = (%s)", (choice_id, ))
        question_id = cursor.fetchone()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO total_statistic (user_id, question_id, choice_id) "
                       "VALUES ((%s), (%s), (%s))", (user_id, question_id[0], choice_id))
    conn.commit()
    conn.close()


# if __name__ == "__main__":
#     pass

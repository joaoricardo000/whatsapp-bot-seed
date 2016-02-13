import config, random
from utils.session import SessionDB
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

"""
    In this Views All methods will have access to a map like object, called session_db, to store some history from users.
    session_db is a Object from SessionDB, check there for more info!
"""


class QuizView:
    def __init__(self, interface_layer):
        self.interface_layer = interface_layer
        self.session_db = SessionDB(config.session_db_path, "quiz")

        # One route to start a new quiz, one to answer.
        self.routes = [
            ("^/quiz\s?$", self.quiz),
            (r"^(?P<quiz_answer>\d{1})\s?$", self.quiz_answer),  # 0-9
        ]

    def quiz(self, message, match):
        # Gets a random quiz and store in the sender' session
        quiz = self._get_quiz()
        self.session_db.set(message.getFrom(), quiz)
        return TextMessageProtocolEntity(self._get_quiz_text(quiz), to=message.getFrom())

    def quiz_answer(self, message, match):
        # if there is a quiz stored on the sender' session, this is an answer, otherwise ignore it
        quiz = self.session_db.get(message.getFrom())
        if quiz:
            self.session_db.set(message.getFrom(), None)
            ans = int(match.group("quiz_answer"))
            if ans == quiz["correct_alternative"]:
                return TextMessageProtocolEntity("Correct!", to=message.getFrom())
            else:
                msg_wrong = "Wrong. Correct answer was: %s" % quiz["correct"]
                return TextMessageProtocolEntity(msg_wrong, to=message.getFrom())

    def _get_quiz_text(self, quiz):
        ans = "\n".join(["(%s) %s" % (k, v) for k, v in quiz["alternatives"].iteritems()])
        return "\n".join([quiz["question"], ans])

    def _get_quiz(self):
        """
        Returns a random quiz like this:
        {
            "question":"How much is 1 + 2 + 3?",
           "alternatives": {
               1:6,
               2:3,
               3:"potato",
               ...
               "d":7
           },
            "correct_alternative": 1
        }
        """
        values = random.sample(range(1, 100), random.randint(2, 5))
        sum_values = sum(values)
        ans = [sum_values + int(random.uniform(-20, 20)) for i in range(3)]
        ans.append(sum_values)
        random.shuffle(ans)

        alternatives = {}
        for i, a in enumerate(ans):
            alternatives[i + 1] = a
        correct_alternative = ans.index(sum_values) + 1

        return {
            "question": "How much is %s?" % " + ".join(str(v) for v in values),
            "alternatives": alternatives,
            "correct_alternative": correct_alternative
        }

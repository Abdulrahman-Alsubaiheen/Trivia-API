import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'd7oom11','localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'do you love me ?',
            'answer': 'noo',
            'category': 1,
            'difficulty': 1
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #________________________________________________________________#

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    #________________________________________________________________#

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    #________________________________________________________________#

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=9557')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #________________________________________________________________#

    def test_delete_questions(self): 
        res = self.client().delete('/questions/1') # must change the id every time i runing the test
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
        
    #________________________________________________________________#

    def test_422_delete_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    #________________________________________________________________#

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question) # json=self.new_question ( that i create up in the setup )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    #________________________________________________________________#

    def test_405_if_question_creation_fails(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    #________________________________________________________________#

    def test_search_for_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'you'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    #________________________________________________________________#

    # def test_get_questions_by_category(self):
    #     res = self.client().get('/categories/1/questions')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['currentCategory'], 1)
    #     self.assertTrue(data['total_questions'])
    #     self.assertTrue(len(data['questions']))
        
    #________________________________________________________________#

    # def test_get_questions_by_not_exist_category(self):
    #     res = self.client().get('/categories/4325/questions')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'resource not found')

    #________________________________________________________________#

    def test_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions":[],"quiz_category":{"type":"Sport","id":"1"}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    #________________________________________________________________#

    def test_404_quiz_by_not_exist_category(self):
        res = self.client().post('/quizzes', json={"previous_questions":[],"quiz_category":{"type":"funny","id":"456"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #________________________________________________________________#

# # Run the test suite, by running python <test_file_name>.py in the command line.

    #________________________________________________________________#



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

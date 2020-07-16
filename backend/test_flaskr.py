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
        self.database_path = "postgres://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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


    # ------------------------------------
    # getting all categories test
    # ------------------------------------

    def test_get_categories(self):
        response = self.client().get("/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']),6)



    # ------------------------------------
    # get questions test
    # ------------------------------------

    def test_get_questions(self):
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']),10) # first page
        
    def test_get_questions_pagination(self):
        response = self.client().get("/questions?page=2")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']),9) # second page

    
    def test_get_questions_notFoundPage(self):
        response = self.client().get("/questions?page=123")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertFalse(data['questions'])
        




    # ------------------------------------
    # create questions
    # ------------------------------------

    def test_create_questions_valid(self):
        new_question = { # id = 20
            "question" : "test_question",
            "answer" : "test_answer",
            "difficulty" : 3,
            'category':1
        }

        response = self.client().post("/questions",json=new_question)
        data = json.loads(response.data)
        

        self.assertEqual(response.status_code,201)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['message'],"question created successfully")
        


        # make sure the question is added in the database
        question = Question.query.order_by(Question.id).all()[-1]
        self.assertEqual(question.question,new_question['question'])
        self.assertEqual(question.answer,new_question['answer'])
        self.assertEqual(question.difficulty,new_question['difficulty'])
        self.assertEqual(question.category,new_question['category'])






    def test_create_questions_CategoryNotExists(self):
        new_question = { 
            "question" : "test_question",
            "answer" : "test_answer",
            "difficulty" : 3,
            'category':12
        }

        response = self.client().post("/questions",json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"category not found")
        


    def test_create_questions_BadFormat(self):
        new_question = { 
            "fwffw" : "test_question",
            "answer" : "test_answer",
            "difficulty" : 3,
            'category':2
        }

        response = self.client().post("/questions",json=new_question)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"can't process the request")














    # ------------------------------------
    # search questions
    # ------------------------------------

    def test_search_question_valid(self):
        search_for = { 
            "searchTerm" : "what",
        }

        response = self.client().post("/questions/search",json=search_for)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])


    def test_search_question_empty(self):
        search_for = { 
            "searchTerm" : "fasfasfsafasfasfasfwfqrijsigjsdifj",
        }

        response = self.client().post("/questions/search",json=search_for)
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertFalse(data['questions'])


    def test_search_questions_BadFormat(self):
        search_for = { 
            "search_term" : "what", # search_term instead of searchTerm
        }

        response = self.client().post("/questions/search",json=search_for)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"can't process the request")






    # ------------------------------------
    # get all questions in one category
    # ------------------------------------

    def test_get_category_questions_valid(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'],'Science')
        

    def test_get_category_questions_notFoundCategory(self):
        response = self.client().get("/categories/62/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)






    # ------------------------------------
    # Quiz
    # ------------------------------------

    def test_get_quizzes_all(self):

        request = { 
            'quiz_category': { 'id': 1, 'type': 'Science'},
            'previous_questions': []
        }

        response = self.client().post("/quizzes",json=request)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])


    def test_get_quizzes_science(self):
        
        request = { 
            'quiz_category': { 'id': 0, 'type': 'Click'},
            'previous_questions': []
        }

        response = self.client().post("/quizzes",json=request)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])



    def test_get_quizzes_badFormat(self):
        
        request = { 
            "previous_questions" : [], 
            "quiz_category" : {'type':"click","q":0} # q instead of id
        }

        response = self.client().post("/quizzes",json=request)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"can't process the request")





    # ------------------------------------
    # delete Question test
    # ------------------------------------

    def test_delete_question_exists(self):
        delete_id = 2 # must be changed after each test
        question = Question.query.get(delete_id)
        self.assertTrue(question)

        response = self.client().delete(f"/questions/{delete_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['message'],"deleted successfully")

        question = Question.query.get(delete_id)
        self.assertFalse(question)


    def test_delete_question_notfound(self):
        delete_id = 329125  

        response = self.client().delete(f"/questions/{delete_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)









# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from  sqlalchemy.sql.expression import func



QUESTIONS_PER_PAGE = 10



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  db = setup_db(app)
  CORS(app)


  @app.route('/')
  def test():
    new_questions = [category.format() for category in Category.query.all()]
    return jsonify(new_questions)





  # after request
  # ----------------

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return response





  # get all categories 
  # ---------------------------------------

  @app.route('/categories',methods=['GET'])
  def get_categories():
    all_categories = [category.format() for category in Category.query.all()]

    return jsonify({
          'success': True,
          'categories': all_categories,
        })



  
  # get all question 
  # ---------------------------------------

  @app.route('/questions',methods=['GET'])
  def get_questions():
    page = int(request.args.get('page',1))
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    all_questions  = Question.query.order_by('id').all()
    current_questions = [question.format() for question in all_questions[start:end]]
    all_categories = [category.format() for category in Category.query.all()]

    return jsonify(

    { 
      "success":True,
      "total_questions":len(all_questions),
      "categories":all_categories ,
      "current_category":"", # current_category="" becuase this is all questions from all categories 
      "questions":current_questions
    }
    ),200

  

  # Delete Questions With id
  #------------------------------

  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):
    
    # raise 404 error if question not found
    question = Question.query.get_or_404(id).delete()
    return jsonify({
      "success":True,
      'message':"deleted successfully"
    }),200
  

  # create new Question
  # -------------------------------

  @app.route('/questions',methods=['POST'])
  def create_questions():
    


    json_data = request.get_json()


    question = json_data.get("question","")
    answer = json_data.get("answer","")
    difficulty = json_data.get("difficulty","")
    category = json_data.get("category","")

    if(not(category and answer and difficulty and question)):
      abort(422,"can't process the request")
    

    # next line only used to raise 404 if category not exists 
    cat = Category.query.get(category)
    if(not cat):
      abort(404,"category not found")

    Question(question,answer,category,difficulty).save()



    return jsonify({
      "success":True,
      "message":"question created successfully"
    }),201




  # search for question
  # -------------------------------
  @app.route('/questions/search',methods=['POST'])
  def search_question():

    search_term = request.get_json().get('searchTerm', "")
    if(not search_term):
      abort(422,"can't process the request")
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    
    # current_page = int( request.args.get('page',1))
    # start = (current_page-1) * QUESTIONS_PER_PAGE 
    # end   = start + QUESTIONS_PER_PAGE

    return jsonify({
      "questions":[question.format() for question in questions ],
      "totalQuestions":len(questions),
      "currentCategory":"",
      'success':True
    })

  

  # get question by category
  # -------------------------------

  @app.route('/categories/<int:id>/questions')
  def get_category_questions(id):
    
    category = Category.query.get_or_404(id)

    questions = Question.query.filter(Question.category==id).all()
    questions = [ question.format() for question in questions ]

    return jsonify({
      "questions":questions,
      "totalQuestions":len(questions),
      "current_category":category.type,
      'success':True,
    })



  # get question for the quiz 
  # -------------------------------

  @app.route('/quizzes',methods=['POST'])
  def get_quizzes():
    json_data = request.get_json()
    previous_questions = json_data.get('previous_questions',"")
    quiz_category = json_data.get('quiz_category').get("id","")


    if(type(previous_questions)!=list or quiz_category==""):
      abort(422,"can't process the request")
    
    question = Question.query.filter(Question.id.notin_(previous_questions))

    
    if(quiz_category!=0):
      question = question.filter(Question.category==quiz_category)
    
    question = question.order_by(func.random()).first()
      
    
    
    quiz_category
    return jsonify({
      "success":True,
      "question":question.format() if question else None
    }),200






  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "message": error.description if error.description else "Not Found"
    }),404

  @app.errorhandler(422)
  def not_processable(error):
    return jsonify({
      "success": False,
      "message": error.description if error.description else "Not processable"
    }), 422

  @app.errorhandler(500)
  def internal_error(error):
    return jsonify({
      "success": False,
      "message": error.description if error.description else "Internal server error"
    }), 500

    







 










  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app



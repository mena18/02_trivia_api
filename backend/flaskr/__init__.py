import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from sqlalchemy.sql.expression import func


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    CORS(app)

    # after request
    # ----------------

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # get all categories
    # ---------------------------------------

    @app.route('/categories', methods=['GET'])
    def get_categories():
        all_categories = [category.format()
                          for category in Category.query.all()]

        return jsonify({
            'success': True,
            'categories': all_categories,
        })

    # get all question
    # ---------------------------------------

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = int(request.args.get('page', 1))
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        all_questions = Question.query.order_by('id').all()
        current_questions = [question.format()
                             for question in all_questions[start:end]]
        all_categories = [category.format()
                          for category in Category.query.all()]

        return jsonify(

            {
                "success": True,
                "total_questions": len(all_questions),
                "categories": all_categories,
                # current_category="" becuase this is all questions from all
                # categories
                "current_category": "",
                "questions": current_questions
            }
        ), 200

    # Delete Questions With id
    # ------------------------------

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        question = Question.query.get(id)
        if(question):
            question.delete()
        else:
            abort(404, "Question not found")

        return jsonify({
            "success": True,
            'message': "deleted successfully"
        }), 200

    # create new Question
    # -------------------------------

    @app.route('/questions', methods=['POST'])
    def create_questions():

        json_data = request.get_json()

        question = json_data.get("question", "")
        answer = json_data.get("answer", "")
        difficulty = json_data.get("difficulty", "")
        category = json_data.get("category", "")

        # raise 404 if any field  was empty  because we can't process the
        # requests
        if(not(category and answer and difficulty and question)):
            abort(422, "can't process the request")

        # raise 404 if category dosen't exists
        cat = Category.query.get(category)
        if(not cat):
            abort(404, "category not found")

        Question(question, answer, category, difficulty).save()

        return jsonify({
            "success": True,
            "message": "question created successfully"
        }), 201

    # search for question
    # -------------------------------

    @app.route('/questions/search', methods=['POST'])
    def search_question():

        search_term = request.get_json().get('searchTerm', "")
        if(not search_term):
            abort(422, "can't process the request")

        # case sensitive search for  questions
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        return jsonify({
            "questions": [question.format() for question in questions],
            "totalQuestions": len(questions),
            "currentCategory": "",
            'success': True
        })

    # get question by category
    # -------------------------------

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_category_questions(id):

        # get the category or raise 404 error if the category not found
        category = Category.query.get_or_404(id)

        questions = Question.query.filter(Question.category == id).all()
        questions = [question.format() for question in questions]

        return jsonify({
            "questions": questions,
            "totalQuestions": len(questions),
            "current_category": category.type,
            'success': True,
        })

    # get question for the quiz
    # -------------------------------

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        json_data = request.get_json()
        previous_questions = json_data.get('previous_questions', "")
        quiz_category = json_data.get('quiz_category').get("id", "")

        # if can't process the request raise 422 error
        if(not isinstance(previous_questions, list) or quiz_category == ""):
            abort(422, "can't process the request")

        # getting all questinos excluding the questions already exists in
        # previous_questions
        question = Question.query.filter(
            Question.id.notin_(previous_questions))

        # if category !=0 then request choose one category so we get the
        # question from that category
        if(quiz_category != 0):
            question = question.filter(Question.category == quiz_category)

        # ordering the question randomly to get new question each time and get
        # only the first one
        question = question.order_by(func.random()).first()

        quiz_category
        return jsonify({
            "success": True,
            "question": question.format() if question else None
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": error.description if error.description else "Not Found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "method not allowed"
        }), 405

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

    return app

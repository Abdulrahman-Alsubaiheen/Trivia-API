import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Helper method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def paginate_questions(request, all_questions):
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [Question.format() for Question in all_questions]
    questions_in_page = questions[start:end]

    return questions_in_page


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Start from here ~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ endpoints ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/categories', methods=['GET'])
    def retrive_categories():
        all_categories = Category.query.order_by(Category.id).all()

        categories = {
            category.id: category.type for category in all_categories}
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories,
        })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/questions', methods=['GET'])
    def retrive_questions():

        all_questions = Question.query.order_by(Question.id).all()
        questions_in_page = paginate_questions(request, all_questions)

        if len(questions_in_page) == 0:
            abort(404)

        all_categories = Category.query.order_by(Category.id).all()
        categories = {
            category.id: category.type for category in all_categories}

        return jsonify({
            'success': True,
            'questions': questions_in_page,
            'total_questions': len(all_questions),
            'categories': categories,
            'currentCategory': None
        })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
            })

        except BaseException:
            abort(422)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/questions', methods=['POST'])
    def create_and_search_question():

        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        searchTerm = body.get('searchTerm', None)

        try:

            if searchTerm:

                results = Question.query.filter(
                    Question.question.ilike(
                        '%{}%'.format(searchTerm)))
                questions_in_page = paginate_questions(request, results)

                return jsonify({
                    'success': True,
                    'questions': questions_in_page,
                    'total_questions': len(results.all()),
                    'currentCategory': None
                })

            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category)
                question.insert()

                all_questions = Question.query.order_by(Question.id).all()
                questions_in_page = paginate_questions(request, all_questions)

                return jsonify({
                    'success': True,
                    'questions': questions_in_page,
                    'total_questions': len(all_questions),
                    'currentCategory': None
                })

        except BaseException:
            abort(422)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrive_questions_by_category(category_id):

        questions_by_category = Question.query.filter(
            Question.category == category_id).all()

        questions_in_page = paginate_questions(request, questions_by_category)

        if len(questions_in_page) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_in_page,
            'total_questions': len(questions_by_category),
            'currentCategory': category_id
        })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.route('/quizzes', methods=['POST'])
    def quizze():

        data = request.get_json()

        previous_questions = data["previous_questions"]
        quiz_category = data["quiz_category"]["id"]

        if quiz_category == 0:
            questions_by_category = Question.query.all()
        else:
            questions_by_category = Question.query.filter(
                Question.category == quiz_category).all()

        next_questions = [Question.format()
                          for Question in questions_by_category]

        if len(next_questions) == 0:
            abort(404)

        try:

            for previous_question in previous_questions:
                for question in next_questions:
                    if question['id'] == previous_question:
                        next_questions.remove(question)
                        break
            if not next_questions:
                return jsonify({
                    'success': True,
                    'question': None,
                })

            currentQuestion = random.choice(next_questions)

            return jsonify({
                'success': True,
                'question': currentQuestion,
            })

        except BaseException:
            abort(422)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Error Handlers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
          'success': False,
          'error': 500,
          'message': 'Internal server error',
        }), 500

    return app

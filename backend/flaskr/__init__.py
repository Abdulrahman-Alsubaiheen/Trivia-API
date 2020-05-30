import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Helper method
def paginate_questions(request , all_questions):

    page = request.args.get('page' , 1 , type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [Question.format() for Question in all_questions]
    questions_in_page = questions[start:end]

    return questions_in_page


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  # CORS(app)
  # cors = CORS(app, resources={r"*/api/*": {"origins": "*"}})
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

 # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories' , methods=['GET'])
  def retrive_categories():
      all_categories = Category.query.order_by(Category.id).all()

      catgs = {cat.id:cat.type for cat in all_categories}
      
      if len(catgs) == 0 :
        abort(404)
    
      return jsonify({
        'success' : True,
        'categories' : catgs,
      })

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

  @app.route('/questions' , methods=['GET'])
  def retrive_questions():

      all_questions = Question.query.order_by(Question.id).all()
      questions_in_page = paginate_questions(request , all_questions)

      if len(questions_in_page) == 0 :
        abort(404)

      all_categories = Category.query.order_by(Category.id).all()
      catgs = {cat.id:cat.type for cat in all_categories}


      return jsonify({
        'success' : True,
        'questions' : questions_in_page,
        'total_questions' : len(all_questions),
        'categories': catgs,
        'currentCategory' : None
      })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
      })

    except:
      abort(422)



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the 
  question, answer, category and difficulty score.

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


  @app.route('/questions', methods=['POST'])
  def create_question():

    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    searchTerm = body.get('searchTerm', None)

    try:

      if searchTerm:

        results = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm)))
        questions_in_page = paginate_questions(request , results)

        return jsonify({
          'success' : True,
          'questions' : questions_in_page,
          'total_questions' : len(results.all()),
          'currentCategory' : None
        })

      else:
        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty , category=new_category)
        question.insert()

        all_questions = Question.query.order_by(Question.id).all()
        questions_in_page = paginate_questions(request, all_questions)

        return jsonify({
          'success' : True,
          'questions' : questions_in_page,
          'total_questions' : len(all_questions),
          'currentCategory' : None
        })

    except:
      abort(422)




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

    
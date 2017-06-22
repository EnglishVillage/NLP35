#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

"""
参考:http://www.cnblogs.com/vovlie/p/4178077.html
"""

from flask import Flask, jsonify, abort, make_response,request

app = Flask(__name__)


# 首页,get请求(页面http://127.0.0.1:5000/或者http://localhost:5000/进行访问)
@app.route("/")
def index():
	return "Hello, World!"


tasks = [{"id": 1, "title": "Buy groceries", "description": "Milk, Cheese, Pizza, Fruit, Tylenol", "done": False},
		 {"id": 2, "title": "Learn Python", "description": "Need to find a good Python tutorial on the web", "done": False}]

# 列表页,get请求
@app.route("/todo/api/v1.0/tasks", methods=["GET"])
# @app.route("/todo/api/keyword", methods=["GET"])
def get_tasks():
	return jsonify({"tasks": tasks})

# 带id详细页,get请求
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	# for task in tasks:
	#	 if task["id"]==task_id:
	#		 return jsonify({'task': task})
	# abort(404)

	result = filter(lambda task: task["id"] == task_id, tasks)
	for task in result:
		return jsonify({'task': task})
	abort(404)

# 404页面
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

# post请求
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	# 这个json不知道怎麽发送
	# if not request.json or not 'title' in request.json:
	# 	abort(400)
	# task = {
	# 	'id': tasks[-1]['id'] + 1,
	# 	'title': request.json['title'],
	# 	'description': request.json.get('description', ""),
	# 	'done': False
	# }
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values)<1:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'title': request.values['title'],
		'description': request.values.get('description', "wkzdescription"),
		'done': False
	}
	tasks.append(task)
	return jsonify({'task': task}), 201


# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
# def update_task(task_id):
# 	task = filter(lambda t: t['id'] == task_id, tasks)
# 	if len(task) == 0:
# 		abort(404)
# 	if not request.json:
# 		abort(400)
# 	if 'title' in request.json and type(request.json['title']) != unicode:
# 		abort(400)
# 	if 'description' in request.json and type(request.json['description']) is not unicode:
# 		abort(400)
# 	if 'done' in request.json and type(request.json['done']) is not bool:
# 		abort(400)
# 	task[0]['title'] = request.json.get('title', task[0]['title'])
# 	task[0]['description'] = request.json.get('description', task[0]['description'])
# 	task[0]['done'] = request.json.get('done', task[0]['done'])
# 	return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = filter(lambda t: t['id'] == task_id, tasks)
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})

if __name__ == "__main__":
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0',port=5000, debug=True)
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子不可访问
	# app.run(host='127.0.0.1',port=25000, debug=True)
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子不可访问
	# app.run(host='localhost',port=25000, debug=True)
	# app.run(debug=True)
	# app.run()


# print(1)

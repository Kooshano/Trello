from flask import request, jsonify
from app import app, db
from models import Workspace, Task, SubTask, User, UserWorkspaceRole
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

# Workspace Routes

@app.route('/workspaces', methods=['GET'])
@jwt_required()
def get_workspaces():
    workspaces = Workspace.query.all()
    return jsonify([workspace.to_dict() for workspace in workspaces])

@app.route('/workspaces', methods=['POST'])
@jwt_required()
def create_workspace():
    data = request.get_json()
    new_workspace = Workspace(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(new_workspace)
    db.session.commit()
    return jsonify(new_workspace.to_dict()), 201

@app.route('/workspaces/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    return jsonify(workspace.to_dict())

@app.route('/workspaces/<int:workspace_id>', methods=['PUT'])
@jwt_required()
def update_workspace(workspace_id):
    data = request.get_json()
    workspace = Workspace.query.get_or_404(workspace_id)
    workspace.name = data['name']
    workspace.description = data.get('description', '')
    db.session.commit()
    return jsonify(workspace.to_dict())

@app.route('/workspaces/<int:workspace_id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    db.session.delete(workspace)
    db.session.commit()
    return '', 204

# Task Routes

@app.route('/workspaces/<int:workspace_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(workspace_id):
    tasks = Task.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/workspaces/<int:workspace_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(workspace_id):
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'Planned'),
        estimated_time=data.get('estimated_time'),
        actual_time=data.get('actual_time'),
        due_date=data.get('due_date'),
        priority=data.get('priority'),
        workspace_id=workspace_id,
        assignee_id=data.get('assignee_id')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route('/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(workspace_id, task_id):
    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()
    return jsonify(task.to_dict())

@app.route('/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(workspace_id, task_id):
    data = request.get_json()
    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()
    task.title = data['title']
    task.description = data.get('description', '')
    task.status = data.get('status', 'Planned')
    task.estimated_time = data.get('estimated_time')
    task.actual_time = data.get('actual_time')
    task.due_date = data.get('due_date')
    task.priority = data.get('priority')
    task.assignee_id = data.get('assignee_id')
    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(workspace_id, task_id):
    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return '', 204

# SubTask Routes

@app.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@jwt_required()
def get_subtasks(task_id):
    subtasks = SubTask.query.filter_by(task_id=task_id).all()
    return jsonify([subtask.to_dict() for subtask in subtasks])

@app.route('/tasks/<int:task_id>/subtasks', methods=['POST'])
@jwt_required()
def create_subtask(task_id):
    data = request.get_json()
    new_subtask = SubTask(
        task_id=task_id,
        title=data['title'],
        is_completed=data.get('is_completed', False),
        assignee_id=data.get('assignee_id')
    )
    db.session.add(new_subtask)
    db.session.commit()
    return jsonify(new_subtask.to_dict()), 201

@app.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['GET'])
@jwt_required()
def get_subtask(task_id, subtask_id):
    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    return jsonify(subtask.to_dict())

@app.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['PUT'])
@jwt_required()
def update_subtask(task_id, subtask_id):
    data = request.get_json()
    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    subtask.title = data['title']
    subtask.is_completed = data.get('is_completed', False)
    subtask.assignee_id = data.get('assignee_id')
    db.session.commit()
    return jsonify(subtask.to_dict())

@app.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(task_id, subtask_id):
    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    db.session.delete(subtask)
    db.session.commit()
    return '', 204

# User Routes

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.username = data['username']
    user.email = data['email']
    user.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# UserWorkspaceRole Routes

@app.route('/workspaces/<int:workspace_id>/users', methods=['GET'])
@jwt_required()
def get_workspace_users(workspace_id):
    roles = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([role.to_dict() for role in roles])

@app.route('/workspaces/<int:workspace_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_workspace(workspace_id):
    data = request.get_json()
    new_role = UserWorkspaceRole(
        user_id=data['user_id'],
        workspace_id=workspace_id,
        role=data['role']
    )
    db.session.add(new_role)
    db.session.commit()
    return jsonify(new_role.to_dict()), 201

@app.route('/workspaces/<int:workspace_id>/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_role(workspace_id, user_id):
    data = request.get_json()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=user_id).first_or_404()
    role.role = data['role']
    db.session.commit()
    return jsonify(role.to_dict())

@app.route('/workspaces/<int:workspace_id>/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_user_from_workspace(workspace_id, user_id):
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=user_id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    return '', 204

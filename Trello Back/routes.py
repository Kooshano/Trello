from datetime import datetime
from flask import request, jsonify
from app import app, db
from models import Workspace, Task, SubTask, User, UserWorkspaceRole
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash




# Helper function to get current user
def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

# Helper function to parse datetime
def parse_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ") if datetime_str else None

# Workspace Routes

@app.route('/workspaces', methods=['GET'])
@jwt_required()
def get_workspaces():
    current_user = get_current_user()
    user_roles = UserWorkspaceRole.query.filter_by(user_id=current_user.id).all()
    workspace_ids = [role.workspace_id for role in user_roles]
    workspaces = Workspace.query.filter(Workspace.id.in_(workspace_ids)).all()
    return jsonify([workspace.to_dict() for workspace in workspaces]), 200

@app.route('/workspaces', methods=['POST'])
@jwt_required()
def create_workspace():
    data = request.get_json()
    current_user = get_current_user()
    new_workspace = Workspace(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(new_workspace)
    db.session.commit()

    # Add the creator as the admin of the workspace
    new_role = UserWorkspaceRole(
        user_id=current_user.id,
        workspace_id=new_workspace.id,
        role='admin'
    )
    db.session.add(new_role)
    db.session.commit()
    return jsonify(new_workspace.to_dict()), 201

@app.route('/workspaces/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace(workspace_id):
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    workspace = Workspace.query.get_or_404(workspace_id)
    return jsonify(workspace.to_dict()), 200

@app.route('/workspaces/<int:workspace_id>', methods=['PUT'])
@jwt_required()
def update_workspace(workspace_id):
    data = request.get_json()
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    if role.role != 'admin':
        return jsonify({"error": "Not authorized"}), 403

    workspace = Workspace.query.get_or_404(workspace_id)
    workspace.name = data['name']
    workspace.description = data.get('description', '')
    db.session.commit()
    return jsonify(workspace.to_dict()), 200

@app.route('/workspaces/<int:workspace_id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(workspace_id):
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    if role.role != 'admin':
        return jsonify({"error": "Not authorized"}), 403

    workspace = Workspace.query.get_or_404(workspace_id)
    db.session.delete(workspace)
    db.session.commit()
    return '', 204

# Task Routes

@app.route('/workspaces/<int:workspace_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(workspace_id):
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    tasks = Task.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/workspaces/<int:workspace_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(workspace_id):
    data = request.get_json()
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()

    due_date = parse_datetime(data.get('due_date'))

    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'Planned'),
        estimated_time=data.get('estimated_time'),
        actual_time=data.get('actual_time'),
        due_date=due_date,
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
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()
    return jsonify(task.to_dict()), 200

@app.route('/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(workspace_id, task_id):
    data = request.get_json()
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()

    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()

    task.title = data['title']
    task.description = data.get('description', '')
    task.status = data.get('status', 'Planned')
    task.estimated_time = data.get('estimated_time')
    task.actual_time = data.get('actual_time')
    task.due_date = parse_datetime(data.get('due_date'))
    task.priority = data.get('priority')
    task.assignee_id = data.get('assignee_id')
    db.session.commit()
    return jsonify(task.to_dict()), 200

@app.route('/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(workspace_id, task_id):
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()

    task = Task.query.filter_by(workspace_id=workspace_id, id=task_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return '', 204

# SubTask Routes

@app.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@jwt_required()
def get_subtasks(task_id):
    current_user = get_current_user()
    task = Task.query.get_or_404(task_id)
    role = UserWorkspaceRole.query.filter_by(workspace_id=task.workspace_id, user_id=current_user.id).first_or_404()

    subtasks = SubTask.query.filter_by(task_id=task_id).all()
    return jsonify([subtask.to_dict() for subtask in subtasks]), 200

@app.route('/tasks/<int:task_id>/subtasks', methods=['POST'])
@jwt_required()
def create_subtask(task_id):
    data = request.get_json()
    current_user = get_current_user()
    task = Task.query.get_or_404(task_id)
    role = UserWorkspaceRole.query.filter_by(workspace_id=task.workspace_id, user_id=current_user.id).first_or_404()

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
    current_user = get_current_user()
    task = Task.query.get_or_404(task_id)
    role = UserWorkspaceRole.query.filter_by(workspace_id=task.workspace_id, user_id=current_user.id).first_or_404()

    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    return jsonify(subtask.to_dict()), 200

@app.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['PUT'])
@jwt_required()
def update_subtask(task_id, subtask_id):
    data = request.get_json()
    current_user = get_current_user()
    task = Task.query.get_or_404(task_id)
    role = UserWorkspaceRole.query.filter_by(workspace_id=task.workspace_id, user_id=current_user.id).first_or_404()

    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    subtask.title = data['title']
    subtask.is_completed = data.get('is_completed', False)
    subtask.assignee_id = data.get('assignee_id')
    db.session.commit()
    return jsonify(subtask.to_dict()), 200

@app.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(task_id, subtask_id):
    current_user = get_current_user()
    task = Task.query.get_or_404(task_id)
    role = UserWorkspaceRole.query.filter_by(workspace_id=task.workspace_id, user_id=current_user.id).first_or_404()

    subtask = SubTask.query.filter_by(task_id=task_id, id=subtask_id).first_or_404()
    db.session.delete(subtask)
    db.session.commit()
    return '', 204

# User Routes

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/users', methods=['POST'])
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
    return jsonify(user.to_dict()), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.username = data['username']
    user.email = data['email']
    user.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(user.to_dict()), 200

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
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()

    roles = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([role.to_dict() for role in roles]), 200

@app.route('/workspaces/<int:workspace_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_workspace(workspace_id):
    data = request.get_json()
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    if role.role != 'admin':
        return jsonify({"error": "Not authorized"}), 403

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
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    if role.role != 'admin':
        return jsonify({"error": "Not authorized"}), 403

    user_role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=user_id).first_or_404()
    user_role.role = data['role']
    db.session.commit()
    return jsonify(user_role.to_dict()), 200

@app.route('/workspaces/<int:workspace_id>/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_user_from_workspace(workspace_id, user_id):
    current_user = get_current_user()
    role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=current_user.id).first_or_404()
    if role.role != 'admin':
        return jsonify({"error": "Not authorized"}), 403

    user_role = UserWorkspaceRole.query.filter_by(workspace_id=workspace_id, user_id=user_id).first_or_404()
    db.session.delete(user_role)
    db.session.commit()
    return '', 204

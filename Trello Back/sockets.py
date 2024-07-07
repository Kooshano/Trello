from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app import socketio, db
from models import Task, Workspace, SubTask, User, UserWorkspaceRole
from datetime import datetime
from flask import request
import json

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        disconnect()
        return
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        print(f'User {user_id} connected')
        emit('response', {'data': 'Connected'})
    except Exception as e:
        print(f'JWT decode error: {e}')
        disconnect()

@socketio.on('message')
def handle_message(msg):
    try:
        data = json.loads(msg)
        print(f'Message: {data}')
        emit('response', {'message': data}, broadcast=True)
    except json.JSONDecodeError:
        print(f'Invalid message format: {msg}')
        emit('response', {'error': 'Invalid message format'}, broadcast=True)

    except ValueError:
        print(f'Invalid message format: {msg}')
        emit('response', {'error': 'Invalid message format'}, broadcast=True)
@socketio.on('create_task')
def handle_create_task(data):
    title = data.get('title')
    description = data.get('description')
    status = data.get('status', 'Planned')
    estimated_time = data.get('estimated_time')
    actual_time = data.get('actual_time')
    due_date = data.get('due_date')
    priority = data.get('priority')
    workspace_id = data.get('workspace_id')
    assignee_id = data.get('assignee_id')

    if not title or not workspace_id:
        emit('task_response', {'message': 'Title and Workspace ID are required'}, broadcast=True)
        return

    new_task = Task(
        title=title,
        description=description,
        status=status,
        estimated_time=estimated_time,
        actual_time=actual_time,
        due_date=due_date,
        priority=priority,
        workspace_id=workspace_id,
        assignee_id=assignee_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(new_task)
    db.session.commit()
    emit('task_response', {'message': 'Task created successfully', 'task': new_task.to_dict()}, broadcast=True)

@socketio.on('update_task')
def handle_update_task(data):
    task_id = data.get('id')
    task = Task.query.get(task_id)

    if not task:
        emit('task_response', {'message': 'Task not found'}, broadcast=True)
        return

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.estimated_time = data.get('estimated_time', task.estimated_time)
    task.actual_time = data.get('actual_time', task.actual_time)
    task.due_date = data.get('due_date', task.due_date)
    task.priority = data.get('priority', task.priority)
    task.assignee_id = data.get('assignee_id', task.assignee_id)
    task.updated_at = datetime.utcnow()

    db.session.commit()
    emit('task_response', {'message': 'Task updated successfully', 'task': task.to_dict()}, broadcast=True)

@socketio.on('delete_task')
def handle_delete_task(data):
    task_id = data.get('id')
    task = Task.query.get(task_id)

    if not task:
        emit('task_response', {'message': 'Task not found'}, broadcast=True)
        return

    db.session.delete(task)
    db.session.commit()
    emit('task_response', {'message': 'Task deleted successfully'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

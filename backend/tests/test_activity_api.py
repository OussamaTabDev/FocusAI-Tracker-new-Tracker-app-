import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask
from app import create_app
from app.services.Activity.WindowTracker import WindowTracker
from app.models.window import WindowInfo
from app.api.Activity.Handlers.handlers import ActivityHandlers


class TestActivityAPI:
    """Test suite for Activity API endpoints using the new Activity structure."""
    
    @pytest.fixture
    def app(self):
        """Create a test Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @pytest.fixture
    def mock_window_info(self):
        """Create a mock WindowInfo object."""
        return WindowInfo(
            id=123,
            title="Test Window",
            process_name="test.exe",
            window_type="application",
            display_title="Test Window"
        )
    
    @pytest.fixture
    def mock_tracker(self):
        """Mock the WindowTracker."""
        with patch('app.api.Activity.Handlers.handlers.WindowTracker') as mock:
            tracker_instance = Mock()
            tracker_instance.tracking = False
            tracker_instance.start_time = None
            tracker_instance.end_time = None
            tracker_instance.interval = 5
            tracker_instance.focus_history = []
            tracker_instance.window_usage_time = {}
            tracker_instance.window_id_to_info = {}
            tracker_instance.get_session_duration.return_value = 120.5
            tracker_instance.get_categorized_usage.return_value = {
                'browser': 300,
                'code_editor': 600
            }
            tracker_instance.get_window_stats_by_type.return_value = {
                'browser': {'count': 2, 'total_usage_seconds': 300},
                'code_editor': {'count': 1, 'total_usage_seconds': 600}
            }
            tracker_instance.get_top_windows.return_value = [
                {'title': 'Window 1', 'usage_seconds': 300, 'app': 'Browser'},
                {'title': 'Window 2', 'usage_seconds': 200, 'app': 'Code Editor'}
            ]
            mock.return_value = tracker_instance
            yield tracker_instance
    
    @pytest.fixture
    def mock_activity_handlers(self, mock_tracker):
        """Mock the ActivityHandlers instance."""
        with patch('app.api.Activity.Routes.routes.activity_handlers') as mock_handlers:
            handlers_instance = Mock()
            handlers_instance.tracker = mock_tracker
            handlers_instance.start_tracking.return_value = ({
                'status': 'success',
                'message': 'Tracking started',
                'interval': 10,
                'start_time': '2023-01-01T00:00:00'
            }, 200)
            handlers_instance.stop_tracking.return_value = ({
                'status': 'success',
                'message': 'Tracking stopped',
                'session_duration_seconds': 120.5,
                'start_time': '2023-01-01T00:00:00',
                'end_time': '2023-01-01T00:02:00'
            }, 200)
            handlers_instance.get_session_info.return_value = ({
                'status': 'success',
                'data': {
                    'is_tracking': True,
                    'current_interval_seconds': 5,
                    'start_time': '2023-01-01T00:00:00',
                    'end_time': None,
                    'session_duration_seconds': 120.5,
                    'total_focus_events': 2,
                    'unique_windows_tracked': 1
                }
            }, 200)
            handlers_instance.get_current_window.return_value = ({
                'status': 'success',
                'data': {
                    'id': 123,
                    'title': 'Test Window',
                    'process_name': 'test.exe'
                },
                'timestamp': '2023-01-01T00:00:00'
            }, 200)
            handlers_instance.get_all_captured_windows.return_value = ({
                'status': 'success',
                'data': [{'id': 1, 'title': 'Test Window'}],
                'count': 1,
                'timestamp': '2023-01-01T00:00:00'
            }, 200)
            handlers_instance.get_focus_history.return_value = ({
                'status': 'success',
                'data': [{'id': 1, 'title': 'Test Window'}] * 10,
                'total_entries': 10
            }, 200)
            handlers_instance.get_usage_summary.return_value = ({
                'status': 'success',
                'summary': {'browser': 300, 'code_editor': 600},
                'window_types_summary': {
                    'browser': {'count': 2, 'total_usage_seconds': 300},
                    'code_editor': {'count': 1, 'total_usage_seconds': 600}
                }
            }, 200)
            handlers_instance.get_top_windows.return_value = ({
                'status': 'success',
                'data': [
                    {'window_info': {'title': 'Window 1'}, 'usage_time_seconds': 300},
                    {'window_info': {'title': 'Window 2'}, 'usage_time_seconds': 200}
                ],
                'total_unique_windows': 2
            }, 200)
            mock_handlers.return_value = handlers_instance
            yield handlers_instance
    
    @pytest.fixture
    def activity_handlers(self, mock_tracker):
        """Create ActivityHandlers instance with mocked tracker."""
        return ActivityHandlers()
    
    def test_start_tracking_success(self, client, mock_activity_handlers):
        """Test successful tracking start."""
        
        response = client.post('/api/activity/start', 
                             json={'interval': 10})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Tracking started'
        assert data['interval'] == 10
    
    def test_start_tracking_already_running(self, client, mock_tracker):
        """Test starting tracking when already running."""
        mock_tracker.tracking = True
        mock_tracker.start_time = datetime.now()
        
        response = client.post('/api/activity/start')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'already running' in data['message']
    
    def test_start_tracking_invalid_interval(self, client):
        """Test starting tracking with invalid interval."""
        response = client.post('/api/activity/start', 
                             json={'interval': -5})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Invalid interval' in data['message']
    
    def test_stop_tracking_success(self, client, mock_tracker):
        """Test successful tracking stop."""
        mock_tracker.tracking = True
        mock_tracker.start_time = datetime.now()
        
        response = client.post('/api/activity/stop')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Tracking stopped'
        assert data['session_duration_seconds'] == 120.5
    
    def test_stop_tracking_not_running(self, client, mock_tracker):
        """Test stopping tracking when not running."""
        mock_tracker.tracking = False
        
        response = client.post('/api/activity/stop')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No active tracking session' in data['message']
    
    def test_get_session_info(self, client, mock_tracker):
        """Test getting session information."""
        mock_tracker.tracking = True
        mock_tracker.start_time = datetime.now()
        mock_tracker.interval = 5
        mock_tracker.focus_history = [Mock(), Mock()]
        mock_tracker.window_id_to_info = {1: Mock()}
        
        response = client.get('/api/activity/session')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['is_tracking'] is True
        assert data['data']['current_interval_seconds'] == 5
        assert data['data']['total_focus_events'] == 2
        assert data['data']['unique_windows_tracked'] == 1
    
    def test_get_current_window_success(self, client, mock_tracker, mock_window_info):
        """Test getting current window successfully."""
        mock_tracker._detect_active_window.return_value = mock_window_info
        
        response = client.get('/api/activity/current-window')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['title'] == 'Test Window'
        assert data['data']['process_name'] == 'test.exe'
    
    def test_get_current_window_not_found(self, client, mock_tracker):
        """Test getting current window when none detected."""
        mock_tracker._detect_active_window.return_value = None
        
        response = client.get('/api/activity/current-window')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Unable to detect active window' in data['message']
    
    def test_get_all_windows(self, client, mock_tracker, mock_window_info):
        """Test getting all captured windows."""
        mock_tracker.window_id_to_info = {1: mock_window_info}
        
        response = client.get('/api/activity/all-captured-windows')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['count'] == 1
        assert len(data['data']) == 1
        assert data['data'][0]['title'] == 'Test Window'
    
    def test_get_focus_history_default_limit(self, client, mock_tracker, mock_window_info):
        """Test getting focus history with default limit."""
        mock_tracker.focus_history = [mock_window_info] * 10
        
        response = client.get('/api/activity/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['total_entries'] == 10
    
    def test_get_focus_history_custom_limit(self, client, mock_tracker, mock_window_info):
        """Test getting focus history with custom limit."""
        mock_tracker.focus_history = [mock_window_info] * 20
        
        response = client.get('/api/activity/history?limit=5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 5
        assert data['total_entries'] == 20
    
    def test_get_focus_history_max_limit(self, client, mock_tracker, mock_window_info):
        """Test getting focus history with max limit exceeded."""
        mock_tracker.focus_history = [mock_window_info] * 2000
        
        response = client.get('/api/activity/history?limit=2000')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 1000  # Should be capped at max limit
    
    def test_get_usage_summary(self, client, mock_tracker):
        """Test getting usage summary."""
        response = client.get('/api/activity/usage')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'browser' in data['summary']
        assert 'browser' in data['window_types_summary']
        assert data['summary']['browser'] == 300
        assert data['summary']['code_editor'] == 600
    
    def test_get_top_windows_default_limit(self, client, mock_tracker):
        """Test getting top windows with default limit."""
        mock_tracker.window_id_to_info = {1: Mock(), 2: Mock()}
        
        response = client.get('/api/activity/top-windows')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 2
        assert data['total_unique_windows'] == 2
        assert data['data'][0]['window_info']['title'] == 'Window 1'
        assert data['data'][0]['usage_time_seconds'] == 300
    
    def test_get_top_windows_custom_limit(self, client, mock_tracker):
        """Test getting top windows with custom limit."""
        mock_tracker.window_id_to_info = {1: Mock(), 2: Mock(), 3: Mock()}
        
        response = client.get('/api/activity/top-windows?limit=2')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 2
    
    def test_get_top_windows_max_limit(self, client, mock_tracker):
        """Test getting top windows with max limit exceeded."""
        mock_tracker.window_id_to_info = {i: Mock() for i in range(30)}
        
        response = client.get('/api/activity/top-windows?limit=30')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 20  # Should be capped at max limit
    
    def test_error_handling_malformed_json(self, client):
        """Test error handling for malformed JSON."""
        response = client.post('/api/activity/start', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_error_handling_server_error(self, client, mock_tracker):
        """Test error handling for server errors."""
        mock_tracker.tracking = False
        mock_tracker.track_window_usage.side_effect = Exception("Test error")
        
        response = client.post('/api/activity/start')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Failed to start tracking' in data['message']
    
    def test_window_info_dataclass(self, mock_window_info):
        """Test WindowInfo dataclass functionality."""
        assert mock_window_info.id == 123
        assert mock_window_info.title == "Test Window"
        assert mock_window_info.process_name == "test.exe"
        assert mock_window_info.window_type == "application"
        assert mock_window_info.display_title == "Test Window"
    
    def test_activity_handlers_initialization(self, mock_tracker):
        """Test ActivityHandlers initialization."""
        handlers = ActivityHandlers()
        assert handlers.tracker is not None
        assert handlers.tracker_thread is None
        assert handlers.tracker_lock is not None


if __name__ == '__main__':
    pytest.main([__file__]) 
# TimerManager Integration Guide

## Overview

The `TimerManager` class provides centralized, safe timer management for the Weather Dashboard application. It replaces direct `after()` and `after_idle()` calls with a more robust system that handles cleanup and prevents memory leaks.

## Key Features

- **Centralized Management**: All timers are managed from a single location
- **Safe Cleanup**: Automatic cleanup on application shutdown
- **Error Handling**: Built-in error handling for timer callbacks
- **Thread Safety**: Safe to use across different components
- **Named Timers**: Easy identification and management of specific timers

## Usage Examples

### Basic Timer Scheduling

```python
# Recurring timer (every 5 seconds)
self.timer_manager.schedule(
    'weather_update',
    5000,  # 5 seconds
    self._update_weather_data,
    start_immediately=True
)

# One-time timer (after 2 seconds)
self.timer_manager.schedule_once(
    'status_clear',
    2000,
    lambda: self.status_label.configure(text="Ready")
)
```

### Timer Management

```python
# Check if timer is running
if self.timer_manager.is_running('weather_update'):
    print("Weather update timer is active")

# Cancel a specific timer
self.timer_manager.cancel('weather_update')

# Shutdown all timers (typically in cleanup)
self.timer_manager.shutdown()
```

## Migration Guide

### Before (Direct after() calls)

```python
class MyComponent(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.scheduled_calls = []
        
    def start_updates(self):
        # Direct after() call
        call_id = self.after(5000, self._update_data)
        self.scheduled_calls.append(call_id)
        
    def cleanup(self):
        # Manual cleanup
        for call_id in self.scheduled_calls:
            try:
                self.after_cancel(call_id)
            except:
                pass
```

### After (TimerManager)

```python
class MyComponent(ctk.CTkFrame):
    def __init__(self, parent, timer_manager):
        super().__init__(parent)
        self.timer_manager = timer_manager
        
    def start_updates(self):
        # Using TimerManager
        self.timer_manager.schedule(
            'data_update',
            5000,
            self._update_data
        )
        
    def cleanup(self):
        # Automatic cleanup through TimerManager
        self.timer_manager.cancel('data_update')
```

## Integration Patterns

### 1. Dashboard Components

For components that inherit from `BaseDashboard`, the `TimerManager` is automatically available:

```python
class MyDashboard(BaseDashboard):
    def __init__(self):
        super().__init__()
        # self.timer_manager is now available
        
    def start_periodic_updates(self):
        self.timer_manager.schedule(
            'periodic_update',
            10000,  # 10 seconds
            self._periodic_update
        )
```

### 2. Standalone Components

For standalone components, pass the `TimerManager` instance:

```python
class StandaloneComponent(ctk.CTkFrame):
    def __init__(self, parent, timer_manager):
        super().__init__(parent)
        self.timer_manager = timer_manager
        
    def setup_auto_refresh(self):
        self.timer_manager.schedule(
            'auto_refresh',
            30000,  # 30 seconds
            self._refresh_content
        )
```

### 3. Service Classes

For service classes that need periodic operations:

```python
class WeatherService:
    def __init__(self, timer_manager):
        self.timer_manager = timer_manager
        
    def start_background_updates(self):
        self.timer_manager.schedule(
            'weather_fetch',
            300000,  # 5 minutes
            self._fetch_weather_data
        )
```

## Best Practices

### 1. Timer Naming

- Use descriptive names: `'weather_update'`, `'status_clear'`, `'auto_refresh'`
- Include component prefix for clarity: `'maps_refresh'`, `'weather_fetch'`
- Avoid generic names: `'timer1'`, `'update'`, `'callback'`

### 2. Error Handling

```python
def _safe_update_callback(self):
    """Timer callback with proper error handling."""
    try:
        # Your update logic here
        self._update_data()
    except Exception as e:
        self.logger.error(f"Update failed: {e}")
        # Optionally reschedule or handle error
```

### 3. Cleanup

```python
def cleanup(self):
    """Component cleanup."""
    # Cancel specific timers
    self.timer_manager.cancel('my_timer')
    
    # Or let the TimerManager handle shutdown automatically
    # when the application closes
```

### 4. Widget Existence Checks

```python
def _update_ui_callback(self):
    """Update UI with existence check."""
    try:
        if self.winfo_exists():
            self._update_display()
        else:
            # Widget destroyed, cancel timer
            self.timer_manager.cancel('ui_update')
    except tk.TclError:
        # Widget destroyed
        self.timer_manager.cancel('ui_update')
```

## Components Already Updated

1. **BaseDashboard**: Core timer management integration
2. **DashboardController**: Status bar timer updates
3. **EnhancedStaticMapsComponent**: Auto-refresh functionality
4. **EnhancedWeatherService**: Thread-safe observer management

## Components Needing Updates

The following components still use direct `after()` calls and should be migrated:

- `ActivitiesTabManager`
- `MapsTabManager` 
- `WeatherTabManager`
- Various UI components with `safe_after()` calls

## Migration Checklist

- [ ] Replace `self.after()` with `timer_manager.schedule_once()`
- [ ] Replace recurring `self.after()` with `timer_manager.schedule()`
- [ ] Remove manual `scheduled_calls` tracking
- [ ] Remove manual `after_cancel()` cleanup
- [ ] Add timer names for easy identification
- [ ] Update component constructors to accept `timer_manager`
- [ ] Test timer cleanup on component destruction

## Troubleshooting

### Timer Not Starting

- Ensure `TimerManager` is properly initialized
- Check that the root window is still valid
- Verify timer name doesn't conflict with existing timer

### Memory Leaks

- Ensure `timer_manager.shutdown()` is called on application exit
- Cancel timers when components are destroyed
- Use `schedule_once()` for one-time operations

### Performance Issues

- Avoid very short intervals (< 100ms)
- Use appropriate intervals for your use case
- Consider batching operations in timer callbacks
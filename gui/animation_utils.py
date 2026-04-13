"""gui/animation_utils.py - Trợ giúp điều khiển nhịp chạy mô phỏng."""

DEFAULT_ANIMATION_DELAY_MS = 5000


def cancel_scheduled_animation(app, keep_as_pending=False):
    after_id = getattr(app, "animation_after_id", None)
    if after_id is not None:
        try:
            app.root.after_cancel(after_id)
        except Exception:
            pass
        app.animation_after_id = None

    scheduled_step = getattr(app, "scheduled_next_step", None)
    app.scheduled_next_step = None

    if keep_as_pending and scheduled_step is not None:
        app.pending_animation_step = scheduled_step


def advance_manual_animation(app):
    next_step = getattr(app, "pending_animation_step", None)
    if next_step is None:
        return

    app.pending_animation_step = None
    next_step()


def schedule_animation_step(app, next_step):
    delay_ms = getattr(app, "animation_delay_ms", DEFAULT_ANIMATION_DELAY_MS)

    if delay_ms is None:
        cancel_scheduled_animation(app, keep_as_pending=False)
        app.pending_animation_step = next_step
        return

    app.pending_animation_step = None
    cancel_scheduled_animation(app, keep_as_pending=False)
    app.scheduled_next_step = next_step

    def run_scheduled_step():
        app.animation_after_id = None
        step = getattr(app, "scheduled_next_step", None)
        app.scheduled_next_step = None
        if step is not None:
            step()

    app.animation_after_id = app.root.after(delay_ms, run_scheduled_step)

from flask import current_app, g

def create_task(f, *args, **kwargs):
    from tenjin.mongo_engine import Database

    rq_enabled = current_app.config["REDIS_QUEUE_ENABLED"]
    job_timeout = 900
    if "job_timeout" in kwargs:
        job_timeout = kwargs.get("job_timeout")
        kwargs.pop("job_timeout")
    if type(rq_enabled) is str:
        if rq_enabled.lower() == "true":
            rq_enabled = True
        else:
            rq_enabled = False
    if rq_enabled:
        # print("RQ execution")
        task_queue = current_app.task_queue
        if hasattr(g, "user"):
            kwargs["__user_id__"] = g.user
        else:
            kwargs["__user_id__"] = None
        kwargs["__disable_access_check__"] = Database.check_for_no_access_check()
        task_queue.enqueue(f, *args, **kwargs, job_timeout=job_timeout)
    else:
        # print("IN execution")
        f(*args, **kwargs)

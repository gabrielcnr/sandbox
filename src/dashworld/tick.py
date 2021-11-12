def tick(component_name: str, out: List[str], notify_callback=print, guard=True):
    """
    Decorator that gives you a better way to create Dash Interval callbacks.

    It monitors if the callback function is taking longer than the ticking/refreshing interval.

    It can also guard against overwhelmingly throtlling the callback if there's a running function already.

    Example of usage:

        app.layout = html.Div([
            html.Label(id="my-label", children="hello"),
            html.Label(id="my-label", children="hello"),
            dcc.Interval(id="my-tick", interval=1000),
            ],
        ])
    
        @tick("my-tick", out=["my-label.children", "another-label.children"])
        def on_every_second(n):
            time.sleep(random.choice([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 2.5, 0.5]))
            return f"tick: {n}", f"{n * 100}"

    """
    if not isinstance(out, list):
        out = [out]

    outputs = [Output(*out_component_property.split(".")) for out_component_property in out]
    inputs = [Input(component_name, "n_intervals")]
    states = [State(component_name, "interval")]

    def decorator(func):
        # Guard/sentinel to prevent throttling
        if guard:
            func._guard = False

        @app.callback(*outputs, *inputs, *states)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(func, "_guard"):
                if func._guard:
                    result = [no_update] * len(outputs)
                    return tuple(*result)
                else:
                    func._guard = True
            # TODO: we should make good usage of inspect module to get function's signature and do this properly
            # But for now let's assume that the only injected extra arguments are the intervals
            # we need to remove extra stuff from here
            *fwd_args, interval = args
            t0 = time.perf_counter()
            try:
                return func(*fwd_args, **kwargs)
            finally:
                if hasattr(func, "_guard"):
                    func._guard = False
                t1 = time.perf_counter()
                elapsed = round((t1 - t0) * 1000, 1)
                if elapsed > interval:
                    notify_callback(f"Callback function is ticking faster than it's taking to complete: "
                                    f"{interval = } ms, {elapsed = } ms")

        return wrapper

    return decorator


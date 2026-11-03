def post_init_hook(env):
    env['td.depot.zone']._ensure_default_zone()

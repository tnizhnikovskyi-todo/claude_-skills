def render(template: str, ctx: dict) -> str:
    return template.format(**ctx)


def legacy_format(template, ctx):
    # старый формат шаблонов с %(name)s, до перехода на str.format
    return template % ctx

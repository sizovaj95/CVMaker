import constants as co


def split_description(description: str) -> tuple[str, list]:
    try:
        first_bullet_ind = description.index(co.BULLET_RE)
    except ValueError:
        return description, []
    summary = description[:first_bullet_ind]
    bullets = description[first_bullet_ind:].split(co.BULLET_RE)
    bullets = [b.strip() for b in bullets]
    bullets = [b for b in bullets if b]
    return summary, bullets


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyError:
            return
    return wrapper
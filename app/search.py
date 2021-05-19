from app import app

def except_field(d, value):
    return {field: d[field] for field in d if field != value}
app.jinja_env.globals.update(except_field=except_field)


def update_techs(args, technology):
    techs = args.get('technology', '')
    tech_list = [' '.join(tech.split()) for tech in techs.split(',') if tech != '']
    technology = ' '.join(technology.split())
    if technology in tech_list:
        return ', '.join([tech for tech in tech_list if technology != tech])
    else:
        return ', '.join(tech_list + [technology])
app.jinja_env.globals.update(update_techs=update_techs)



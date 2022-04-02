from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
from markupsafe import escape

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/my-profile')
@login_required
def profile():
    ask_me_dict = [
    # {
    #     "skill": "Watercolour",
    #     "note": "I do watercolouring for my job. I like to paint landscape and fish",
    #     "level": "Ask me anything! I'm an expert"
    # },
    #     {
    #     "skill": "Python",
    #     "note": "I have been coding for 1 year. I like python because it's cool. ",
    #     "level": "Ask me about my learning journey"
    # },
    #     {
    #     "skill": "Fish",
    #     "note": "Fish keeping has been a passion and hobby of mine since I was a child. We used to go to Qian Hu fish farm a lot to look at the fish.",
    #     "level": "Ask me about my hobby"
    # }
    ]

    tell_me_dict = [{
        "skill": "Chickens",
        "note": "I would love to rear chickens one day. If you have an advice, let's chat",
        "level": "I'm curious about the hobby"
    },
        {
        "skill": "Skydiving",
        "note": "I'm a thrill seeker! Would love to skydive. Anyone care to share about their experiences?  ",
        "level": "I'm looking for an experience"
    },
        {
        "skill": "Yoga",
        "note": "I've been doing yoga for close to 8 years now. I practice around 3 times per week. I'm curious about taking this further and potentially becoming a teacher.",
        "level": "Looking for a potential career switch"
    }]

    nav_items = [
        {"nav_label": "About", 
        "nav_link": "#"},
        {"nav_label": "Messages", 
        "nav_link": "#"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('my_profile.html', nav_items=nav_items, name=current_user.name, ask_me_dict=ask_me_dict, tell_me_dict=tell_me_dict)


@main.route('/edit-profile')
@login_required
def editProfile():
    return (render_template('edit-profile.html'))

from flask import request, flash
from marketing_notifications_python.forms import SendMessageForm
from marketing_notifications_python.models import init_models_module
from marketing_notifications_python.twilio import init_twilio_module
from marketing_notifications_python.view_helpers import twiml, view
from flask import Blueprint
from marketing_notifications_python.twilio.twilio_services import TwilioServices


def construct_view_blueprint(app, db):
    SUBSCRIBE_COMMAND = "Subscribe"
    UNSUBSCRIBE_COMMAND = "Unsubscribe"

    views = Blueprint("views", __name__)

    init_twilio_module(app)
    init_models_module(db)
    from marketing_notifications_python.models.subscriber import Subscriber

    @views.route('/', methods=["GET", "POST"])
    @views.route('/notifications', methods=["GET", "POST"])
    def notifications():
        form = SendMessageForm()
        if request.method == 'POST' and form.validate_on_submit():
            subscribers = Subscriber.query.filter(Subscriber.subscribed).all()
            if len(subscribers) > 0:
                flash('Messages on their way!')
                twilio_services = TwilioServices()
                for s in subscribers:
                    twilio_services.send_message(s.phone_number, form.message.data, form.imageUrl.data)
            else:
                flash('No subscribers found!')

            form.reset()
            return view('notifications', form)

        return view('notifications', form)

    @views.route('/message', methods=["POST"])
    def message():
        subscriber = Subscriber.query.filter(Subscriber.phone_number == request.form['From']).first()
        if subscriber is None:
            subscriber = Subscriber(phone_number=request.form['From'])
            db.session.add(subscriber)
            db.session.commit()
            output = "Thanks for contacting TWBC! Text 'subscribe' if you would like to receive updates via text message."
        elif not subscriber.subscribed:
            output = _process_message(request.form['Body'], subscriber)
            db.session.commit()
        elif subscriber.zipcode is None:
            output = _process_zip(request.form['Body'], subscriber)
            db.session.commit()
        elif subscriber.age is None:
            output = _process_age(request.form['Body'], subscriber)
            db.session.commit()
        elif subscriber.interests is None:
            output = _process_interests(request.form['Body'], subscriber)
            db.session.commit()

        twilio_services = TwilioServices()
        return twiml(twilio_services.respond_message(output))

    def _process_message(message, subscriber):
        output = "Sorry, we don't recognize that command. Available commands are: 'subscribe' or 'unsubscribe'."

        if message.startswith(SUBSCRIBE_COMMAND) or message.startswith(UNSUBSCRIBE_COMMAND):
            subscriber.subscribed = message.startswith(SUBSCRIBE_COMMAND)

            if subscriber.subscribed:
                output = "You are now subscribed for updates. Please respond with your zipcode"
            else:
                output = "You have unsubscribed from notifications. Text 'subscribe' to start receiving updates again"

        return output

    def _process_zip(message, subscriber):
        output = "Sorry, that's an invalid zipcode. Please reenter your zipcode."

        if message[0].isdigit():
            subscriber.zipcode = message
            output = "Thank you. Please respond with your child's age"

        return output

    def _process_age(message, subscriber):
        output = "Sorry, that's an invalid age. Please reenter your child's age."

        if message[0].isdigit():
            subscriber.age = message
            output = "Thank you. Please reply with your child's interests: 1 for Sports, 2 for Art"

        return output

    def _process_interests(message, subscriber):
        output = "Sorry, that's an invalid interest. Please reenter your child's interests: 1 for Sports, 2 for Art"

        if message[0].isdigit():
            subscriber.interests = message
            output = "Thank you. Stay tuned!"

        return output

    return views

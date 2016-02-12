import logging
import queue

from sdk import jwt
from flask import abort
from threading import Thread
from ecdsa.keys import BadSignatureError, BadDigestError

try:
    from urllib2 import unquote
except ImportError:
    from urllib.parse import unquote

from main import beaker_client
from sdk import constants
from sdk import sdk_settings

def get_link_info(link_jwt):
    """
    Gets the info for a given link JWT.
    :param link_jwt: The JWT containing link information.
    :return: A tuple containg the action to perform and link URL.
    """

    try:
        link_jwt = jwt.decode_jwt(link_jwt)
    except (BadSignatureError, BadDigestError):
        logging.exception("Error while attempting to "
                          "decode a link JWT",
                          extra={'link_jwt': link_jwt})

        return constants.ACTION_INVALID, None

    link_id = link_jwt["i"]
    link_url = link_jwt["u"]

    # This line is here for legacy support for old, old links (alpha code, back
    # when it was just internal users + Ben Holland).
    # Once we have real customers, we can remove this, as URLs are
    # unquoted in the message processing stack, before being saved to Beaker.
    link_url = unquote(link_url)

    try:
        link = beaker_client.get_link(link_id)
        link['redirect_url'] = link_url
    except Exception:
        logging.exception("Link could not be retrieved.")
        return constants.ACTION_DEFAULT, link_url

    message_id = link.get('message')

    try:
        message = beaker_client.get_message(message_id)
    except Exception:
        logging.exception("Message could not be retrieved.")
        return constants.ACTION_DEFAULT, link_url

    """
    We need to do two things that both take some time.
    First, we need to check existing rule matches (that is,
    rules that were matched when the message was processed (body / subject).
    Second, we need to check against the current ruleset in
    case an admin has made new rules to respond to a threat.
    So, we kick off two threads, and wait until they both return
    to unblock this thread. Each thread has 3 seconds to report
    back before being terminated.
    """
    thread_queue = queue.Queue()
    check_existing_rule_matches_thread = Thread(target=check_existing_rule_matches,
                                         args=(link, thread_queue))
    check_existing_rule_matches_thread.start()

    check_current_rule_matches_thread = Thread(target=check_current_rule_matches,
                                        args=(link, message, thread_queue))
    check_current_rule_matches_thread.start()

    # Wait for both to return in any order for a max of three seconds
    result_a = None
    result_b = None
    try:
        result_a = thread_queue.get(block=True, timeout=3)
        result_b = thread_queue.get(block=True, timeout=3)
    except queue.Empty:
        logging.error("Could not retrieve rule matches before timeout.")

    action = max(result_a, result_b, constants.ACTION_DEFAULT)

    return action, link_url


def check_existing_rule_matches(link, thread_queue):
    """
    Checks Beaker to see if there are any Rules which
    are already known to match this Link.

    :param link: A dictionary describing the Link object.
    :param thread_queue: The Queue object to use for returning the result cross-thread.
    """

    # If the Link was not known in the DB, just redirect to the
    # URL as specified in the JWT.
    if not link.get('redirect_url'):
        return thread_queue.put(constants.ACTION_DEFAULT)

    rules = link.get('rules')
    final_action = constants.ACTION_DEFAULT

    for rule_id in rules:
        try:
            rule = beaker_client.get_rule(rule_id)
        except Exception:
            logging.exception("Rule could not be retrieved.")
            continue

        action = rule.get('action', constants.ACTION_DEFAULT)
        if action > final_action:
            final_action = action

    thread_queue.put(final_action)

# Click-time
def check_current_rule_matches(link, message, thread_queue):
    """
    Checks Beaker to see if there are any Rules which
    match this Message.

    :param link: A dictionary describing the Link object.
    :param message: A dictionary describing the Message object.
    :param thread_queue: The Queue object to use for returning the result cross-thread.
    """

    message_from_address = message.get('message_from_address')
    envelope_from_address = message.get('envelope_from_address')
    rcpt_to_address = message.get('rcpt_to_address')
    domain_id = message.get('domain')
    domain_name = rcpt_to_address.split("@")[1]
    link_id = link.get('id')
    link_url = link.get('redirect_url')

    # Check the current Rules for the domain and ensure the URL
    # hasn't been listed in a Rule since it was first seen.
    link_rules_dict = beaker_client.check_rules(
        message_from_address=message_from_address,
        domain_id=domain_id,
        domain_name=domain_name,
        link_ids=[link_id],
        senders=[message_from_address, envelope_from_address],
        receivers=[rcpt_to_address], # TODO Probably need to have all the 'To's and 'Cc's in Beaker on the MSG object
        subject=None,
        body=None,
        urls=[link_url]
        )

    final_action = constants.ACTION_DEFAULT

    # If we have matches, we need to notify Beaker and get the associated action to perform.
    for link_id, rule_ids in link_rules_dict.items():
        rule_ids = rule_ids["rule_ids"]
        for rule_id in rule_ids:
            try:
                rule = beaker_client.get_rule(rule_id)
            except Exception:
                logging.exception("Rule could not be retrieved.")
                continue

            action = rule.get('action', constants.ACTION_DEFAULT)
            if action > final_action:
                final_action = action

            beaker_client.mark_link_with_rule(rule_id, link_id)

    thread_queue.put(final_action)

